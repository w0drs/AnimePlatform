package service

import (
	"kuronami/internal/core/security"
	"log/slog"
	"time"
)

type UserService struct {
	logger     *slog.Logger
	userRepo   UserRepository
	tokeRepo   TokenRepository
	jwt        *security.JWT
	sessionTTL time.Duration
}

func NewUserService(logger *slog.Logger, userRepo UserRepository, tokenRepo TokenRepository, jwt *security.JWT,
	sessionTTl time.Duration) *UserService {
	return &UserService{
		logger:     logger,
		userRepo:   userRepo,
		tokeRepo:   tokenRepo,
		jwt:        jwt,
		sessionTTL: sessionTTl,
	}
}
