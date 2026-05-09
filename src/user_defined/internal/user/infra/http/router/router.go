package router

import (
	"kuronami/internal/core/middleware"
	"kuronami/internal/core/security"
	"net/http"

	"kuronami/internal/user/infra/http/handlers"
)

func GetAuthRouter(userHandlers *handlers.AuthHandlers, jwt *security.JWT) *http.ServeMux {
	mux := http.NewServeMux()

	mux.HandleFunc("POST /auth/login", userHandlers.Login)
	mux.HandleFunc("POST /auth/register", userHandlers.Register)
	mux.HandleFunc("POST /auth/refresh", userHandlers.Refresh)
	mux.Handle("POST /auth/changepass", middleware.AuthMiddleware(jwt)(http.HandlerFunc(userHandlers.ChangePass)))
	mux.HandleFunc("GET /auth/check", userHandlers.CheckAuth)

	mux.HandleFunc("GET /user/profile/{login}", userHandlers.GetByLogin)
	mux.Handle("GET /user/profile/me", middleware.AuthMiddleware(jwt)(http.HandlerFunc(userHandlers.GetMe)))
	mux.Handle("PUT /user/profile", middleware.AuthMiddleware(jwt)(http.HandlerFunc(userHandlers.UpdateUser)))
	mux.Handle("DELETE /user/profile", middleware.AuthMiddleware(jwt)(http.HandlerFunc(userHandlers.DeactivateUser)))

	mux.Handle("GET /user/sessions", middleware.AuthMiddleware(jwt)(http.HandlerFunc(userHandlers.GetSessions)))
	mux.Handle("DELETE /user/sessions", middleware.AuthMiddleware(jwt)(http.HandlerFunc(userHandlers.DeleteSessions)))
	mux.Handle("POST /user/logout", middleware.AuthMiddleware(jwt)(http.HandlerFunc(userHandlers.Logout)))

	return mux
}
