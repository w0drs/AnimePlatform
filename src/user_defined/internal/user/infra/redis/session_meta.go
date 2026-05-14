package redis

import (
	"context"
	"encoding/json"
	"errors"
	"github.com/go-redis/redis/v8"
	"github.com/google/uuid"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/user/domain"
	"time"
)

func (r *tokenRepository) SaveSessionMeta(ctx context.Context, jti uuid.UUID, meta domain.SessionMeta, ttl time.Duration) error {
	meta.LastActivity = time.Now()

	data, err := json.Marshal(meta)
	if err != nil {
		r.logger.Error("error marshalling session meta", "jti", jti.String(), "error", err.Error())
		return coreHttp.NewErrorWithDetails(coreHttp.ErrInternal, "error", err.Error())
	}
	err = r.client.SetEX(ctx, sessionMetaKey(jti), data, ttl).Err()
	if err != nil {
		r.logger.Error("error setting session meta", "jti", jti.String(), "error", err.Error())
		return coreHttp.NewErrorWithDetails(coreHttp.ErrInternal, "error", err.Error())
	}

	r.logger.Debug("session meta saved", "jti", jti.String())
	return nil
}

func (r *tokenRepository) GetSessionMeta(ctx context.Context, jti uuid.UUID) (*domain.SessionMeta, error) {
	data, err := r.client.Get(ctx, sessionMetaKey(jti)).Bytes()
	if errors.Is(err, redis.Nil) {
		r.logger.Warn("session meta not found", "jti", jti.String())
		return nil, coreHttp.ErrSessionMetaNotFound
	}
	if err != nil {
		r.logger.Error("error getting session meta", "jti", jti.String(), "error", err.Error())
		return nil, coreHttp.NewErrorWithDetails(coreHttp.ErrInternal, "error", err.Error())
	}

	var meta domain.SessionMeta
	if err = json.Unmarshal(data, &meta); err != nil {
		r.logger.Error("error unmarshalling session meta", "jti", jti.String(), "error", err.Error())
		return nil, coreHttp.NewErrorWithDetails(coreHttp.ErrInternal, "error", err.Error())
	}

	r.logger.Debug("session meta found", "jti", jti.String())
	return &meta, nil
}

func (r *tokenRepository) UpdateSessionMeta(ctx context.Context, jti uuid.UUID, ip string) error {

	// Получем сессию которая щас есть
	meta, err := r.GetSessionMeta(ctx, jti)
	if err != nil {
		r.logger.Error("error getting session meta", "jti", jti.String(), "error", err.Error())
		return err
	}

	meta.IP = ip
	meta.LastActivity = time.Now()

	// Сохраняем обратно
	data, err := json.Marshal(meta)
	if err != nil {
		r.logger.Error("error marshalling session meta", "jti", jti.String(), "error", err.Error())
		return coreHttp.NewErrorWithDetails(coreHttp.ErrInternal, "error", err.Error())
	}

	// Получаем TTL из существующего ключа
	ttl, err := r.client.TTL(ctx, sessionMetaKey(jti)).Result()
	if err != nil {
		r.logger.Error("error getting session meta", "jti", jti.String(), "error", err.Error())
		return coreHttp.NewErrorWithDetails(coreHttp.ErrInternal, "error", err.Error())
	}

	err = r.client.SetEX(ctx, sessionMetaKey(jti), data, ttl).Err()
	if err != nil {
		r.logger.Error("error setting session meta", "jti", jti.String(), "error", err.Error())
		return coreHttp.NewErrorWithDetails(coreHttp.ErrInternal, "error", err.Error())
	}

	r.logger.Debug("session meta updated", "jti", jti.String())
	return nil
}

func (r *tokenRepository) DeleteSessionMeta(ctx context.Context, jti uuid.UUID) error {
	err := r.client.Del(ctx, sessionMetaKey(jti)).Err()
	if err != nil {
		r.logger.Error("error deleting session meta", "jti", jti.String(), "error", err.Error())
		return coreHttp.NewErrorWithDetails(coreHttp.ErrInternal, "error", err.Error())
	}

	r.logger.Debug("session meta deleted", "jti", jti.String())
	return nil
}
