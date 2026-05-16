package router

import (
	"github.com/go-redis/redis/v8"
	"kuronami/internal/core/middleware"
	"kuronami/internal/core/security"
	"log/slog"
	"net/http"

	"kuronami/internal/user/infra/http/handlers"
)

func GetAuthRouter(logger *slog.Logger, userHandlers *handlers.AuthHandlers,
	jwt *security.JWT, pool *redis.Client) *http.ServeMux {

	mux := http.NewServeMux()

	mux.HandleFunc("POST /auth/login", userHandlers.Login)
	mux.HandleFunc("POST /auth/register", userHandlers.Register)
	mux.HandleFunc("POST /auth/refresh", userHandlers.Refresh)
	mux.HandleFunc("POST /auth/check", userHandlers.CheckAuth)
	mux.Handle("POST /auth/changepass", middleware.AuthMiddleware(logger, jwt, pool)(http.HandlerFunc(userHandlers.ChangePass)))
	mux.Handle("POST /auth/logout", middleware.AuthMiddleware(logger, jwt, pool)(http.HandlerFunc(userHandlers.Logout)))

	mux.HandleFunc("POST /users/batch", userHandlers.GetUserList)

	mux.HandleFunc("GET /user/profile/{login}", userHandlers.GetByLogin)
	mux.Handle("GET /user/profile/me", middleware.AuthMiddleware(logger, jwt, pool)(http.HandlerFunc(userHandlers.GetMe)))
	mux.Handle("PUT /user/profile/me", middleware.AuthMiddleware(logger, jwt, pool)(http.HandlerFunc(userHandlers.UpdateUser)))
	mux.Handle("DELETE /user/profile/me", middleware.AuthMiddleware(logger, jwt, pool)(http.HandlerFunc(userHandlers.DeactivateUser)))

	mux.Handle("GET /user/sessions", middleware.AuthMiddleware(logger, jwt, pool)(http.HandlerFunc(userHandlers.GetSessions)))
	mux.Handle("DELETE /user/sessions", middleware.AuthMiddleware(logger, jwt, pool)(http.HandlerFunc(userHandlers.DeleteSessions)))

	return mux
}
