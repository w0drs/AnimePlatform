package redis

import (
	"context"
	"errors"
	"github.com/go-redis/redis/v8"
	"github.com/google/uuid"
	coreHttp "kuronami/internal/core/http"
	"time"
)

func (r *tokenRepository) CreateRefresh(ctx context.Context, jti uuid.UUID, userID uuid.UUID, ttl time.Duration) error {
	err := r.client.SetEX(ctx, refreshKey(jti), userID.String(), ttl).Err()
	if err != nil {
		r.logger.Error("error saving refresh token", "userID", userID.String(), "error", err.Error())
		return coreHttp.NewErrorWithDetails(coreHttp.ErrInternal, "error", err)
	}
	r.logger.Debug("refresh token saved", "userId", userID.String())
	return nil
}

func (r *tokenRepository) GetUserIDByRefresh(ctx context.Context, jti uuid.UUID) (*uuid.UUID, error) {
	userIDStr, err := r.client.Get(ctx, refreshKey(jti)).Result()
	if errors.Is(err, redis.Nil) {
		r.logger.Error("refresh token is nil", "error", err.Error(), "jtwId", jti.String())
		return nil, coreHttp.ErrTokenNotFound
	}
	if err != nil {
		r.logger.Error("error getting user id by refresh token", "jti", jti.String(), "error", err.Error())
		return nil, coreHttp.NewErrorWithDetails(coreHttp.ErrInternal, "error", err)
	}

	userID, err := uuid.Parse(userIDStr)
	if err != nil {
		r.logger.Error("error parsing user id by refresh token", "userID", userIDStr, "error", err.Error())
		return nil, coreHttp.NewErrorWithDetails(coreHttp.ErrInvalidBody, "error", err)
	}

	r.logger.Debug("user id by refresh token", "userId", userID.String())
	return &userID, nil
}

func (r *tokenRepository) DeleteRefresh(ctx context.Context, jti uuid.UUID) error {
	err := r.client.Del(ctx, refreshKey(jti)).Err()
	if err != nil {
		r.logger.Error("error deleting refresh token", "jti", jti.String(), "error", err.Error())
		return coreHttp.NewErrorWithDetails(coreHttp.ErrInternal, "error", err)
	}

	r.logger.Debug("refresh token deleted", "jti", jti.String())
	return nil
}
