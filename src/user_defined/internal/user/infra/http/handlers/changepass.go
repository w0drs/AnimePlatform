package handlers

import (
	"errors"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/middleware"
	"kuronami/internal/user/infra/http/dto"
	"net/http"
)

func (a *AuthHandlers) ChangePass(w http.ResponseWriter, r *http.Request) {
	claims, err := middleware.GetClaimsFromContext(r.Context())
	if err != nil {
		a.logger.Warn("user is unauthorized")
		coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrUnauthorized)
		return
	}
	var req dto.ChangePassRequest
	if errBody := coreHttp.ParseJSONBody(a.logger, r, &req); errBody != nil {
		a.logger.Warn("invalid body", "error", errBody.Error())
		coreHttp.SendErrorJSON(a.logger, w, errBody)
		return
	}

	errChange := a.userService.ChangePass(r.Context(), claims.UserID, req.OldPassword, req.NewPassword)
	if errChange != nil {
		a.logger.Error("error change password", "error", errChange.Error())
		var errApi coreHttp.APIError
		if errors.As(errChange, &errApi) {
			coreHttp.SendErrorJSON(a.logger, w, &errApi)
			return
		}
		coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrInternal)
		return
	}

	coreHttp.SendJSON(a.logger, w, dto.ChangePassResponse{
		Message: "password changed successfully",
	}, http.StatusOK)
	a.logger.Debug("successfully changed password")
}
