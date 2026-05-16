package service

import (
	"context"
	"github.com/google/uuid"
	"kuronami/internal/comments/domain"
)

type CommentsRepository interface {
	GetAnimeComments(ctx context.Context, animeID int, page int) ([]*domain.AnimeComment, error)
	AddAnimeComment(ctx context.Context, comment domain.AnimeComment) (*domain.AnimeComment, error)
	DeleteAnimeComment(ctx context.Context, userID uuid.UUID, commentID int, isModer bool) error

	GetNewsComments(ctx context.Context, newsID int, page int) ([]*domain.NewsComment, error)
	AddNewsComment(ctx context.Context, comment domain.NewsComment) (*domain.NewsComment, error)
	DeleteNewsComment(ctx context.Context, userID uuid.UUID, commentID int, isModer bool) error
}
