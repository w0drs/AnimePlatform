package service

import (
	"context"
	"github.com/google/uuid"
	coreHttp "kuronami/internal/core/http"
)

func (u *UserService) Deactivate(ctx context.Context, userID uuid.UUID) error {
	if userID == uuid.Nil {
		u.logger.Warn("deactivate: user is null")
		return coreHttp.NewValidationError("userID", "userID is nil")
	}

	err := u.userRepo.Deactivate(ctx, userID)
	if err != nil {
		u.logger.Debug("user deactivate failed", "userID", userID.String(), "error", err.Error())
		return err
	}
	u.logger.Info("user deactivated", "userID", userID.String())
	return nil
}
