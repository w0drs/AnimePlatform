package postgres

import (
	"context"
	"kuronami/internal/comments/domain"
	coreHttp "kuronami/internal/core/http"
)

func (c *CommentsPG) AddAnimeComment(ctx context.Context, comment domain.AnimeComment) (*domain.AnimeComment, error) {
	query := `
        INSERT INTO anime_comments (text, user_id, anime_id, tagged_user_id)
        VALUES ($1, $2, $3, $4)
        RETURNING id, created_at
    `

	err := c.pool.QueryRow(ctx, query, comment.Text, comment.UserID, comment.AnimeID, comment.TaggedUserID).
		Scan(&comment.ID, &comment.CreatedAt)
	if err != nil {
		c.logger.Error("add anime comment failed",
			"user_id", comment.UserID,
			"anime_id", comment.AnimeID,
			"error", err.Error())
		return nil, coreHttp.ErrInternal
	}

	c.logger.Debug("anime comment added successfully",
		"comment_id", comment.ID,
		"user_id", comment.UserID,
		"anime_id", comment.AnimeID)
	return &comment, nil
}

func (c *CommentsPG) AddNewsComment(ctx context.Context, comment domain.NewsComment) (*domain.NewsComment, error) {
	query := `
        INSERT INTO news_comments (text, user_id, news_id, tagged_user_id)
        VALUES ($1, $2, $3, $4)
        RETURNING id, created_at
    `

	err := c.pool.QueryRow(ctx, query, comment.Text, comment.UserID, comment.NewsID, comment.TaggedUserID).
		Scan(&comment.ID, &comment.CreatedAt)
	if err != nil {
		c.logger.Error("add anime comment failed",
			"user_id", comment.UserID,
			"anime_id", comment.NewsID,
			"error", err.Error())
		return nil, coreHttp.ErrInternal
	}

	c.logger.Debug("anime comment added successfully",
		"comment_id", comment.ID,
		"user_id", comment.UserID,
		"anime_id", comment.NewsID)
	return &comment, nil
}
