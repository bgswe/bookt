CREATE TABLE message_outbox
(
    id        UUID PRIMARY KEY,
    type      TEXT NOT NULL,
    data      JSONB  NOT NULL
);
