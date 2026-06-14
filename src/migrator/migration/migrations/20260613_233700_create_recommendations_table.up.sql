CREATE TABLE IF NOT EXISTS collaborative_recommendations (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    anime_id INTEGER NOT NULL REFERENCES anime(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_collab_recs_user ON collaborative_recommendations(user_id, created_at DESC);
CREATE INDEX idx_collab_recs_anime ON collaborative_recommendations(anime_id);
CREATE INDEX idx_collab_recs_created ON collaborative_recommendations(created_at DESC);