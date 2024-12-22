-- create processed message table
CREATE TABLE processed_messages
(
    id        VARCHAR(36) PRIMARY KEY
);

-- create message outbox table
CREATE TABLE message_outbox
(
    id        VARCHAR(36) PRIMARY KEY,
    message   BYTEA NOT NULL
);

-- create event table
CREATE TABLE events
(
    id        VARCHAR(36) PRIMARY KEY,
    stream_id VARCHAR(36) NOT NULL,
    data      JSONB NOT NULL
);
