package postgres

import (
	"context"
	"errors"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/favorite/domain"
)

func (f *FavoritePG) GetOneByUserID(ctx context.Context, userID uuid.UUID, animeID int) (*domain.Favorite, error) {
	query := `
       SELECT user_id, anime_id 
       from favorites 
       where user_id = $1 and anime_id = $2 and is_deleted = false;
    `
	var favorite domain.Favorite

	err := f.pool.QueryRow(ctx, query, userID, animeID).Scan(&favorite.UserID, &favorite.AnimeID)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return nil, coreHttp.ErrFavoriteNotFound
		}
		f.logger.Error("postgres get user favorite failed", "err", err.Error())
		return nil, coreHttp.ErrInternal
	}
	return &favorite, nil
}
