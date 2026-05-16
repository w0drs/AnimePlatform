package redis

import (
	"github.com/go-redis/redis/v8"
	"kuronami/internal/user/service"
	"log/slog"
)

type tokenRepository struct {
	client *redis.Client
	logger *slog.Logger
}

func NewTokenRepository(logger *slog.Logger, client *redis.Client) service.TokenRepository {
	return &tokenRepository{client: client, logger: logger}
}
