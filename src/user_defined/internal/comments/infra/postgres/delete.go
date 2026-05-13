package postgres

import (
	"context"
	"fmt"
	"github.com/google/uuid"
)

func (c *CommentsPG) DeleteAnimeComment(ctx context.Context, userID uuid.UUID, commentID int, isModer bool) error {
	query := `
		UPDATE comments 
		SET is_deleted = true, deleted_at = NOW()
		WHERE id = $1 
			AND is_deleted = false
			AND ($2 = true OR user_id = $3)
	`

	result, err := c.pool.Exec(ctx, query, commentID, isModer, userID)
	if err != nil {
		c.logger.Error("delete comment query failed",
			"comment_id", commentID,
			"error", err.Error())
		return fmt.Errorf("database error: %w", err)
	}

	if result.RowsAffected() == 0 {
		c.logger.Debug("no comment updated (already deleted, not found, or permission denied)",
			"comment_id", commentID,
			"user_id", userID,
			"is_admin", isModer)
		return nil
	}

	c.logger.Info("comment deleted successfully",
		"comment_id", commentID,
		"user_id", userID,
		"is_admin", isModer)

	return nil
}

func (c *CommentsPG) DeleteNewsComment(ctx context.Context, userID uuid.UUID, commentID int) error {
	return nil
}
