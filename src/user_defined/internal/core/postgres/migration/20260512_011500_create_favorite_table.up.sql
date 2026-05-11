CREATE TABLE favorites (
     id SERIAL PRIMARY KEY,
     user_id UUID NOT NULL,
     anime_id INTEGER NOT NULL,
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     is_deleted BOOLEAN DEFAULT FALSE,
     UNIQUE(user_id, anime_id)
);

CREATE INDEX idx_favorites_user_id ON favorites(user_id) WHERE is_deleted = false;