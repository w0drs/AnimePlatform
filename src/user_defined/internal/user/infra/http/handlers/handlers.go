package handlers

import (
	"kuronami/internal/core/security"
	"kuronami/internal/user/service"
	"log/slog"
)

/*
Что точно должно быть

POST /auth/login  <without token>
POST /auth/register  <without token>
POST /auth/changepass   <token>
POST /auth/refresh <token>
POST /auth/check

GET /user/profile/{login}  <without token>
GET /user/profile/me  <token>
PUT /user/profile/me  <token>
DELETE /user/profile/me  <token>

GET /user/sessions <token>
DELETE /user/sessions <token>
POST /user/logout <token>
*/

type AuthHandlers struct {
	logger      *slog.Logger
	userService *service.UserService
	jwt         *security.JWT
}

func NewAuthHandlers(logger *slog.Logger, userService *service.UserService, jwt *security.JWT) *AuthHandlers {
	return &AuthHandlers{logger, userService, jwt}
}
