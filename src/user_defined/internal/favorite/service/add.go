package service

import (
	"context"
	coreHttp "kuronami/internal/core/http"
	corePG "kuronami/internal/core/postgres"
	"kuronami/internal/favorite/domain"

	"github.com/google/uuid"
)

func (f *FavoriteService) Add(ctx context.Context, favorite domain.Favorite) error {
	if favorite.UserID == uuid.Nil {
		f.logger.Error("favorite add, user id is nil")
		return coreHttp.ErrInvalidUserParams
	}

	ctxTimeout, cancel := context.WithTimeout(ctx, corePG.DefaultTimeout)
	defer cancel()

	err := f.favoritesRepo.Add(ctxTimeout, favorite.UserID, favorite.AnimeID)
	if err != nil {
		f.logger.Error("add favorite user error", "error", err.Error())
		return err
	}

	f.logger.Info("add favorite user", "id", favorite.UserID.String())
	return nil
}
