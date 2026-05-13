package postgres

import (
	"context"
	"kuronami/internal/comments/domain"
)

func (c *CommentsPG) AddAnimeComment(ctx context.Context, comment domain.AnimeComment) (*domain.AnimeComment, error) {
	query := `
        INSERT INTO anime_comments (text, user_id, anime_id, tagged_user_id)
        VALUES ($1, $2, $3, $4)
        RETURNING id
    `
	_ = query
	return &comment, nil
}
