-- =============================================================================
-- NBA Game Outcome Prediction System — Database Schema
-- MySQL 8.0+
-- =============================================================================

DROP TABLE IF EXISTS head_to_head;
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS player_stats;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS teams;

-- -----------------------------------------------------------------------------
-- teams
-- -----------------------------------------------------------------------------
CREATE TABLE teams (
    team_id        INT           AUTO_INCREMENT PRIMARY KEY,
    nba_team_id    INT           NOT NULL UNIQUE,
    name           VARCHAR(100)  NOT NULL,
    abbreviation   VARCHAR(10)   NOT NULL,
    city           VARCHAR(100)  NOT NULL,
    conference     ENUM('East','West') NOT NULL,
    division       VARCHAR(50)   NOT NULL,
    wins           INT           NOT NULL DEFAULT 0,
    losses         INT           NOT NULL DEFAULT 0,
    win_ratio      DECIMAL(5,4)  GENERATED ALWAYS AS (
                       IF(wins + losses = 0, 0, wins / (wins + losses))
                   ) STORED,
    last_10_wins   INT           NOT NULL DEFAULT 0,
    last_10_losses INT           NOT NULL DEFAULT 0,
    updated_at     TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                 ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_teams_win_ratio (win_ratio DESC),
    INDEX idx_teams_name      (name ASC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- players
-- -----------------------------------------------------------------------------
CREATE TABLE players (
    player_id      INT           AUTO_INCREMENT PRIMARY KEY,
    nba_player_id  INT           NOT NULL UNIQUE,
    team_id        INT           NOT NULL,
    full_name      VARCHAR(150)  NOT NULL,
    position       VARCHAR(20)   NOT NULL DEFAULT '',
    is_active      BOOLEAN       NOT NULL DEFAULT TRUE,
    updated_at     TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                 ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_players_team_id   (team_id),
    INDEX idx_players_is_active (is_active),

    CONSTRAINT fk_players_team
        FOREIGN KEY (team_id) REFERENCES teams (team_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- player_stats
-- -----------------------------------------------------------------------------
CREATE TABLE player_stats (
    stat_id            INT           AUTO_INCREMENT PRIMARY KEY,
    player_id          INT           NOT NULL,
    season             VARCHAR(10)   NOT NULL,
    games_played       INT           NOT NULL DEFAULT 0,
    points_per_game    DECIMAL(5,2)  NOT NULL DEFAULT 0.00,
    assists_per_game   DECIMAL(5,2)  NOT NULL DEFAULT 0.00,
    rebounds_per_game  DECIMAL(5,2)  NOT NULL DEFAULT 0.00,
    steals_per_game    DECIMAL(5,2)  NOT NULL DEFAULT 0.00,
    blocks_per_game    DECIMAL(5,2)  NOT NULL DEFAULT 0.00,
    minutes_per_game   DECIMAL(5,2)  NOT NULL DEFAULT 0.00,
    player_score       DECIMAL(6,4)  NOT NULL DEFAULT 0.0000,
    updated_at         TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                     ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uq_player_season (player_id, season),
    INDEX idx_player_score      (player_score DESC),

    CONSTRAINT fk_stats_player
        FOREIGN KEY (player_id) REFERENCES players (player_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- matches
-- -----------------------------------------------------------------------------
CREATE TABLE matches (
    match_id       INT           AUTO_INCREMENT PRIMARY KEY,
    nba_game_id    VARCHAR(20)   NOT NULL UNIQUE,
    home_team_id   INT           NOT NULL,
    away_team_id   INT           NOT NULL,
    scheduled_date DATE          NOT NULL,
    status         ENUM('scheduled','live','completed') NOT NULL DEFAULT 'scheduled',
    home_score     INT           NULL,
    away_score     INT           NULL,
    winner_team_id INT           NULL,
    season         VARCHAR(10)   NOT NULL,
    updated_at     TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                 ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_matches_scheduled_date (scheduled_date),
    INDEX idx_matches_status         (status),

    CONSTRAINT fk_matches_home
        FOREIGN KEY (home_team_id) REFERENCES teams (team_id),
    CONSTRAINT fk_matches_away
        FOREIGN KEY (away_team_id) REFERENCES teams (team_id),
    CONSTRAINT fk_matches_winner
        FOREIGN KEY (winner_team_id) REFERENCES teams (team_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_different_teams
        CHECK (home_team_id <> away_team_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- head_to_head
-- -----------------------------------------------------------------------------
CREATE TABLE head_to_head (
    h2h_id         INT           AUTO_INCREMENT PRIMARY KEY,
    team_a_id      INT           NOT NULL,
    team_b_id      INT           NOT NULL,
    season         VARCHAR(10)   NOT NULL,
    team_a_wins    INT           NOT NULL DEFAULT 0,
    team_b_wins    INT           NOT NULL DEFAULT 0,
    total_games    INT           GENERATED ALWAYS AS (team_a_wins + team_b_wins) STORED,
    team_a_win_pct DECIMAL(5,4)  GENERATED ALWAYS AS (
                       IF(team_a_wins + team_b_wins = 0, 0.5000,
                          team_a_wins / (team_a_wins + team_b_wins))
                   ) STORED,

    UNIQUE KEY uq_h2h_matchup (team_a_id, team_b_id, season),

    CONSTRAINT fk_h2h_team_a
        FOREIGN KEY (team_a_id) REFERENCES teams (team_id),
    CONSTRAINT fk_h2h_team_b
        FOREIGN KEY (team_b_id) REFERENCES teams (team_id),
    CONSTRAINT chk_team_order
        CHECK (team_a_id < team_b_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
