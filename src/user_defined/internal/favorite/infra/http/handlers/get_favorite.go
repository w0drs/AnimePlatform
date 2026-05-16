package handlers

import (
	"errors"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/middleware"
	"kuronami/internal/favorite/infra/http/dto"
	"net/http"
	"strconv"
)

func (f *FavoriteHandler) GetFavorite(w http.ResponseWriter, r *http.Request) {
	claims, err := middleware.GetClaimsFromContext(r.Context())
	if err != nil {
		f.logger.Debug("user is unauthorized")
		coreHttp.SendErrorJSON(f.logger, w, &coreHttp.ErrUnauthorized)
		return
	}

	animeID, err := strconv.Atoi(r.PathValue("anime_id"))
	if err != nil {
		f.logger.Debug("anime_id is invalid", "anime_id", r.PathValue("anime_id"))
		apiErr := coreHttp.NewValidationError("anime_id", "anime id is invalid")
		coreHttp.SendErrorJSON(f.logger, w, &apiErr)
		return
	}

	favorite, err := f.favService.GetOneByUserID(r.Context(), claims.UserID, animeID)
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
	if favorite == nil {
		coreHttp.SendErrorJSON(f.logger, w, &coreHttp.ErrFavoriteNotFound)
		return
	}

	coreHttp.SendJSON(f.logger, w, dto.GetFavoriteResp{Favorite: *favorite}, http.StatusOK)
	f.logger.Debug("get favorite success", "user", claims.UserID)
	return
}
