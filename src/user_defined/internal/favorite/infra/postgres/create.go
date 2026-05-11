package postgres

import (
	"context"
	coreHttp "kuronami/internal/core/http"

	"github.com/google/uuid"
)

func (f *FavoritePG) Add(ctx context.Context, userID uuid.UUID, animeID int) error {
	query := `
       INSERT INTO favorites(user_id, anime_id) VALUES ($1, $2)
	   ON CONFLICT DO
       UPDATE SET is_deleted=FALSE WHERE user_id=$1 AND anime_id=$2;
	`
	_, err := f.pool.Exec(ctx, query, userID, animeID, userID)
	if err != nil {
		f.logger.Error("postgres add favorite error", "error", err.Error())
		return coreHttp.ErrInternal
	}
	f.logger.Debug("postgres add favorite success", "userID", userID.String())
	return nil
}
