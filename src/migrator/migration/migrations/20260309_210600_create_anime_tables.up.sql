CREATE TABLE IF NOT EXISTS anime (
    id SERIAL PRIMARY KEY,
    title_english TEXT,
    image_webp_large_url TEXT,
    trailer_url TEXT,
    type TEXT,
    episodes INTEGER,
    duration TEXT,
    rating TEXT,
    synopsis TEXT,
    background TEXT,
    year INTEGER
);

CREATE TABLE IF NOT EXISTS genres (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS themes (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS demographics (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS studios (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS anime_genres (
    anime_id INTEGER REFERENCES anime(id) ON DELETE CASCADE,
    genre_id INTEGER REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (anime_id, genre_id)
);

CREATE TABLE IF NOT EXISTS anime_themes (
    anime_id INTEGER REFERENCES anime(id) ON DELETE CASCADE,
    theme_id INTEGER REFERENCES themes(id) ON DELETE CASCADE,
    PRIMARY KEY (anime_id, theme_id)
);

CREATE TABLE IF NOT EXISTS anime_demographics (
    anime_id INTEGER REFERENCES anime(id) ON DELETE CASCADE,
    demographic_id INTEGER REFERENCES demographics(id) ON DELETE CASCADE,
    PRIMARY KEY (anime_id, demographic_id)
);

CREATE TABLE IF NOT EXISTS anime_studios (
    anime_id INTEGER REFERENCES anime(id) ON DELETE CASCADE,
    studio_id INTEGER REFERENCES studios(id) ON DELETE CASCADE,
    PRIMARY KEY (anime_id, studio_id)
);

-- Индексы для таблицы anime
CREATE INDEX IF NOT EXISTS idx_anime_year ON anime(year);
CREATE INDEX IF NOT EXISTS idx_anime_type ON anime(type);
CREATE INDEX IF NOT EXISTS idx_anime_rating ON anime(rating);
CREATE INDEX IF NOT EXISTS idx_anime_year_type ON anime(year, type);
CREATE INDEX IF NOT EXISTS idx_anime_id ON anime(id);
CREATE INDEX IF NOT EXISTS idx_anime_year_id ON anime(year, id);
CREATE INDEX IF NOT EXISTS idx_anime_type_id ON anime(type, id);
CREATE INDEX IF NOT EXISTS idx_anime_rating_id ON anime(rating, id);

-- Индексы для связующих таблиц
CREATE INDEX IF NOT EXISTS idx_anime_genres_anime_id ON anime_genres(anime_id);
CREATE INDEX IF NOT EXISTS idx_anime_genres_genre_id ON anime_genres(genre_id);
CREATE INDEX IF NOT EXISTS idx_anime_genres_combo ON anime_genres(anime_id, genre_id);

CREATE INDEX IF NOT EXISTS idx_anime_themes_anime_id ON anime_themes(anime_id);
CREATE INDEX IF NOT EXISTS idx_anime_themes_theme_id ON anime_themes(theme_id);
CREATE INDEX IF NOT EXISTS idx_anime_themes_combo ON anime_themes(anime_id, theme_id);

CREATE INDEX IF NOT EXISTS idx_anime_demographics_anime_id ON anime_demographics(anime_id);
CREATE INDEX IF NOT EXISTS idx_anime_demographics_demographic_id ON anime_demographics(demographic_id);
CREATE INDEX IF NOT EXISTS idx_anime_demographics_combo ON anime_demographics(anime_id, demographic_id);

CREATE INDEX IF NOT EXISTS idx_anime_studios_anime_id ON anime_studios(anime_id);
CREATE INDEX IF NOT EXISTS idx_anime_studios_studio_id ON anime_studios(studio_id);
CREATE INDEX IF NOT EXISTS idx_anime_studios_combo ON anime_studios(anime_id, studio_id);

-- Индексы для справочников
CREATE INDEX IF NOT EXISTS idx_genres_name ON genres(name);
CREATE INDEX IF NOT EXISTS idx_themes_name ON themes(name);
CREATE INDEX IF NOT EXISTS idx_demographics_name ON demographics(name);
CREATE INDEX IF NOT EXISTS idx_studios_name ON studios(name);

-- Индексы для подзапросов в json_agg
CREATE INDEX IF NOT EXISTS idx_anime_genres_anime_id_genre_id ON anime_genres(anime_id, genre_id);
CREATE INDEX IF NOT EXISTS idx_anime_themes_anime_id_theme_id ON anime_themes(anime_id, theme_id);
CREATE INDEX IF NOT EXISTS idx_anime_demographics_anime_id_demographic_id ON anime_demographics(anime_id, demographic_id);
CREATE INDEX IF NOT EXISTS idx_anime_studios_anime_id_studio_id ON anime_studios(anime_id, studio_id);
    