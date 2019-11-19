CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE VISIBILITY AS ENUM ('public', 'private');

CREATE TABLE users (
    id            UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name    VARCHAR(50)  NOT NULL,
    last_name     VARCHAR(50)  NOT NULL,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    email         VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    visibility    VISIBILITY   NOT NULL DEFAULT 'public',
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active     BOOLEAN      NOT NULL DEFAULT true
);

CREATE TABLE teams (
    id         UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    name       VARCHAR(50) NOT NULL,
    created_at TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active  BOOLEAN     NOT NULL DEFAULT true
);

CREATE TABLE team_memberships (
    id          UUID      PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    team_id     UUID      NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active   BOOLEAN   NOT NULL DEFAULT true,
    PRIMARY KEY (user_id,team_id)
);

CREATE TABLE boards (
    id         UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    name       VARCHAR(50) NOT NULL,
    created_by UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active  BOOLEAN     NOT NULL DEFAULT true
);

CREATE TABLE board_owners_users (
    board_id   UUID      NOT NULL REFERENCES boards(id) ON DELETE CASCADE,
    user_id    UUID      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active  BOOLEAN   NOT NULL DEFAULT true,
    PRIMARY KEY (board_id,user_id)
);

CREATE TABLE board_owners_teams (
    board_id   UUID      NOT NULL REFERENCES boards(id) ON DELETE CASCADE,
    team_id    UUID      NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active  BOOLEAN   NOT NULL DEFAULT true,
    PRIMARY KEY (board_id,team_id)
);

CREATE TABLE lanes (
    id         UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    board_id   UUID        NOT NULL REFERENCES boards(id) ON DELETE CASCADE,
    name       VARCHAR(50) NOT NULL,
    rank       INTEGER     NOT NULL,
    created_at TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active  BOOLEAN     NOT NULL DEFAULT true
);

CREATE TABLE tasks (
    id          UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    lane_id     UUID        REFERENCES lanes(id) ON DELETE SET NULL,
    board_id    UUID        NOT NULL REFERENCES boards(id) ON DELETE CASCADE,
    title       VARCHAR(50) NOT NULL,
    content     TEXT,
    rank        INTEGER     NOT NULL,
    created_by  UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assigned_to UUID        REFERENCES users(id) ON DELETE SET NULL,
    created_at  TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active   BOOLEAN     NOT NULL DEFAULT true
);
