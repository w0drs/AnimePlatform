package service

import (
	"context"
	coreHttp "kuronami/internal/core/http"
	corePG "kuronami/internal/core/postgres"
	"kuronami/internal/favorite/domain"

	"github.com/google/uuid"
)

func (f *FavoriteService) GetByUserID(ctx context.Context, userID uuid.UUID) ([]*domain.Favorite, error) {
	if userID == uuid.Nil {
		f.logger.Error("favorite get, user id is nil")
		return nil, coreHttp.ErrInvalidUserParams
	}

	ctxTimeout, cancel := context.WithTimeout(ctx, corePG.DefaultTimeout)
	defer cancel()

	favorites, err := f.favoritesRepo.GetByUserID(ctxTimeout, userID)
	if err != nil {
		return nil, err
	}

	f.logger.Info("get user favorites", "userId", userID.String())
	return favorites, nil
}
