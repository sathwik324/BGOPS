-- =============================================================================
-- NBA Game Outcome Prediction System — MySQL Functions
-- MySQL 8.0+
-- =============================================================================

DELIMITER $$

-- -----------------------------------------------------------------------------
-- 1. calculate_player_score
--    Weighted composite of per-game stats, normalized to 0–10 scale.
-- -----------------------------------------------------------------------------
DROP FUNCTION IF EXISTS calculate_player_score$$

CREATE FUNCTION calculate_player_score(
    p_player_id INT,
    p_season    VARCHAR(10)
)
RETURNS DECIMAL(6,4)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_pts  DECIMAL(5,2) DEFAULT 0;
    DECLARE v_ast  DECIMAL(5,2) DEFAULT 0;
    DECLARE v_reb  DECIMAL(5,2) DEFAULT 0;
    DECLARE v_stl  DECIMAL(5,2) DEFAULT 0;
    DECLARE v_blk  DECIMAL(5,2) DEFAULT 0;
    DECLARE v_raw  DECIMAL(10,4);
    DECLARE v_score DECIMAL(6,4);

    SELECT
        COALESCE(points_per_game, 0),
        COALESCE(assists_per_game, 0),
        COALESCE(rebounds_per_game, 0),
        COALESCE(steals_per_game, 0),
        COALESCE(blocks_per_game, 0)
    INTO v_pts, v_ast, v_reb, v_stl, v_blk
    FROM player_stats
    WHERE player_id = p_player_id
      AND season    = p_season
    LIMIT 1;

    -- Weighted raw score
    SET v_raw = (v_pts * 0.40) + (v_ast * 0.20) + (v_reb * 0.20)
              + (v_stl * 0.10) + (v_blk * 0.10);

    -- Normalize to 0–10 scale (max realistic raw ≈ 30)
    SET v_score = (v_raw / 30.0) * 10.0;

    -- Clamp to [0, 10]
    IF v_score < 0 THEN
        SET v_score = 0;
    ELSEIF v_score > 10 THEN
        SET v_score = 10.0000;
    END IF;

    RETURN v_score;
END$$

-- -----------------------------------------------------------------------------
-- 2. calculate_team_score
--    Sum of player scores (inactive contribute 20%) + win_ratio bonus.
-- -----------------------------------------------------------------------------
DROP FUNCTION IF EXISTS calculate_team_score$$

CREATE FUNCTION calculate_team_score(
    p_team_id INT,
    p_season  VARCHAR(10)
)
RETURNS DECIMAL(8,4)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_total   DECIMAL(10,4) DEFAULT 0;
    DECLARE v_wr      DECIMAL(5,4)  DEFAULT 0;
    DECLARE v_done    INT DEFAULT 0;
    DECLARE v_pid     INT;
    DECLARE v_active  BOOLEAN;
    DECLARE v_pscore  DECIMAL(6,4);

    DECLARE cur CURSOR FOR
        SELECT p.player_id, p.is_active
        FROM players p
        INNER JOIN player_stats ps ON ps.player_id = p.player_id
        WHERE p.team_id = p_team_id
          AND ps.season = p_season;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO v_pid, v_active;
        IF v_done THEN
            LEAVE read_loop;
        END IF;

        SET v_pscore = calculate_player_score(v_pid, p_season);

        IF v_active THEN
            SET v_total = v_total + v_pscore;
        ELSE
            SET v_total = v_total + (v_pscore * 0.20);
        END IF;
    END LOOP;
    CLOSE cur;

    -- Add win_ratio bonus (win_ratio * 5.0)
    SELECT COALESCE(win_ratio, 0)
    INTO v_wr
    FROM teams
    WHERE team_id = p_team_id
    LIMIT 1;

    SET v_total = v_total + (v_wr * 5.0);

    RETURN v_total;
END$$

-- -----------------------------------------------------------------------------
-- 3. get_h2h_advantage
--    Returns team_a win percentage from head_to_head.
-- -----------------------------------------------------------------------------
DROP FUNCTION IF EXISTS get_h2h_advantage$$

CREATE FUNCTION get_h2h_advantage(
    p_team_a INT,
    p_team_b INT,
    p_season VARCHAR(10)
)
RETURNS DECIMAL(5,4)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_lo INT;
    DECLARE v_hi INT;
    DECLARE v_pct DECIMAL(5,4) DEFAULT 0.5000;
    DECLARE v_a_wins INT;
    DECLARE v_b_wins INT;
    DECLARE v_total  INT;

    -- Enforce team_a_id < team_b_id ordering
    IF p_team_a < p_team_b THEN
        SET v_lo = p_team_a;
        SET v_hi = p_team_b;
    ELSE
        SET v_lo = p_team_b;
        SET v_hi = p_team_a;
    END IF;

    SELECT team_a_wins, team_b_wins, total_games
    INTO v_a_wins, v_b_wins, v_total
    FROM head_to_head
    WHERE team_a_id = v_lo
      AND team_b_id = v_hi
      AND season    = p_season
    LIMIT 1;

    -- If no record found, v_total stays NULL from the failed SELECT
    IF v_total IS NULL OR v_total = 0 THEN
        RETURN 0.5000;
    END IF;

    -- Return win pct from the perspective of p_team_a
    IF p_team_a = v_lo THEN
        SET v_pct = v_a_wins / v_total;
    ELSE
        SET v_pct = v_b_wins / v_total;
    END IF;

    RETURN v_pct;
END$$

-- -----------------------------------------------------------------------------
-- 4. predict_win_probability
--    Returns home team win probability.
-- -----------------------------------------------------------------------------
DROP FUNCTION IF EXISTS predict_win_probability$$

CREATE FUNCTION predict_win_probability(
    p_home   INT,
    p_away   INT,
    p_season VARCHAR(10)
)
RETURNS DECIMAL(5,4)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_home_score DECIMAL(8,4);
    DECLARE v_away_score DECIMAL(8,4);
    DECLARE v_h2h        DECIMAL(5,4);
    DECLARE v_score_pct  DECIMAL(5,4);
    DECLARE v_home_adv   DECIMAL(5,4) DEFAULT 0.03;
    DECLARE v_prob       DECIMAL(5,4);

    SET v_home_score = calculate_team_score(p_home, p_season);
    SET v_away_score = calculate_team_score(p_away, p_season);
    SET v_h2h        = get_h2h_advantage(p_home, p_away, p_season);

    -- Score proportion (avoid division by zero)
    IF (v_home_score + v_away_score) = 0 THEN
        SET v_score_pct = 0.5000;
    ELSE
        SET v_score_pct = v_home_score / (v_home_score + v_away_score);
    END IF;

    -- Weighted probability
    SET v_prob = (v_score_pct * 0.60)
              + (v_h2h       * 0.30)
              + (v_home_adv  * 0.10);

    -- Clamp to [0.05, 0.95]
    IF v_prob < 0.05 THEN
        SET v_prob = 0.0500;
    ELSEIF v_prob > 0.95 THEN
        SET v_prob = 0.9500;
    END IF;

    RETURN v_prob;
END$$

DELIMITER ;
