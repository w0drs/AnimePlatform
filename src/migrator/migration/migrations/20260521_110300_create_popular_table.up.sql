CREATE TABLE IF NOT EXISTS popular_anime (
    id SERIAL PRIMARY KEY,
    anime_id INTEGER NOT NULL UNIQUE REFERENCES anime(id) ON DELETE CASCADE,
    large_poster_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индекс для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_popular_anime_anime_id ON popular_anime(anime_id);

CREATE OR REPLACE FUNCTION update_popular_anime_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_popular_anime_timestamp ON popular_anime;
CREATE TRIGGER update_popular_anime_timestamp
    BEFORE UPDATE ON popular_anime
    FOR EACH ROW
    EXECUTE FUNCTION update_popular_anime_updated_at();