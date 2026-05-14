package service

import "log/slog"

type FavoriteService struct {
	logger        *slog.Logger
	favoritesRepo FavoriteRepository
}

func NewFavoriteService(logger *slog.Logger, favoritesRepo FavoriteRepository) *FavoriteService {
	return &FavoriteService{logger, favoritesRepo}
}
