package service

import (
	"context"
	"github.com/google/uuid"
)

func (u *UserService) Logout(ctx context.Context, jwtID uuid.UUID) error {
	userId, err := u.tokeRepo.GetUserIDByRefresh(ctx, jwtID)
	if err != nil {
		u.logger.Error("error getting jwtID", "err", err.Error())
		return err
	}

	err = u.tokeRepo.DeleteRefresh(ctx, jwtID)
	if err != nil {
		u.logger.Error("error deleting refresh", "err", err.Error())
		return err
	}

	err = u.tokeRepo.RemoveUserSession(ctx, *userId, jwtID)
	if err != nil {
		u.logger.Error("error removing user session", "err", err.Error())
		return err
	}
	err = u.tokeRepo.DeleteSessionMeta(ctx, jwtID)
	if err != nil {
		u.logger.Error("error deleting session meta", "err", err.Error())
		return err
	}

	u.logger.Info("logout success", "userID", userId.String())
	return nil
}
