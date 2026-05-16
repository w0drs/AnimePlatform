CREATE TABLE IF NOT EXISTS anime_comments (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    user_id UUID NOT NULL,
    anime_id INTEGER NOT NULL,
    tagged_user_id UUID,
    is_deleted BOOLEAN DEFAULT FALSE,

    deleted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_anime_comments_anime_deleted ON anime_comments(anime_id, is_deleted, id DESC);
CREATE INDEX IF NOT EXISTS idx_anime_comments_user_id ON anime_comments(user_id) WHERE is_deleted = false;
CREATE INDEX IF NOT EXISTS idx_anime_comments_tagged_user ON anime_comments(tagged_user_id) WHERE is_deleted = false;

CREATE TABLE IF NOT EXISTS news_comments (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    user_id UUID NOT NULL,
    news_id INTEGER NOT NULL,
    tagged_user_id UUID,
    is_deleted BOOLEAN DEFAULT FALSE,

    deleted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_news_comments_news_deleted ON news_comments(news_id, is_deleted, id DESC);
CREATE INDEX IF NOT EXISTS idx_news_comments_user_id ON news_comments(user_id) WHERE is_deleted = false;
CREATE INDEX IF NOT EXISTS idx_news_comments_tagged_user ON news_comments(tagged_user_id) WHERE is_deleted = false;