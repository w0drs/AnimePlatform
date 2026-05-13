package service

import (
	"context"
	"kuronami/internal/comments/domain"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/postgres"
)

func (c *CommentService) GetAnimeComments(ctx context.Context, animeID int, page int) ([]*domain.AnimeComment, error) {
	if animeID <= 0 {
		c.logger.Warn("animeID is invalid")
		return nil, coreHttp.NewValidationError("anime_id", "anime_id is invalid")
	}

	if page <= 0 {
		c.logger.Warn("page is invalid")
		page = 1
	}

	ctxTimeout, cancel := context.WithTimeout(ctx, postgres.DefaultTimeout)
	defer cancel()

	comments, err := c.commentRepo.GetAnimeComments(ctxTimeout, animeID, page)
	if err != nil {
		c.logger.Debug("get anime comments failed", "anime_id", animeID, "page", page, "error", err.Error())
		return nil, err
	}

	c.logger.Debug("get anime comments", "count", len(comments))
	return comments, nil
}

func (c *CommentService) GetNewsComments(ctx context.Context, newsID int, page int) ([]*domain.NewsComment, error) {
	if newsID <= 0 {
		c.logger.Warn("newsID is invalid")
		return nil, coreHttp.NewValidationError("news_id", "news_id is invalid")
	}

	if page <= 0 {
		c.logger.Warn("page is invalid")
		page = 1
	}

	ctxTimeout, cancel := context.WithTimeout(ctx, postgres.DefaultTimeout)
	defer cancel()

	comments, err := c.commentRepo.GetNewsComments(ctxTimeout, newsID, page)
	if err != nil {
		c.logger.Debug("get news comments failed", "news_id", newsID, "page", page, "error", err.Error())
		return nil, err
	}

	c.logger.Debug("get news comments", "count", len(comments))
	return comments, nil
}
