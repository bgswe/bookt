-- create processed message table
CREATE TABLE tenant
(
    id VARCHAR(36) PRIMARY KEY,
    name TEXT NOT NULL,
);

CREATE TABLE usr
(
    id          VARCHAR(36) PRIMARY KEY,
    email       TEXT NOT NULL,
    hash        TEXT,
    last_login  TIMESTAMP,
    first_name  TEXT,
    last_name   TEXT,

    tenant_id  VARCHAR(36) NOT NULL
);
