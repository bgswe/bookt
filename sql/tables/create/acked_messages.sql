CREATE TABLE acked_messages
(
    id        UUID PRIMARY KEY,
    type      TEXT NOT NULL,
    data      JSONB  NOT NULL
);
