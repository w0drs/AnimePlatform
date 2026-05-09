package service

import (
	"context"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/security"
	"kuronami/internal/user/domain"
	"time"
)

func (u *UserService) Register(ctx context.Context, user *domain.User) (*domain.User, error) {
	if err := domain.ValidateUser(user); err != nil {
		u.logger.Warn("validate user error", "error", err.Error(), "time", time.Now())
		return nil, err
	}

	hashedPass, err := security.Hash(user.Password)
	if err != nil {
		u.logger.Error("hash password error", "error", err.Error(), "time", time.Now())
		return nil, coreHttp.ErrInternal
	}
	user.Password = hashedPass

	newUser, err := u.userRepo.Create(ctx, user)
	if err != nil {
		u.logger.Error("user create error", "error", err.Error(), "time", time.Now())
		return nil, err
	}

	newUser.Password = ""
	u.logger.Info("user created", "id", newUser.ID, "time", time.Now())
	return newUser, nil
}
