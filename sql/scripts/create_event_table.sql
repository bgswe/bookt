CREATE TABLE events
(
    id        VARCHAR(36) PRIMARY KEY,
    stream_id VARCHAR(36) NOT NULL,
    stream_type TEXT NOT NULL,
    event_type      TEXT NOT NULL,
    version   BIGINT NOT NULL,
    data      JSONB  NOT NULL,
    UNIQUE (stream_id, version)
);
