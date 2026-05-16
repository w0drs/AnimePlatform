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