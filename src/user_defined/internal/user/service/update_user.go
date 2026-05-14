package service

import (
	"context"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/user/domain"
	"net/url"
)

func (u *UserService) Update(ctx context.Context, user *domain.User) (*domain.User, error) {
	if len(user.FirstName) < domain.UsernameMinLength {
		u.logger.Warn("firstName too short", "firstName", user.FirstName)
		return nil, coreHttp.NewValidationError("first name", "first name is too short")
	}
	if len(user.FirstName) > domain.UsernameMaxLength {
		u.logger.Warn("firstName too long", "firstName", user.FirstName)
		return nil, coreHttp.NewValidationError("first name", "first name is too long")
	}
	if len(user.Description) > domain.UserDescriptionMaxLength {
		u.logger.Warn("description too long", "description", user.Description)
		return nil, coreHttp.NewValidationError("description", "description is too long")
	}
	if _, err := url.Parse(user.IconUrl); err != nil || user.IconUrl == "" {
		u.logger.Warn("iconUrl invalid", "iconUrl", user.IconUrl)
		return nil, coreHttp.NewValidationError("icon_url", "icon_url is invalid")
	}

	updatedUser, err := u.userRepo.Update(ctx, user)
	if err != nil {
		u.logger.Debug("update user error", "error", err.Error())
		return nil, err
	}

	u.logger.Info("update user success", "updatedUserID", updatedUser.ID.String())
	return updatedUser, nil
}
