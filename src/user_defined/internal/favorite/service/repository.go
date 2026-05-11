package service

import (
	"context"
	"kuronami/internal/favorite/domain"

	"github.com/google/uuid"
)

type FavoriteRepository interface {
	GetByUserID(ctx context.Context, userID uuid.UUID) ([]*domain.Favorite, error)
	Add(ctx context.Context, userID uuid.UUID, animeID int) error
	Delete(ctx context.Context, userID uuid.UUID, animeID int) error
}
