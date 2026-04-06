-- =============================================================================
-- NBA Game Outcome Prediction System — Stored Procedures
-- MySQL 8.0+
-- =============================================================================

DELIMITER $$

-- -----------------------------------------------------------------------------
-- 1. refresh_player_scores
--    Recompute player_score for every player_stats row in a given season.
--    Commits every 100 rows for large datasets.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS refresh_player_scores$$

CREATE PROCEDURE refresh_player_scores(
    IN p_season VARCHAR(10)
)
BEGIN
    DECLARE v_pid     INT;
    DECLARE v_score   DECIMAL(6,4);
    DECLARE v_counter INT DEFAULT 0;
    DECLARE v_done    INT DEFAULT 0;

    DECLARE cur CURSOR FOR
        SELECT player_id
        FROM player_stats
        WHERE season = p_season;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    START TRANSACTION;

    OPEN cur;
    score_loop: LOOP
        FETCH cur INTO v_pid;
        IF v_done THEN
            LEAVE score_loop;
        END IF;

        SET v_score = calculate_player_score(v_pid, p_season);

        UPDATE player_stats
        SET player_score = v_score
        WHERE player_id = v_pid
          AND season     = p_season;

        SET v_counter = v_counter + 1;

        IF v_counter MOD 100 = 0 THEN
            COMMIT;
            START TRANSACTION;
        END IF;
    END LOOP;
    CLOSE cur;

    COMMIT;
END$$

-- -----------------------------------------------------------------------------
-- 2. get_top_players
--    Returns top N active players by player_score for a given season.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS get_top_players$$

CREATE PROCEDURE get_top_players(
    IN p_season VARCHAR(10),
    IN p_limit  INT
)
BEGIN
    SELECT
        p.full_name,
        t.name            AS team_name,
        ps.games_played,
        ps.points_per_game,
        ps.assists_per_game,
        ps.rebounds_per_game,
        ps.steals_per_game,
        ps.blocks_per_game,
        ps.minutes_per_game,
        ps.player_score
    FROM player_stats ps
    INNER JOIN players p ON p.player_id = ps.player_id
    INNER JOIN teams   t ON t.team_id   = p.team_id
    WHERE ps.season  = p_season
      AND p.is_active = TRUE
    ORDER BY ps.player_score DESC
    LIMIT p_limit;
END$$

-- -----------------------------------------------------------------------------
-- 3. get_team_rankings
--    Returns all teams ranked by win_ratio with team_score calculation.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS get_team_rankings$$

CREATE PROCEDURE get_team_rankings(
    IN p_season VARCHAR(10)
)
BEGIN
    SELECT
        t.name,
        t.wins,
        t.losses,
        t.win_ratio,
        t.last_10_wins,
        t.last_10_losses,
        calculate_team_score(t.team_id, p_season) AS team_score
    FROM teams t
    ORDER BY t.win_ratio DESC, t.last_10_wins DESC, t.name ASC;
END$$

-- -----------------------------------------------------------------------------
-- 4. predict_match
--    Predicts outcome between two teams with full context.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS predict_match$$

CREATE PROCEDURE predict_match(
    IN p_home_id INT,
    IN p_away_id INT,
    IN p_season  VARCHAR(10)
)
BEGIN
    DECLARE v_prob DECIMAL(5,4);

    SET v_prob = predict_win_probability(p_home_id, p_away_id, p_season);

    SELECT
        th.name                                          AS home_team,
        ta.name                                          AS away_team,
        ROUND(v_prob * 100, 2)                           AS home_win_pct,
        ROUND((1 - v_prob) * 100, 2)                     AS away_win_pct,
        calculate_team_score(p_home_id, p_season)        AS home_team_score,
        calculate_team_score(p_away_id, p_season)        AS away_team_score,
        get_h2h_advantage(p_home_id, p_away_id, p_season) AS h2h_win_pct
    FROM teams th
    CROSS JOIN teams ta
    WHERE th.team_id = p_home_id
      AND ta.team_id = p_away_id;
END$$

DELIMITER ;
