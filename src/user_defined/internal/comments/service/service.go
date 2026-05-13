package service

import "log/slog"

type CommentService struct {
	logger      *slog.Logger
	commentRepo CommentsRepository
}

func NewCommentService(logger *slog.Logger, commentRepo CommentsRepository) *CommentService {
	return &CommentService{logger, commentRepo}
}
