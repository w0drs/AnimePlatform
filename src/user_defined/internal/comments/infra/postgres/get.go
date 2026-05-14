package postgres

import (
	"context"
	"errors"
	"github.com/jackc/pgx/v5"
	"kuronami/internal/comments/domain"
	coreHttp "kuronami/internal/core/http"
)

func (c *CommentsPG) GetAnimeComments(ctx context.Context, animeID int, page int) ([]*domain.AnimeComment, error) {
	maxID := int64(page * domain.DefaultCommentsPerPage)
	if maxID < 0 {
		return []*domain.AnimeComment{}, nil
	}
	query := `
        SELECT id, text, user_id, anime_id, tagged_user_id, created_at
        FROM anime_comments
        WHERE anime_id = $1 
            AND is_deleted = false 
            AND id < $2
        ORDER BY id DESC
        LIMIT $3
    `

	rows, err := c.pool.Query(ctx, query, animeID, maxID, domain.DefaultCommentsPerPage)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			c.logger.Warn("no anime comments found",
				"animeID", animeID,
				"page", page)
			return []*domain.AnimeComment{}, nil
		}
		c.logger.Error("get anime comments failed",
			"animeID", animeID,
			"page", page,
			"error", err.Error())
		return nil, coreHttp.ErrInternal
	}
	defer rows.Close()

	comments, err := pgx.CollectRows(rows, pgx.RowToAddrOfStructByName[domain.AnimeComment])
	if err != nil {
		c.logger.Error("get anime comments failed",
			"animeID", animeID,
			"page", page,
			"error", err.Error())
		return nil, coreHttp.ErrInternal
	}

	c.logger.Debug("get anime comments successful", "animeID", animeID, "page", page)
	return comments, nil
}

func (c *CommentsPG) GetNewsComments(ctx context.Context, newsID int, page int) ([]*domain.NewsComment, error) {
	maxID := int64(page * domain.DefaultCommentsPerPage)
	if maxID < 0 {
		return []*domain.NewsComment{}, nil
	}
	query := `
        SELECT id, text, user_id, news_id, tagged_user_id, created_at
        FROM news_comments
        WHERE news_id = $1 
            AND is_deleted = false 
            AND id < $2
        ORDER BY id DESC
        LIMIT $3
    `

	rows, err := c.pool.Query(ctx, query, newsID, maxID, domain.DefaultCommentsPerPage)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			c.logger.Warn("no news comments found",
				"newsID", newsID,
				"page", page)
			return []*domain.NewsComment{}, nil
		}
		c.logger.Error("get news comments failed",
			"newsID", newsID,
			"page", page,
			"error", err.Error())
		return nil, coreHttp.ErrInternal
	}
	defer rows.Close()

	comments, err := pgx.CollectRows(rows, pgx.RowToAddrOfStructByName[domain.NewsComment])
	if err != nil {
		c.logger.Error("get news comments failed",
			"newsID", newsID,
			"page", page,
			"error", err.Error())
		return nil, coreHttp.ErrInternal
	}

	c.logger.Debug("get news comments successful", "newsID", newsID, "page", page)
	return comments, nil
}
