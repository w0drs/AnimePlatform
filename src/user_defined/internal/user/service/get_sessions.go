package service

import (
	"context"
	"github.com/google/uuid"
	"kuronami/internal/user/domain"
)

func (u *UserService) GetSessions(ctx context.Context, userId uuid.UUID) ([]domain.SessionInfo, error) {

	sessions, err := u.tokeRepo.GetUserSessions(ctx, userId)
	if err != nil {
		u.logger.Error("getUserSessions error", "err", err.Error(), "userId", userId.String())
		return nil, err
	}
	var sessionsInfo = make([]domain.SessionInfo, len(sessions))

	for i, session := range sessions {
		meta, err := u.tokeRepo.GetSessionMeta(ctx, session)
		if err != nil {
			u.logger.Error("failed to get session meta data", "err", err.Error(), "jwtID", session.String())
			continue
		}
		sessionsInfo[i] = domain.SessionInfo{
			JTI:          session,
			IP:           meta.IP,
			Device:       meta.Device,
			LastActivity: meta.LastActivity,
		}
	}
	u.logger.Info("getSessions", "userId", userId.String())
	return sessionsInfo, nil
}
