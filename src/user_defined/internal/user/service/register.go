package service

import (
	"context"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/security"
	"kuronami/internal/user/domain"
)

func (u *UserService) Register(ctx context.Context, user *domain.User) (*domain.User, error) {
	if err := domain.ValidateUser(user); err != nil {
		u.logger.Debug("validate user error", "userID", user.ID.String(), "error", err.Error())
		return nil, err
	}

	hashedPass, err := security.Hash(user.Password)
	if err != nil {
		u.logger.Error("hash password error", "error", err.Error())
		return nil, coreHttp.ErrInternal
	}
	user.Password = hashedPass

	newUser, err := u.userRepo.Create(ctx, user)
	if err != nil {
		u.logger.Debug("user create error", "error", err.Error())
		return nil, err
	}

	newUser.Password = ""
	u.logger.Info("user created", "user id", newUser.ID.String())
	return newUser, nil
}
