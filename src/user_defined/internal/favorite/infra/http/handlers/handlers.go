package handlers

import (
	"kuronami/internal/favorite/service"
	"log/slog"
)

type FavoriteHandler struct {
	logger     *slog.Logger
	favService *service.FavoriteService
}

func NewFavoriteHandler(logger *slog.Logger, favService *service.FavoriteService) *FavoriteHandler {
	return &FavoriteHandler{logger, favService}
}
