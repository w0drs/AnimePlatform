package redis

import (
	"context"
	"github.com/google/uuid"
	coreHttp "kuronami/internal/core/http"
)

func (r *tokenRepository) AddUserSession(ctx context.Context, userID uuid.UUID, jti uuid.UUID) error {
	err := r.client.SAdd(ctx, userSessionsKey(userID), jti.String()).Err()
	if err != nil {
		r.logger.Error("error saving user session to redis", "err", err.Error())
		return coreHttp.NewErrorWithDetails(coreHttp.ErrInternal, "error", err.Error())
	}

	r.logger.Info("added user session to redis", "userID", userID.String())
	return nil
}

func (r *tokenRepository) GetUserSessions(ctx context.Context, userID uuid.UUID) ([]uuid.UUID, error) {
	members, err := r.client.SMembers(ctx, userSessionsKey(userID)).Result()
	if err != nil {
		r.logger.Error("error saving user sessions to redis", "err", err.Error())
		return nil, coreHttp.NewErrorWithDetails(coreHttp.ErrInternal, "error", err.Error())
	}

	jtis := make([]uuid.UUID, 0, len(members))
	for _, member := range members {
		jti, err := uuid.Parse(member)
		if err != nil {
			r.logger.Warn("error saving user session to redis", "err", err.Error())
			continue
		}
		jtis = append(jtis, jti)
	}

	r.logger.Info("got user sessions from redis", "users", userID.String())
	return jtis, nil
}

func (r *tokenRepository) RemoveUserSession(ctx context.Context, userID uuid.UUID, jti uuid.UUID) error {
	err := r.client.SRem(ctx, userSessionsKey(userID), jti.String()).Err()
	if err != nil {
		r.logger.Error("error removing user session to redis", "err", err.Error())
		return coreHttp.NewErrorWithDetails(coreHttp.ErrInternal, "error", err.Error())
	}

	r.logger.Info("removed user session to redis", "userID", userID.String())
	return nil
}

func (r *tokenRepository) RemoveAllUserSessions(ctx context.Context, userID uuid.UUID) error {
	err := r.client.Del(ctx, userSessionsKey(userID)).Err()
	if err != nil {
		r.logger.Error("error removing user sessions to redis", "err", err.Error())
		return coreHttp.NewErrorWithDetails(coreHttp.ErrInternal, "error", err.Error())
	}

	r.logger.Info("removed user sessions to redis", "users", userID.String())
	return nil
}
