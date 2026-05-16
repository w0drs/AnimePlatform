package handlers

import (
	"errors"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/middleware"
	"net/http"
)

func (a *AuthHandlers) DeleteSessions(w http.ResponseWriter, r *http.Request) {
	claims, err := middleware.GetClaimsFromContext(r.Context())
	if err != nil {
		a.logger.Debug("user is unauthorized")
		coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrUnauthorized)
		return
	}

	errD := a.userService.DeleteSessions(r.Context(), claims.UserID)
	if errD != nil {
		a.logger.Debug("delete sessions error", "userID", claims.UserID.String(), "err", errD.Error())
		var apiErr coreHttp.APIError
		if errors.As(errD, &apiErr) {
			coreHttp.SendErrorJSON(a.logger, w, &apiErr)
			return
		}
		coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrInternal)
		return
	}

	w.WriteHeader(http.StatusNoContent)
	a.logger.Debug("delete sessions success", "userID", claims.UserID.String())
}
