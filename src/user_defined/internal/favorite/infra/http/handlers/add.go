package handlers

import (
	"errors"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/middleware"
	"kuronami/internal/favorite/domain"
	"net/http"
	"strconv"
)

func (f *FavoriteHandler) Add(w http.ResponseWriter, r *http.Request) {
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

	err = f.favService.Add(r.Context(), domain.Favorite{
		AnimeID: animeID,
		UserID:  claims.UserID,
	})
	if err != nil {
		f.logger.Debug("err to add favorite", "user", claims.UserID.String(), "animeID", animeID, "err", err.Error())
		var apiErr coreHttp.APIError
		if errors.As(err, &apiErr) {
			coreHttp.SendErrorJSON(f.logger, w, &apiErr)
			return
		}
		coreHttp.SendErrorJSON(f.logger, w, &coreHttp.ErrInternal)
		return
	}

	coreHttp.SendJSON(f.logger, w, map[string]string{"message": "favorite added successfully"}, http.StatusCreated)
	f.logger.Debug("add favorite success", "user", claims.UserID)
	return
}
