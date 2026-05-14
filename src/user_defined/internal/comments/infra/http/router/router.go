package router

import (
	"github.com/go-redis/redis/v8"
	"kuronami/internal/comments/infra/http/handlers"
	"kuronami/internal/core/middleware"
	"kuronami/internal/core/security"
	"log/slog"
	"net/http"
)

func CommentsRouter(logger *slog.Logger, comHandles *handlers.CommentsHandlers,
	jwt *security.JWT, pool *redis.Client) *http.ServeMux {
	router := http.NewServeMux()
	// аниме эндпоинты
	router.Handle("POST /comments/anime/", middleware.AuthMiddleware(logger, jwt, pool)(
		http.HandlerFunc(comHandles.AddAnimeComment)))
	router.Handle("DELETE /comments/anime/{comment_id}", middleware.AuthMiddleware(logger, jwt, pool)(
		http.HandlerFunc(comHandles.DeleteAnimeComments)))
	router.HandleFunc("GET /comments/anime/{anime_id}", comHandles.GetAnimeComments)
	// эндпоиниты новостей
	router.Handle("POST /comments/news/", middleware.AuthMiddleware(logger, jwt, pool)(
		http.HandlerFunc(comHandles.AddNewsComment)))
	router.Handle("DELETE /comments/news/{comment_id}", middleware.AuthMiddleware(logger, jwt, pool)(
		http.HandlerFunc(comHandles.DeleteNewsComments)))
	router.HandleFunc("GET /comments/news/{news_id}", comHandles.GetNewsComments)
	//
	return router
}
