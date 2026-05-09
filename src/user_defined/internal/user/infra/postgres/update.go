package postgres

import (
	"context"
	"errors"
	"github.com/jackc/pgx/v5/pgconn"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/user/domain"
)

func (r *UserRepo) Update(ctx context.Context, user *domain.User) (*domain.User, error) {
	query := `
        UPDATE users 
        SET description = $2, first_name = $3, icon_url = $4
        WHERE id = $1
    `

	cmdTag, err := r.pool.Exec(ctx, query, user.ID, user.Description, user.FirstName, user.IconUrl)
	if err != nil {
		var pgErr *pgconn.PgError
		if errors.As(err, &pgErr) {
			if pgErr.Code == "23514" {
				r.logger.Error("user constraint error", "error", err.Error())
				return nil, coreHttp.ErrInvalidUserParams
			}
		}
		r.logger.Error("user internal error", "error", err.Error())
		return nil, coreHttp.ErrInternal
	}

	if cmdTag.RowsAffected() == 0 {
		r.logger.Error("user not found", "id", user.ID)
		return nil, coreHttp.ErrUserNotFound
	}

	r.logger.Debug("user updated", "id", user.ID)
	return user, nil
}
