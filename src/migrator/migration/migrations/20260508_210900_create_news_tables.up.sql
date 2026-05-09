CREATE TABLE IF NOT EXISTS news_preview (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    preview_text TEXT NOT NULL,
    preview_image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_published BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS news_content (
    id SERIAL PRIMARY KEY,
    news_id INTEGER UNIQUE REFERENCES news_preview(id) ON DELETE CASCADE,
    full_content TEXT NOT NULL,
    full_image_url TEXT
);

CREATE INDEX IF NOT EXISTS idx_news_preview_created_at ON news_preview(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_news_preview_published ON news_preview(is_published, created_at DESC);