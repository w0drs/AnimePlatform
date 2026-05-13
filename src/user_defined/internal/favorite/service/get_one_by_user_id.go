package service

import (
	"context"
	"github.com/google/uuid"
	coreHttp "kuronami/internal/core/http"
	corePG "kuronami/internal/core/postgres"
	"kuronami/internal/favorite/domain"
)

func (f *FavoriteService) GetOneByUserID(ctx context.Context, userID uuid.UUID, animeID int) (*domain.Favorite, error) {
	if userID == uuid.Nil {
		f.logger.Error("favorite get, user id is nil")
		return nil, coreHttp.ErrInvalidUserParams
	}

	ctxTimeout, cancel := context.WithTimeout(ctx, corePG.DefaultTimeout)
	defer cancel()

	favorite, err := f.favoritesRepo.GetOneByUserID(ctxTimeout, userID, animeID)
	if err != nil {
		return nil, err
	}

	f.logger.Info("get user favorite", "userId", userID.String())
	return favorite, nil
}
