package service

import "log/slog"

type FavoriteService struct {
	logger        *slog.Logger
	favoritesRepo FavoriteRepository
}
