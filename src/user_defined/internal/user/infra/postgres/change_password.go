package postgres

import (
	"context"
	"errors"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgconn"
	coreHttp "kuronami/internal/core/http"
)

func (r *UserRepo) ChangePassword(ctx context.Context, userID uuid.UUID, newHashed string) error {
	query := `
        UPDATE users 
        SET hashed_password = $2
        WHERE id = $1
    `
	r.logger.Debug("postgres: user changes password", "user", userID.String())

	cmdTag, err := r.pool.Exec(ctx, query, userID, newHashed)
	if err != nil {
		r.logger.Error("error changing password", "user", userID.String(), "error", err.Error())

		var pgErr *pgconn.PgError
		if errors.As(err, &pgErr) {
			if pgErr.Code == "23514" {
				return coreHttp.NewErrorWithDetails(coreHttp.ErrInvalidCredentials, "message", pgErr.Error())
			}
		}
		return coreHttp.NewErrorWithDetails(coreHttp.ErrInternal, "message", err.Error())
	}

	if cmdTag.RowsAffected() == 0 {
		r.logger.Warn("error changing password", "user", userID.String(),
			"error", "no row affected (invalid user or password)")
		return coreHttp.NewErrorWithDetails(coreHttp.ErrInvalidCredentials, "message", "invalid user or password")
	}

	r.logger.Debug("successfully changed password", "user", userID.String())
	return nil
}
