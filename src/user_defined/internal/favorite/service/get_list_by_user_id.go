package service

import (
	"context"
	coreHttp "kuronami/internal/core/http"
	corePG "kuronami/internal/core/postgres"
	"kuronami/internal/favorite/domain"

	"github.com/google/uuid"
)

func (f *FavoriteService) GetListByUserID(ctx context.Context, userID uuid.UUID) ([]*domain.Favorite, error) {
	if userID == uuid.Nil {
		f.logger.Warn("favorite get, user id is nil")
		return nil, coreHttp.ErrInvalidUserParams
	}

	ctxTimeout, cancel := context.WithTimeout(ctx, corePG.DefaultTimeout)
	defer cancel()

	favorites, err := f.favoritesRepo.GetListByUserID(ctxTimeout, userID)
	if err != nil {
		f.logger.Debug("get favorite failed", "userID", userID.String(), "error", err.Error())
		return nil, err
	}

	f.logger.Debug("get user favorites", "userId", userID.String())
	return favorites, nil
}
