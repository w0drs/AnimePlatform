package router

import (
	"github.com/go-redis/redis/v8"
	"kuronami/internal/core/middleware"
	"kuronami/internal/core/security"
	"kuronami/internal/favorite/infra/http/handlers"
	"log/slog"
	"net/http"
)

func FavoriteRouter(logger *slog.Logger, favoriteHandlers *handlers.FavoriteHandler,
	jwt *security.JWT, pool *redis.Client) *http.ServeMux {

	router := http.NewServeMux()
	router.Handle("GET /user/favorites/me", middleware.AuthMiddleware(logger, jwt, pool)(http.HandlerFunc(favoriteHandlers.GetFavorites)))
	router.Handle("GET /user/favorites/me/{anime_id}", middleware.AuthMiddleware(logger, jwt, pool)(http.HandlerFunc(favoriteHandlers.GetFavorite)))
	router.Handle("POST /user/favorites/{anime_id}", middleware.AuthMiddleware(logger, jwt, pool)(http.HandlerFunc(favoriteHandlers.Add)))
	router.Handle("DELETE /user/favorites/{anime_id}", middleware.AuthMiddleware(logger, jwt, pool)(http.HandlerFunc(favoriteHandlers.Delete)))

	return router
}
