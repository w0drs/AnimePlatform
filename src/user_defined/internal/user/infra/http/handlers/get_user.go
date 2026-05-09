package handlers

import (
	"errors"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/middleware"
	"kuronami/internal/user/infra/http/dto"
	"net/http"
)

func (a *AuthHandlers) GetByLogin(w http.ResponseWriter, r *http.Request) {
	login := r.PathValue("login")

	user, err := a.userService.GetByLogin(r.Context(), login)
	if err != nil {
		var errApi coreHttp.APIError
		if errors.As(err, &errApi) {
			coreHttp.SendErrorJSON(a.logger, w, &errApi)
			return
		}
		coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrInternal)
		return
	}

	coreHttp.SendJSON(a.logger, w, dto.GetUserResponse{
		Login:       user.Login,
		Email:       user.Email,
		Description: user.Description,
		FirstName:   user.FirstName,
		IconUrl:     user.IconUrl,
	}, http.StatusOK)
}

func (a *AuthHandlers) GetMe(w http.ResponseWriter, r *http.Request) {
	claims, err := middleware.GetClaimsFromContext(r.Context())
	if err != nil {
		a.logger.Warn("user is unauthorized")
		coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrUnauthorized)
		return
	}

	user, err := a.userService.GetByEmail(r.Context(), claims.Email)
	if err != nil {
		var errApi coreHttp.APIError
		if errors.As(err, &errApi) {
			coreHttp.SendErrorJSON(a.logger, w, &errApi)
			return
		}
		coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrInternal)
		return
	}

	coreHttp.SendJSON(a.logger, w, dto.GetUserResponse{
		Login:       user.Login,
		Email:       user.Email,
		Description: user.Description,
		FirstName:   user.FirstName,
		IconUrl:     user.IconUrl,
	}, http.StatusOK)
}
