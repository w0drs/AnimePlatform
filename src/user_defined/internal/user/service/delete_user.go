package service

import (
	"context"
	"github.com/google/uuid"
)

func (u *UserService) Deactivate(ctx context.Context, userID uuid.UUID) error {
	err := u.userRepo.Deactivate(ctx, userID)
	if err != nil {
		u.logger.Error("user deactivate error", "id", userID.String(), "err", err.Error())
		return err
	}
	u.logger.Debug("user deactivated", "id", userID.String())
	return nil
}
