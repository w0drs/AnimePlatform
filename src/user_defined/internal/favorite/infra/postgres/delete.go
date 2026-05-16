package postgres

import (
	"context"
	coreHttp "kuronami/internal/core/http"

	"github.com/google/uuid"
)

func (f *FavoritePG) Delete(ctx context.Context, userID uuid.UUID, animeID int) error {
	query := `
      UPDATE favorites 
      SET is_deleted = true 
      where user_id = $1 and anime_id = $2 and is_deleted = false;
    `

	cmd, err := f.pool.Exec(ctx, query, userID, animeID)
	if err != nil {
		f.logger.Error("postgres delete favorites error", "error", err.Error())
		return coreHttp.ErrInternal
	}
	if cmd.RowsAffected() == 0 {
		f.logger.Warn("postgres delete favorites no affected", "user", userID.String())
		return nil
	}

	return nil
}
