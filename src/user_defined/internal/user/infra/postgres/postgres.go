package postgres

import (
	"github.com/jackc/pgx/v5/pgxpool"
	"log/slog"
)

type UserRepo struct {
	pool   *pgxpool.Pool
	logger *slog.Logger
}

func NewUserRepo(logger *slog.Logger, pool *pgxpool.Pool) *UserRepo {
	return &UserRepo{pool, logger}
}
