package handlers

import (
	"errors"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/user/infra/http/dto"
	"net/http"
	"os"
)

func (a *AuthHandlers) Refresh(w http.ResponseWriter, r *http.Request) {
	cookie, err := r.Cookie("refresh")
	if err != nil {
		a.logger.Warn("refresh cookie error", "error", err.Error())
		if errors.Is(err, http.ErrNoCookie) {
			coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrUnauthorized)
			return
		}
		coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrInternal)
		return
	}
	refreshToken := cookie.Value

	claims, err := a.jwt.ParseToken(refreshToken)
	if err != nil {
		a.logger.Warn("refresh parse error", "error", err.Error())
		coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrUnauthorized)
		return

	}

	newAccessToken, newRefreshToken, err := a.userService.Refresh(r.Context(), *claims)
	if err != nil {
		a.logger.Warn("refresh error", "error", err.Error())
		var errAPI coreHttp.APIError
		if errors.As(err, &errAPI) {
			coreHttp.SendErrorJSON(a.logger, w, &errAPI)
			return
		}
		coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrUnauthorized)
		return
	}

	http.SetCookie(w, &http.Cookie{
		Name:     "refresh",
		Value:    newRefreshToken,
		Path:     "/auth/refresh",
		HttpOnly: true,
		Secure:   os.Getenv("ENV") == "production",
		SameSite: http.SameSiteStrictMode,
		MaxAge:   7 * 24 * 60 * 60,
	})

	coreHttp.SendJSON(a.logger, w, dto.RefreshResponse{
		Token: newAccessToken,
	}, http.StatusOK)
	a.logger.Debug("refresh success", "userID", claims.UserID.String())
}
