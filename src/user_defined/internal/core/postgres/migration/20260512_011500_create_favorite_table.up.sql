CREATE TABLE favorites (
     id SERIAL PRIMARY KEY,
     user_id UUID NOT NULL,
     anime_id INTEGER NOT NULL,
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     is_deleted BOOLEAN DEFAULT FALSE,
     UNIQUE(user_id, anime_id)
);
