CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL UNIQUE,
    descriptions TEXT,  -- Added this column
    variants TEXT,
    price TEXT NOT NULL,
    sizes TEXT,
    colors TEXT,
    images TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
