package service

import (
	"context"
	"github.com/google/uuid"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/security"
	"kuronami/internal/user/domain"
)

func (u *UserService) ChangePass(ctx context.Context, userID uuid.UUID, oldPass, newPass string) error {
	if len(newPass) < domain.UserPasswordMinLength {
		u.logger.Warn("password too short", "user", userID.String())
		return coreHttp.NewValidationError("password", "password length too short")
	}
	if oldPass == newPass {
		u.logger.Warn("password is not different", "user", userID.String())
		return coreHttp.NewValidationError("password", "new password must be different from old password")
	}
	u.logger.Debug("change password", "user", userID.String())

	user, err := u.userRepo.GetByID(ctx, userID)
	if err != nil {
		u.logger.Warn("user err", "err", err.Error(), "user", userID.String())
		return err
	}

	if !security.Verify(user.Password, oldPass) {
		u.logger.Warn("old password is invalid", "user", userID.String())
		return coreHttp.NewErrorWithDetails(coreHttp.ErrUnauthorized, "password", "old password is invalid")
	}

	newPassHashed, err := security.Hash(newPass)
	if err != nil {
		u.logger.Warn("failed to hash new password", "error", err.Error(), "user", userID.String())
		return coreHttp.NewErrorWithDetails(coreHttp.ErrInternal, "hash", err.Error())
	}

	err = u.userRepo.ChangePassword(ctx, userID, newPassHashed)
	if err != nil {
		u.logger.Warn("failed to change password", "error", err.Error(), "user", userID.String())
		return err
	}

	u.logger.Info("change password successful", "user", userID.String())
	return nil
}
