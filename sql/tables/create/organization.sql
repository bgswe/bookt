CREATE TABLE organization (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,

    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,

    name VARCHAR(255) NOT NULL,
    address VARCHAR(255)
);
