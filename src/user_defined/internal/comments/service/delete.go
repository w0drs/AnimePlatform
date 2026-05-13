package service

import (
	"context"
	"github.com/google/uuid"
	domainComment "kuronami/internal/comments/domain"
	coreHttp "kuronami/internal/core/http"
	domainUser "kuronami/internal/user/domain"
)

func (c *CommentService) DeleteAnimeComment(ctx context.Context, user domainUser.User,
	comment domainComment.AnimeComment) error {

	if comment.ID <= 0 {
		c.logger.Warn("anime comment id is invalid", "commentID", comment.ID)
		return coreHttp.NewValidationError("anime comment id", "anime comment id is invalid")
	}
	if comment.UserID == uuid.Nil || user.ID == uuid.Nil {
		c.logger.Warn("anime comment user id is invalid")
		return coreHttp.NewValidationError("user id", "anime comment user id is invalid")
	}

	var isAdmin = user.Role == domainUser.Admin || user.Role == domainUser.Moderator

	err := c.commentRepo.DeleteAnimeComment(ctx, comment.UserID, comment.ID, isAdmin)
	if err != nil {
		c.logger.Debug("delete anime comment failed", "error", err.Error())
		return err
	}
	c.logger.Info("delete anime comment success", "commentID", comment.ID)
	return nil
}

func (c *CommentService) DeleteNewsComment(ctx context.Context, user domainUser.User,
	comment domainComment.NewsComment) error {

	if comment.ID <= 0 {
		c.logger.Warn("news comment id is invalid", "commentID", comment.ID)
		return coreHttp.NewValidationError("news comment id", "news comment id is invalid")
	}
	if comment.UserID == uuid.Nil || user.ID == uuid.Nil {
		c.logger.Warn("news comment user id is invalid")
		return coreHttp.NewValidationError("user id", "news comment user id is invalid")
	}

	var isAdmin = user.Role == domainUser.Admin || user.Role == domainUser.Moderator

	err := c.commentRepo.DeleteNewsComment(ctx, comment.UserID, comment.ID, isAdmin)
	if err != nil {
		c.logger.Debug("delete news comment failed", "error", err.Error())
		return err
	}
	c.logger.Info("delete news comment success", "commentID", comment.ID)
	return nil
}
