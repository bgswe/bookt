-- create processed message table
CREATE TABLE account
(
    id               VARCHAR(36) PRIMARY KEY,
    originator_email TEXT NOT NULL
);

CREATE TABLE usr
(
    id          VARCHAR(36) PRIMARY KEY,
    email       TEXT NOT NULL,
    password    TEXT,
    last_login  TIMESTAMP,
    first_name  TEXT,
    last_name   TEXT,

    account_id  VARCHAR(36) NOT NULL
);
