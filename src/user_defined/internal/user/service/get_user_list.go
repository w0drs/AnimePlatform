package service

import (
	"context"
	"github.com/google/uuid"
	"kuronami/internal/user/domain"
)

func (u *UserService) GetUserList(ctx context.Context, userIDs []uuid.UUID) ([]domain.User, error) {
	if len(userIDs) == 0 {
		u.logger.Debug("userIDs is empty")
		return []domain.User{}, nil
	}

	users, err := u.userRepo.GetByUserIDList(ctx, userIDs)
	if err != nil {
		u.logger.Debug("get user list failed", "error", err.Error())
		return nil, err
	}
	for i, _ := range users {
		users[i].Password = ""
	}

	u.logger.Info("get user list success", "len users", len(users))
	return users, nil
}
