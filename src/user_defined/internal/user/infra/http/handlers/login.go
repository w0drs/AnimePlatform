package handlers

import (
	"errors"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/user/infra/http/dto"
	"net/http"
	"os"
)

func (a *AuthHandlers) Login(w http.ResponseWriter, r *http.Request) {
	var req dto.LoginRequest
	if err := coreHttp.ParseJSONBody(a.logger, r, &req); err != nil {
		a.logger.Warn("parse body err", "err", err.Error())
		coreHttp.SendErrorJSON(a.logger, w, err)
		return
	}

	access, refresh, err := a.userService.Login(r.Context(), req.Email, req.Password, req.Remember, ExtractSessionMeta(r))
	if err != nil {
		a.logger.Error("login err", "err", err.Error())
		var apiErr coreHttp.APIError
		if errors.As(err, &apiErr) {
			coreHttp.SendErrorJSON(a.logger, w, &apiErr)
			return
		}
		coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrInternal)
		return
	}

	http.SetCookie(w, &http.Cookie{
		Name:     "refresh",
		Value:    refresh,
		Path:     "/auth/refresh",
		HttpOnly: true,
		Secure:   os.Getenv("ENV") == "production",
		SameSite: http.SameSiteStrictMode,
		MaxAge:   7 * 24 * 60 * 60,
	})

	coreHttp.SendJSON(a.logger, w, dto.LoginResponse{
		Token: access,
	}, http.StatusOK)
	a.logger.Debug("login success", "user email", req.Email)
}
