package service

import (
	"context"
	coreHttp "kuronami/internal/core/http"
	corePG "kuronami/internal/core/postgres"
	"kuronami/internal/favorite/domain"

	"github.com/google/uuid"
)

func (f *FavoriteService) Delete(ctx context.Context, favorite domain.Favorite) error {
	if favorite.UserID == uuid.Nil {
		f.logger.Warn("favorite delete, user id is nil")
		return coreHttp.ErrInvalidUserParams
	}

	if favorite.AnimeID <= 0 {
		f.logger.Warn("favorite add failed: invalid anime id", "animeID", favorite.AnimeID)
		return coreHttp.ErrInvalidUserParams
	}

	ctxTimeout, cancel := context.WithTimeout(ctx, corePG.DefaultTimeout)
	defer cancel()

	err := f.favoritesRepo.Delete(ctxTimeout, favorite.UserID, favorite.AnimeID)
	if err != nil {
		f.logger.Debug("delete favorite failed",
			"userID", favorite.UserID, "animeID", favorite.AnimeID, "error", err.Error())
		return err
	}

	f.logger.Info("delete favorite user", "id", favorite.UserID.String())
	return nil
}
