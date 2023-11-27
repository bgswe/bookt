CREATE TABLE message_outbox
(
    id        VARCHAR(36) PRIMARY KEY,
    message   BYTEA  NOT NULL
);
