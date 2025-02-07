CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    price TEXT NOT NULL,
    sizes TEXT,
    colors TEXT,
    images TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
