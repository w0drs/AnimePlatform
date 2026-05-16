package postgres

import (
	"context"
	"database/sql"
	"errors"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/user/domain"
)

func (r *UserRepo) GetByLogin(ctx context.Context, login string) (*domain.User, error) {
	query := `SELECT id, login, email, description, hashed_password, first_name, icon_url, role
	FROM users WHERE login = $1 and is_active = true`

	var user domain.User

	err := r.pool.QueryRow(ctx, query, login).Scan(
		&user.ID, &user.Login, &user.Email,
		&user.Description, &user.Password,
		&user.FirstName, &user.IconUrl, &user.Role,
	)
	if err != nil {
		r.logger.Error("error getting user by login", "login", login, "error", err.Error())
		if errors.Is(err, sql.ErrNoRows) {
			return nil, coreHttp.ErrUserNotFound
		}
		return nil, coreHttp.ErrInternal
	}
	r.logger.Debug("got user", "user id", user.ID.String())
	return &user, nil
}
