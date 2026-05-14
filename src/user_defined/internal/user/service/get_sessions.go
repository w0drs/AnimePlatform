package service

import (
	"context"
	"github.com/google/uuid"
	"kuronami/internal/user/domain"
)

func (u *UserService) GetSessions(ctx context.Context, userId uuid.UUID) ([]domain.SessionInfo, error) {

	sessions, err := u.tokeRepo.GetUserSessions(ctx, userId)
	if err != nil {
		u.logger.Debug("get user sessions failed", "error", err.Error(), "userId", userId.String())
		return nil, err
	}
	var sessionsInfo = make([]domain.SessionInfo, 0)

	for _, session := range sessions {
		meta, err := u.tokeRepo.GetSessionMeta(ctx, session)
		if err != nil {
			u.logger.Debug("failed to get session meta data", "error", err.Error(), "jwtID", session.String())
			continue
		}

		sessionsInfo = append(sessionsInfo, domain.SessionInfo{
			JTI:          session,
			IP:           meta.IP,
			Device:       meta.Device,
			LastActivity: meta.LastActivity,
		})
	}
	u.logger.Info("get sessions", "userId", userId.String())
	return sessionsInfo, nil
}
