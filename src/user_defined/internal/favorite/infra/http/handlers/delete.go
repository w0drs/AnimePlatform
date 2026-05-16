package handlers

import (
	"errors"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/middleware"
	"kuronami/internal/favorite/domain"
	"net/http"
	"strconv"
)

func (f *FavoriteHandler) Delete(w http.ResponseWriter, r *http.Request) {
	claims, err := middleware.GetClaimsFromContext(r.Context())
	if err != nil {
		f.logger.Debug("user is unauthorized")
		coreHttp.SendErrorJSON(f.logger, w, &coreHttp.ErrUnauthorized)
		return
	}

	animeID, err := strconv.Atoi(r.PathValue("anime_id"))
	if err != nil {
		f.logger.Warn("anime_id is invalid", "anime_id", r.PathValue("anime_id"))
		validateErr := coreHttp.NewValidationError("anime_id", "invalid anime_id, not int")
		coreHttp.SendErrorJSON(f.logger, w, &validateErr)
		return
	}

	err = f.favService.Delete(r.Context(), domain.Favorite{
		AnimeID: animeID,
		UserID:  claims.UserID,
	})
	if err != nil {
		f.logger.Debug("err to delete favorite", "user", claims.UserID.String(), "animeID", animeID, "err", err.Error())
		var apiErr coreHttp.APIError
		if errors.As(err, &apiErr) {
			coreHttp.SendErrorJSON(f.logger, w, &apiErr)
			return
		}
		coreHttp.SendErrorJSON(f.logger, w, &coreHttp.ErrInternal)
		return
	}

	w.WriteHeader(http.StatusNoContent)
	f.logger.Debug("delete favorite success", "user", claims.UserID)
	return
}
