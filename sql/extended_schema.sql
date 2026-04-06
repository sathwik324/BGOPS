-- =============================================================================
-- BGOPS — Extended Schema (new tables only)
-- MySQL 8.0+   |   Database: nba_predictions
-- =============================================================================
-- Existing tables NOT touched: teams, players, player_stats, matches, head_to_head

-- -----------------------------------------------------------------------------
-- venues
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS venues (
    venue_id   INT           AUTO_INCREMENT PRIMARY KEY,
    arena_name VARCHAR(150)  NOT NULL,
    capacity   INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- sponsors
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sponsors (
    sponsor_id   INT           AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(150)  NOT NULL,
    industry     VARCHAR(100),
    venue_id     INT,

    CONSTRAINT fk_sponsors_venue
        FOREIGN KEY (venue_id) REFERENCES venues (venue_id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- coaches
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS coaches (
    coach_id    INT           AUTO_INCREMENT PRIMARY KEY,
    coach_name  VARCHAR(150)  NOT NULL,
    career_wins INT           DEFAULT 0,
    team_id     INT,

    CONSTRAINT fk_coaches_team
        FOREIGN KEY (team_id) REFERENCES teams (team_id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- users
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id  INT           AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100)  UNIQUE NOT NULL,
    role     ENUM('admin','analyst','sponsor') DEFAULT 'analyst'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- seasons
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS seasons (
    season_id   INT           AUTO_INCREMENT PRIMARY KEY,
    season_year VARCHAR(10)   NOT NULL,
    start_date  DATE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- awards
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS awards (
    award_id    INT           AUTO_INCREMENT PRIMARY KEY,
    award_title VARCHAR(150)  NOT NULL,
    category    VARCHAR(100),
    player_id   INT,

    CONSTRAINT fk_awards_player
        FOREIGN KEY (player_id) REFERENCES players (player_id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- broadcasters
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS broadcasters (
    broadcaster_id INT           AUTO_INCREMENT PRIMARY KEY,
    network_name   VARCHAR(100)  NOT NULL,
    rights_fee     FLOAT         DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- games
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS games (
    game_id        INT           AUTO_INCREMENT PRIMARY KEY,
    game_date      DATE          NOT NULL,
    match_type     VARCHAR(50),
    attendance     INT           DEFAULT 0,
    venue_id       INT,
    broadcaster_id INT,
    season_id      INT,
    home_team_id   INT,
    away_team_id   INT,
    predicted_by   INT,

    CONSTRAINT fk_games_venue
        FOREIGN KEY (venue_id) REFERENCES venues (venue_id),
    CONSTRAINT fk_games_broadcaster
        FOREIGN KEY (broadcaster_id) REFERENCES broadcasters (broadcaster_id),
    CONSTRAINT fk_games_season
        FOREIGN KEY (season_id) REFERENCES seasons (season_id),
    CONSTRAINT fk_games_home_team
        FOREIGN KEY (home_team_id) REFERENCES teams (team_id),
    CONSTRAINT fk_games_away_team
        FOREIGN KEY (away_team_id) REFERENCES teams (team_id),
    CONSTRAINT fk_games_predicted_by
        FOREIGN KEY (predicted_by) REFERENCES users (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- team_game_stats
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS team_game_stats (
    stat_id  INT  AUTO_INCREMENT PRIMARY KEY,
    team_id  INT  NOT NULL,
    game_id  INT  NOT NULL,
    points   INT  DEFAULT 0,
    rebounds INT  DEFAULT 0,
    assists  INT  DEFAULT 0,

    UNIQUE KEY uq_team_game (team_id, game_id),

    CONSTRAINT fk_tgs_team
        FOREIGN KEY (team_id) REFERENCES teams (team_id),
    CONSTRAINT fk_tgs_game
        FOREIGN KEY (game_id) REFERENCES games (game_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- player_game_stats
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS player_game_stats (
    stat_id        INT  AUTO_INCREMENT PRIMARY KEY,
    player_id      INT  NOT NULL,
    game_id        INT  NOT NULL,
    points         INT  DEFAULT 0,
    rebounds       INT  DEFAULT 0,
    minutes_played INT  DEFAULT 0,

    UNIQUE KEY uq_player_game (player_id, game_id),

    CONSTRAINT fk_pgs_player
        FOREIGN KEY (player_id) REFERENCES players (player_id),
    CONSTRAINT fk_pgs_game
        FOREIGN KEY (game_id) REFERENCES games (game_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- SEED DATA
-- =============================================================================

INSERT IGNORE INTO venues (arena_name, capacity) VALUES
    ('Madison Square Garden', 19812),
    ('Crypto.com Arena', 18997);

INSERT IGNORE INTO sponsors (company_name, industry, venue_id) VALUES
    ('Nike', 'Sportswear', 1),
    ('State Farm', 'Insurance', 2);

INSERT IGNORE INTO users (username, role) VALUES
    ('admin_bgops', 'admin'),
    ('analyst_one', 'analyst');

INSERT IGNORE INTO seasons (season_year, start_date) VALUES
    ('2024-25', '2024-10-22');

INSERT IGNORE INTO broadcasters (network_name, rights_fee) VALUES
    ('ESPN', 2600000000),
    ('TNT', 1200000000);

INSERT IGNORE INTO coaches (coach_name, career_wins, team_id) VALUES
    ('Tom Thibodeau', 434, 1);

INSERT IGNORE INTO awards (award_title, category, player_id) VALUES
    ('Most Valuable Player', 'Regular Season', 1);
