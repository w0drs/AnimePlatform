CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    login VARCHAR(128) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    description VARCHAR(512) DEFAULT '',
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(128) DEFAULT 'Anonim',
    icon_url VARCHAR(255) DEFAULT '',
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_login_length CHECK (LENGTH(login) >= 4),
    CONSTRAINT valid_hashed_password CHECK (LENGTH(hashed_password) >= 60)
);

CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC);

CREATE UNIQUE INDEX IF NOT EXISTS unique_active_email ON users(email) WHERE is_active = TRUE;
CREATE UNIQUE INDEX IF NOT EXISTS unique_active_login ON users(login) WHERE is_active = TRUE;


CREATE OR REPLACE FUNCTION prevent_user_deletion()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.is_active = TRUE THEN
       RAISE EXCEPTION 'cannot delete active account %', OLD.login
       USING ERRCODE = '42501';
END IF;
    IF OLD.role = 'admin' THEN
       RAISE EXCEPTION 'cannot delete admin user %', OLD.login
       USING ERRCODE = '42501';
END IF;
RETURN OLD;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS protect_user ON users;
CREATE TRIGGER protect_user
    BEFORE DELETE ON users
    FOR EACH ROW
    EXECUTE FUNCTION prevent_user_deletion();

CREATE OR REPLACE FUNCTION update_user_row()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.role <> 'admin' and NEW.role = 'admin' THEN
       RAISE EXCEPTION 'cannot upgrade account to admin ' USING ERRCODE = '42501';
END IF;
    IF OLD.role = 'admin' and NEW.role <> 'admin' THEN
       RAISE EXCEPTION 'cannot demote admin' USING ERRCODE = '42501';
END IF;
    IF OLD.role = 'admin' and NEW.is_active = FALSE THEN
        RAISE EXCEPTION 'cannot deactivate admin' USING ERRCODE = '42501';
END IF;

    NEW.updated_at = CURRENT_TIMESTAMP;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_user ON users;
CREATE TRIGGER update_user
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_user_row();

CREATE OR REPLACE FUNCTION prevent_create_user()
RETURNS TRIGGER AS $$
BEGIN
    NEW.is_active = TRUE;
    IF NEW.role IS NULL or NEW.role = '' or NEW.role = ' ' THEN
        NEW.role = 'user';
END IF;
    IF NEW.role NOT IN ('user', 'moder', 'admin') THEN
        RAISE EXCEPTION 'role is invalid' USING ERRCODE = '23514';
end if;

RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS check_user_before_create ON users;
CREATE TRIGGER check_user_before_create
    BEFORE INSERT ON users
    FOR EACH ROW
    EXECUTE FUNCTION prevent_create_user();