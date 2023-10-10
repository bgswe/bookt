CREATE TABLE message_outbox
(
    id        UUID PRIMARY KEY,
    message   BYTEA  NOT NULL
);
