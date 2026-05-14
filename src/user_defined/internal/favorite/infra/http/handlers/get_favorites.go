package handlers

import (
	"errors"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/middleware"
	"kuronami/internal/favorite/domain"
	"kuronami/internal/favorite/infra/http/dto"
	"net/http"
)

func (f *FavoriteHandler) GetFavorites(w http.ResponseWriter, r *http.Request) {
	claims, err := middleware.GetClaimsFromContext(r.Context())
	if err != nil {
		f.logger.Debug("user is unauthorized")
		coreHttp.SendErrorJSON(f.logger, w, &coreHttp.ErrUnauthorized)
		return
	}

	favorites, err := f.favService.GetListByUserID(r.Context(), claims.UserID)
	if err != nil {
		f.logger.Debug("err to get favorite", "user", claims.UserID.String(), "err", err.Error())
		var apiErr coreHttp.APIError
		if errors.As(err, &apiErr) {
			coreHttp.SendErrorJSON(f.logger, w, &apiErr)
			return
		}
		coreHttp.SendErrorJSON(f.logger, w, &coreHttp.ErrInternal)
		return
	}
	if favorites == nil {
		favorites = []*domain.Favorite{}
	}

	coreHttp.SendJSON(f.logger, w, dto.GetFavoritesResp{Favorites: favorites}, http.StatusOK)
	f.logger.Debug("get favorite success", "user", claims.UserID)
	return
}
