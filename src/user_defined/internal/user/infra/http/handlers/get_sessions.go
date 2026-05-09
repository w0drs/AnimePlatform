package handlers

import (
	"errors"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/middleware"
	"kuronami/internal/user/infra/http/dto"
	"net/http"
)

func (a *AuthHandlers) GetSessions(w http.ResponseWriter, r *http.Request) {
	claims, err := middleware.GetClaimsFromContext(r.Context())
	if err != nil {
		a.logger.Warn("user is unauthorized")
		coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrUnauthorized)
		return
	}

	sessions, err := a.userService.GetSessions(r.Context(), claims.UserID)
	if err != nil {
		var apiErr coreHttp.APIError
		if errors.As(err, &apiErr) {
			coreHttp.SendErrorJSON(a.logger, w, &apiErr)
			return
		}
		coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrInternal)
		return
	}

	coreHttp.SendJSON(a.logger, w, dto.GetSessionsResponse{
		Sessions: sessions,
	}, http.StatusOK)
}
