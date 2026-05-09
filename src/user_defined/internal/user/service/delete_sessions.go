package service

import (
	"context"
	"github.com/google/uuid"
)

func (u *UserService) DeleteSessions(ctx context.Context, userId uuid.UUID) error {
	sessions, err := u.tokeRepo.GetUserSessions(ctx, userId)
	if err != nil {
		u.logger.Error("getUserSessions error", "err", err.Error(), "userId", userId.String())
		return err
	}

	if len(sessions) == 0 {
		u.logger.Debug("no sessions to clean", "userId", userId.String())
		return nil
	}

	err = u.tokeRepo.RemoveAllUserSessions(ctx, userId)
	if err != nil {
		u.logger.Error("removeAllUserSessions error", "err", err.Error(), "userId", userId.String())
		return err
	}

	for _, session := range sessions {
		err = u.tokeRepo.DeleteSessionMeta(ctx, session)
		if err != nil {
			u.logger.Error("deleteSessionMeta error", "err", err.Error(), "userId", userId.String())
			continue
		}
		err = u.tokeRepo.DeleteRefresh(ctx, session)
		if err != nil {
			u.logger.Error("deleteRefresh error", "err", err.Error(), "userId", userId.String())
			continue
		}
	}

	u.logger.Info("delete sessions success", "userId", userId.String())
	return nil
}
