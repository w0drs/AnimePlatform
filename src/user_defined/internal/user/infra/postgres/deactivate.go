package postgres

import (
	"context"
	"github.com/google/uuid"
	coreHttp "kuronami/internal/core/http"
)

func (r *UserRepo) Deactivate(ctx context.Context, userID uuid.UUID) error {
	query := `
        UPDATE users 
        SET is_active = FALSE
        WHERE id = $1 AND is_active = TRUE
    `

	cmdTag, err := r.pool.Exec(ctx, query, userID)
	if err != nil {
		r.logger.Error("deactivate user error", "user", userID.String(), "error", err.Error())
		return coreHttp.ErrInternal
	}

	if cmdTag.RowsAffected() == 0 {
		return nil
	}

	r.logger.Debug("user deactivated", "user_id", userID.String())
	return nil
}
