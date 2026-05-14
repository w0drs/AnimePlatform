package handlers

import (
	"errors"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/user/domain"
	"kuronami/internal/user/infra/http/dto"
	"net/http"
)

func (a *AuthHandlers) Register(w http.ResponseWriter, r *http.Request) {
	var req dto.RegisterRequest
	if err := coreHttp.ParseJSONBody(a.logger, r, &req); err != nil {
		a.logger.Warn("parse body failed", "err", err.Error())
		coreHttp.SendErrorJSON(a.logger, w, err)
		return
	}

	newUser, err := a.userService.Register(r.Context(), &domain.User{
		Login:       req.Login,
		Email:       req.Email,
		Password:    req.Password,
		Description: req.Description,
		FirstName:   req.FirstName,
		IconUrl:     req.IconURL,
	})
	if err != nil {
		a.logger.Debug("register failed", "err", err.Error())
		var errApi coreHttp.APIError
		if errors.As(err, &errApi) {
			coreHttp.SendErrorJSON(a.logger, w, &errApi)
			return
		}
		coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrInternal)
		return
	}

	coreHttp.SendJSON(a.logger, w, dto.RegisterResponse{
		ID:          newUser.ID.String(),
		Login:       newUser.Login,
		Email:       newUser.Email,
		Description: newUser.Description,
		FirstName:   newUser.FirstName,
		IconUrl:     newUser.IconUrl,
		Role:        newUser.Role,
	}, http.StatusCreated)
	a.logger.Debug("register success", "userID", newUser.ID.String())
}
