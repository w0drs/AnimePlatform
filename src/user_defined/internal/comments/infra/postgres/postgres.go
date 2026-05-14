package postgres

import (
	"github.com/jackc/pgx/v5/pgxpool"
	"log/slog"
)

type CommentsPG struct {
	logger *slog.Logger
	pool   *pgxpool.Pool
}

func NewCommentsPG(logger *slog.Logger, pool *pgxpool.Pool) *CommentsPG {
	return &CommentsPG{logger, pool}
}
