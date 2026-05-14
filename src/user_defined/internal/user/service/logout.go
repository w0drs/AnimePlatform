package service

import (
	"context"
	"github.com/google/uuid"
)

func (u *UserService) Logout(ctx context.Context, jwtID uuid.UUID) error {
	userId, err := u.tokeRepo.GetUserIDByRefresh(ctx, jwtID)
	if err != nil {
		u.logger.Debug("get user id by refresh failed", "jti", jwtID.String(), "error", err.Error())
		return err
	}

	err = u.tokeRepo.DeleteRefresh(ctx, jwtID)
	if err != nil {
		u.logger.Debug("delete refresh failed", "jti", jwtID.String(), "error", err.Error())
		return err
	}

	err = u.tokeRepo.RemoveUserSession(ctx, *userId, jwtID)
	if err != nil {
		u.logger.Debug("remove user session failed", "jti", jwtID.String(), "error", err.Error())
		return err
	}
	err = u.tokeRepo.DeleteSessionMeta(ctx, jwtID)
	if err != nil {
		u.logger.Debug("delete session meta failed", "jti", jwtID.String(), "error", err.Error())
		return err
	}

	u.logger.Info("logout success", "userID", userId.String())
	return nil
}
