CREATE TABLE organization (
    id uuid PRIMARY KEY,

    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,

    name VARCHAR(255) NOT NULL
);
