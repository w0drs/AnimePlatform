package handlers

import (
	"errors"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/middleware"
	"kuronami/internal/user/domain"
	"kuronami/internal/user/infra/http/dto"
	"net/http"
)

func (a *AuthHandlers) UpdateUser(w http.ResponseWriter, r *http.Request) {
	claims, err := middleware.GetClaimsFromContext(r.Context())
	if err != nil {
		a.logger.Debug("user is unauthorized")
		coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrUnauthorized)
		return
	}

	var req dto.UpdateUserRequest
	if errBody := coreHttp.ParseJSONBody(a.logger, r, &req); errBody != nil {
		a.logger.Warn("invalid body", "error", errBody.Error())
		coreHttp.SendErrorJSON(a.logger, w, errBody)
		return
	}

	_, err = a.userService.Update(r.Context(), &domain.User{
		ID:          claims.UserID,
		Email:       claims.Email,
		Description: req.Description,
		FirstName:   req.FirstName,
		IconUrl:     req.IconUrl,
	})
	if err != nil {
		a.logger.Error("error updating user", "error", err.Error())
		var apiErr coreHttp.APIError
		if errors.As(err, &apiErr) {
			coreHttp.SendErrorJSON(a.logger, w, &apiErr)
			return
		}
		coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrInternal)
		return
	}

	coreHttp.SendJSON(a.logger, w, dto.UpdateUserResponse{
		Message: "user profile updated",
	}, http.StatusOK)
	a.logger.Debug("user updated", "userID", claims.UserID.String())
}
