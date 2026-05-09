package service

import (
	"context"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/user/domain"
	"net/url"
)

func (u *UserService) Update(ctx context.Context, user *domain.User) (*domain.User, error) {
	if len(user.FirstName) < domain.UsernameMinLength {
		return nil, coreHttp.NewValidationError("first name", "first name is too short")
	}
	if len(user.FirstName) > domain.UsernameMaxLength {
		return nil, coreHttp.NewValidationError("first name", "first name is too long")
	}
	if len(user.Description) > domain.UserDescriptionMaxLength {
		return nil, coreHttp.NewValidationError("description", "description is too long")
	}
	if _, err := url.Parse(user.IconUrl); err != nil {
		return nil, coreHttp.NewValidationError("icon_url", "icon_url is invalid")
	}

	updatedUser, err := u.userRepo.Update(ctx, user)
	if err != nil {
		return nil, err
	}

	return updatedUser, nil
}
