package router

import (
	"kuronami/internal/core/middleware"
	"kuronami/internal/core/security"
	"kuronami/internal/favorite/infra/http/handlers"
	"net/http"
)

func FavoriteRouter(favoriteHandlers *handlers.FavoriteHandler, jwt *security.JWT) *http.ServeMux {
	router := http.NewServeMux()
	router.Handle("GET /user/favorites/me", middleware.AuthMiddleware(jwt)(http.HandlerFunc(favoriteHandlers.GetFavorites)))
	router.Handle("POST /user/favorites/{anime_id}", middleware.AuthMiddleware(jwt)(http.HandlerFunc(favoriteHandlers.Add)))
	router.Handle("DELETE /user/favorites/{anime_id}", middleware.AuthMiddleware(jwt)(http.HandlerFunc(favoriteHandlers.Delete)))
	return router
}
