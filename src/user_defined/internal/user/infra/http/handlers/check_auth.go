package handlers

import (
	"errors"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/user/infra/http/dto"
	"net/http"
)

func (a *AuthHandlers) CheckAuth(w http.ResponseWriter, r *http.Request) {
	var req dto.CheckAuthRequest

	if err := coreHttp.ParseJSONBody(a.logger, r, &req); err != nil {
		coreHttp.SendErrorJSON(a.logger, w, err)
		return
	}

	claims, err := a.userService.GetClaims(req.Token)
	if err != nil {
		var apiErr coreHttp.APIError
		if errors.As(err, &apiErr) {
			coreHttp.SendErrorJSON(a.logger, w, &apiErr)
			return
		}
		coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrInternal)
		return
	}

	coreHttp.SendJSON(a.logger, w, dto.CheckAuthResponse{
		UserID: claims.UserID.String(),
		Email:  claims.Email,
		Role:   claims.Role,
	}, http.StatusOK)
}
