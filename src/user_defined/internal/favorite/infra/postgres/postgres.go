package postgres

import (
	"log/slog"

	"github.com/jackc/pgx/v5/pgxpool"
)

type FavoritePG struct {
	pool   *pgxpool.Pool
	logger *slog.Logger
}

func NewFavoritePG(logger *slog.Logger, pool *pgxpool.Pool) *FavoritePG {
	return &FavoritePG{pool, logger}
}
