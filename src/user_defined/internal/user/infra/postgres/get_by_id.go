package postgres

import (
	"context"
	"database/sql"
	"errors"
	"github.com/google/uuid"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/user/domain"
)

func (r *UserRepo) GetByID(ctx context.Context, userID uuid.UUID) (*domain.User, error) {
	query := `SELECT id, login, email, description, hashed_password, first_name, icon_url, role
	FROM users WHERE id = $1 and is_active = true`

	var user domain.User

	err := r.pool.QueryRow(ctx, query, userID).Scan(
		&user.ID, &user.Login, &user.Email,
		&user.Description, &user.Password,
		&user.FirstName, &user.IconUrl, &user.Role,
	)
	if err != nil {
		r.logger.Error("error getting user by ID", "error", err.Error())
		if errors.Is(err, sql.ErrNoRows) {
			return nil, coreHttp.ErrUserNotFound
		}
		return nil, coreHttp.ErrInternal
	}
	r.logger.Debug("got user", "user id", user.ID.String())
	return &user, nil
}
