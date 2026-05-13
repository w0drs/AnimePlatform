package postgres

import (
	"context"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/favorite/domain"

	"github.com/google/uuid"
)

func (f *FavoritePG) GetListByUserID(ctx context.Context, userID uuid.UUID) ([]*domain.Favorite, error) {
	query := `
       SELECT user_id, anime_id 
       from favorites 
       where user_id = $1 and is_deleted = false;
    `

	rows, err := f.pool.Query(ctx, query, userID)
	if err != nil {
		f.logger.Error("postgres get user favorites failed", "err", err.Error())
		return nil, coreHttp.ErrInternal
	}
	defer rows.Close()

	var favorites []*domain.Favorite

	for rows.Next() {
		var favorite domain.Favorite
		if err := rows.Scan(&favorite.UserID, &favorite.AnimeID); err != nil {
			f.logger.Error("postgres get user favorite failed", "err", err.Error())
			return nil, coreHttp.ErrInternal
		}
		favorites = append(favorites, &favorite)
	}

	if err = rows.Err(); err != nil {
		f.logger.Error("postgres rows iteration error", "err", err.Error())
		return nil, coreHttp.ErrInternal
	}

	return favorites, nil
}
