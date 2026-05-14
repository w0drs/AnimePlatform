package postgres

import (
	"context"
	"errors"
	"github.com/jackc/pgx/v5/pgconn"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/user/domain"
)

func (r *UserRepo) Create(ctx context.Context, user *domain.User) (*domain.User, error) {
	query := `
		INSERT INTO users (login, email, hashed_password, first_name, description, icon_url, role)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
		RETURNING id
	`
	r.logger.Debug("userRepo.Create", "user", user.ID.String())
	err := r.pool.QueryRow(ctx, query, user.Login, user.Email, user.Password, user.FirstName, user.Description,
		user.IconUrl, user.Role).Scan(&user.ID)
	if err != nil {
		var errPG *pgconn.PgError
		if errors.As(err, &errPG) {
			if errPG.Code == "23505" {
				r.logger.Error("user already exists", "postgres err", err.Error())
				return nil, coreHttp.ErrUserAlreadyExists
			}
			if errPG.Code == "23514" {
				r.logger.Error("user constraint error", "postgres err", err.Error())
				return nil, coreHttp.ErrInvalidUserParams
			}
		}
		r.logger.Error("user internal error", "postgres err", err.Error())
		return nil, coreHttp.ErrInternal
	}

	r.logger.Debug("user created", "id", user.ID.String())
	return user, nil
}
