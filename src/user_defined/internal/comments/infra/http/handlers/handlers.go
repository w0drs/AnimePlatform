package handlers

import (
	"kuronami/internal/comments/service"
	"log/slog"
)

type CommentsHandlers struct {
	logger  *slog.Logger
	comServ *service.CommentService
}

func NewCommentsHandlers(logger *slog.Logger, comServ *service.CommentService) *CommentsHandlers {
	return &CommentsHandlers{logger, comServ}
}
