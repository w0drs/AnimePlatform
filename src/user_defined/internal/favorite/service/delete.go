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
		f.logger.Error("favorite delete, user id is nil")
		return coreHttp.ErrInvalidUserParams
	}

	ctxTimeout, cancel := context.WithTimeout(ctx, corePG.DefaultTimeout)
	defer cancel()

	err := f.favoritesRepo.Delete(ctxTimeout, favorite.UserID, favorite.AnimeID)
	if err != nil {
		f.logger.Error("delete favorite user error", "error", err.Error())
		return err
	}

	f.logger.Info("delete favorite user", "id", favorite.UserID.String())
	return nil
}
