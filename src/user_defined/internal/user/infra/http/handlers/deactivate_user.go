package handlers

import (
	"errors"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/middleware"
	"kuronami/internal/user/infra/http/dto"
	"net/http"
)

func (a *AuthHandlers) DeactivateUser(w http.ResponseWriter, r *http.Request) {
	claims, err := middleware.GetClaimsFromContext(r.Context())
	if err != nil {
		a.logger.Warn("user is unauthorized")
		coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrUnauthorized)
		return
	}

	errD := a.userService.Deactivate(r.Context(), claims.UserID)
	if errD != nil {
		var apiErr coreHttp.APIError
		if errors.As(errD, &apiErr) {
			coreHttp.SendErrorJSON(a.logger, w, &apiErr)
			return
		}
		coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrInternal)
		return
	}

	coreHttp.SendJSON(a.logger, w, dto.DeactivateUserResponse{
		Message: "user profile deactivated",
	}, http.StatusNoContent)
}
