package service

import (
	"context"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/user/domain"
	"net/mail"
)

func (u *UserService) GetByLogin(ctx context.Context, login string) (*domain.User, error) {
	if len(login) < domain.UsernameMinLength {
		return nil, coreHttp.NewValidationError("username", "username too short")
	}
	if len(login) > domain.UsernameMaxLength {
		return nil, coreHttp.NewValidationError("username", "username too long")
	}

	user, err := u.userRepo.GetByLogin(ctx, login)
	if err != nil {
		return nil, err
	}
	return user, nil
}

func (u *UserService) GetByEmail(ctx context.Context, email string) (*domain.User, error) {
	_, err := mail.ParseAddress(email)
	if err != nil {
		return nil, coreHttp.NewValidationError("email", "invalid email")
	}

	user, err := u.userRepo.GetByEmail(ctx, email)
	if err != nil {
		return nil, err
	}
	return user, nil
}
