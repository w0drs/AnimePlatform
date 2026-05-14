package service

import (
	"context"
	"github.com/google/uuid"
	"kuronami/internal/comments/domain"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/postgres"
)

func (c *CommentService) AddAnimeComment(ctx context.Context, comment domain.AnimeComment) (*domain.AnimeComment, error) {
	if comment.Text == "" {
		c.logger.Warn("comment text is empty")
		return nil, coreHttp.NewValidationError("comment text", "comment text is empty")
	}
	if comment.UserID == uuid.Nil {
		c.logger.Warn("comment user id is empty")
		return nil, coreHttp.NewValidationError("comment userID", "comment userID is empty")
	}
	if comment.AnimeID <= 0 {
		c.logger.Warn("comment anime id is invalid")
		return nil, coreHttp.NewValidationError("comment animeID", "comment animeID is invalid")
	}

	ctxTimeout, cancel := context.WithTimeout(ctx, postgres.DefaultTimeout)
	defer cancel()

	commentNew, err := c.commentRepo.AddAnimeComment(ctxTimeout, comment)
	if err != nil {
		c.logger.Debug("add comment failed",
			"user_id", comment.UserID,
			"anime_id", comment.AnimeID,
			"text_len", len(comment.Text),
			"error", err.Error())
		return nil, err
	}

	c.logger.Info("comment added successfully",
		"comment_id", commentNew.ID,
		"user_id", commentNew.UserID.String(),
		"anime_id", commentNew.AnimeID)
	return commentNew, nil
}

func (c *CommentService) AddNewsComment(ctx context.Context, comment domain.NewsComment) (*domain.NewsComment, error) {
	if comment.Text == "" {
		c.logger.Warn("comment text is empty")
		return nil, coreHttp.NewValidationError("comment text", "comment text is empty")
	}
	if comment.UserID == uuid.Nil {
		c.logger.Warn("comment user id is empty")
		return nil, coreHttp.NewValidationError("comment userID", "comment userID is empty")
	}
	if comment.NewsID <= 0 {
		c.logger.Warn("comment news id is invalid")
		return nil, coreHttp.NewValidationError("comment newsID", "comment newsID is invalid")
	}

	ctxTimeout, cancel := context.WithTimeout(ctx, postgres.DefaultTimeout)
	defer cancel()

	commentNew, err := c.commentRepo.AddNewsComment(ctxTimeout, comment)
	if err != nil {
		c.logger.Debug("add comment failed",
			"user_id", comment.UserID,
			"news_id", comment.NewsID,
			"text_len", len(comment.Text),
			"error", err.Error())
		return nil, err
	}

	c.logger.Info("comment added successfully",
		"comment_id", commentNew.ID,
		"user_id", commentNew.UserID.String(),
		"news_id", commentNew.NewsID)
	return commentNew, nil
}
