CREATE TABLE events
(
    id        UUID PRIMARY KEY,
    stream_id UUID NOT NULL,
    stream_type TEXT NOT NULL,
    event_type      TEXT NOT NULL,
    version   BIGINT NOT NULL,
    data      JSONB  NOT NULL,
    UNIQUE (stream_id, version)
);
