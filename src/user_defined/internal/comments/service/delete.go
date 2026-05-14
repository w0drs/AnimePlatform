package service

import (
	"context"
	"github.com/google/uuid"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/postgres"
	domainUser "kuronami/internal/user/domain"
)

func (c *CommentService) DeleteAnimeComment(ctx context.Context, user domainUser.User,
	commentID int) error {

	if commentID <= 0 {
		c.logger.Warn("anime comment id is invalid", "commentID", commentID)
		return coreHttp.NewValidationError("anime comment id", "anime comment id is invalid")
	}
	if user.ID == uuid.Nil {
		c.logger.Warn("anime comment user id is invalid")
		return coreHttp.NewValidationError("user id", "anime comment user id is invalid")
	}

	var isAdmin = user.Role == domainUser.Admin || user.Role == domainUser.Moderator

	ctxTimeout, cancel := context.WithTimeout(ctx, postgres.DefaultTimeout)
	defer cancel()
	err := c.commentRepo.DeleteAnimeComment(ctxTimeout, user.ID, commentID, isAdmin)
	if err != nil {
		c.logger.Debug("delete anime comment failed", "error", err.Error())
		return err
	}
	c.logger.Info("delete anime comment success", "commentID", commentID)
	return nil
}

func (c *CommentService) DeleteNewsComment(ctx context.Context, user domainUser.User,
	commentID int) error {

	if commentID <= 0 {
		c.logger.Warn("news comment id is invalid", "commentID", commentID)
		return coreHttp.NewValidationError("news comment id", "news comment id is invalid")
	}
	if user.ID == uuid.Nil {
		c.logger.Warn("news comment user id is invalid")
		return coreHttp.NewValidationError("user id", "news comment user id is invalid")
	}

	var isAdmin = user.Role == domainUser.Admin || user.Role == domainUser.Moderator

	ctxTimeout, cancel := context.WithTimeout(ctx, postgres.DefaultTimeout)
	defer cancel()
	err := c.commentRepo.DeleteNewsComment(ctxTimeout, user.ID, commentID, isAdmin)
	if err != nil {
		c.logger.Debug("delete news comment failed", "error", err.Error())
		return err
	}
	c.logger.Info("delete news comment success", "commentID", commentID)
	return nil
}
