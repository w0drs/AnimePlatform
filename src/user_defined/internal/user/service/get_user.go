package service

import (
	"context"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/user/domain"
	"net/mail"
)

func (u *UserService) GetByLogin(ctx context.Context, login string) (*domain.User, error) {
	if len(login) < domain.UsernameMinLength {
		u.logger.Warn("user name too short", "login", login)
		return nil, coreHttp.NewValidationError("username", "username too short")
	}
	if len(login) > domain.UsernameMaxLength {
		u.logger.Warn("user name too long", "login", login)
		return nil, coreHttp.NewValidationError("username", "username too long")
	}

	user, err := u.userRepo.GetByLogin(ctx, login)
	if err != nil {
		u.logger.Debug("get user error", "login", login)
		return nil, err
	}

	u.logger.Debug("get user", "login", login)
	return user, nil
}

func (u *UserService) GetByEmail(ctx context.Context, email string) (*domain.User, error) {
	_, err := mail.ParseAddress(email)
	if err != nil {
		u.logger.Warn("error parse email", "email", email)
		return nil, coreHttp.NewValidationError("email", "invalid email")
	}

	user, err := u.userRepo.GetByEmail(ctx, email)
	if err != nil {
		u.logger.Debug("get user error", "email", email)
		return nil, err
	}
	u.logger.Debug("get user", "email", email)
	return user, nil
}
