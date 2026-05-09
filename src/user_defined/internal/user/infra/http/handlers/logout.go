package handlers

import (
	"errors"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/middleware"
	"kuronami/internal/user/infra/http/dto"
	"net/http"
)

func (a *AuthHandlers) Logout(w http.ResponseWriter, r *http.Request) {
	claims, err := middleware.GetClaimsFromContext(r.Context())
	if err != nil {
		a.logger.Warn("user is unauthorized")
		coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrUnauthorized)
		return
	}

	errL := a.userService.Logout(r.Context(), claims.JwtID)
	if errL != nil {
		a.logger.Error("logout error", "err", errL.Error())
		var apiErr coreHttp.APIError
		if errors.As(errL, &apiErr) {
			coreHttp.SendErrorJSON(a.logger, w, &apiErr)
			return
		}
		coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrInternal)
		return
	}

	coreHttp.SendJSON(a.logger, w, dto.LogoutResponse{
		Message: "logged out",
	}, http.StatusOK)
	a.logger.Debug("logout success", "userID", claims.UserID.String())
}
