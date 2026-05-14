package postgres

import (
	"context"
	coreHttp "kuronami/internal/core/http"

	"github.com/google/uuid"
)

func (f *FavoritePG) Add(ctx context.Context, userID uuid.UUID, animeID int) error {
	query := `
       INSERT INTO favorites(user_id, anime_id, is_deleted) VALUES ($1, $2, false)
	   ON CONFLICT (user_id, anime_id)
       DO UPDATE SET is_deleted = false;
	`

	_, err := f.pool.Exec(ctx, query, userID, animeID)
	if err != nil {
		f.logger.Error("postgres add favorite error", "error", err.Error())
		return coreHttp.ErrInternal
	}

	return nil
}
