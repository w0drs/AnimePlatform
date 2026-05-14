package service

import (
	"context"
	"github.com/google/uuid"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/security"
	"kuronami/internal/user/domain"
	"net/mail"
)

// Login - вход пользователя в аккаунт
// принимает логин пароль, возвращает access token, refresh token и ошибку если есть.
func (u *UserService) Login(ctx context.Context, email, pass string, remember bool, meta domain.SessionMeta) (
	string, string, error) {
	// Валидируем поля
	if _, err := mail.ParseAddress(email); err != nil {
		u.logger.Warn("email address is not valid", "email", email, "error", err.Error())
		return "", "", coreHttp.NewValidationError("mail", err.Error())
	}
	if len(pass) < domain.UserPasswordMinLength {
		u.logger.Warn("password too short", "length", len(pass))
		return "", "", coreHttp.NewValidationError("password len", "too short")
	}
	if len(pass) > domain.UserPasswordMaxLength {
		u.logger.Warn("password too long", "password len", len(pass))
		return "", "", coreHttp.NewValidationError("password", "too long")
	}

	// Получаем пользователя по Email
	getUser, err := u.userRepo.GetByEmail(ctx, email)
	if err != nil {
		u.logger.Debug("get user by email failed", "email", email, "error", err.Error())
		return "", "", err
	}
	// Проверяем, что пароль подходит
	if !security.Verify(getUser.Password, pass) {
		u.logger.Debug("password incorrect")
		return "", "", coreHttp.NewValidationError("verify", "incorrect email or password")
	}
	// Создаем jwtID
	jwtID := uuid.New()

	// Генерируем access токен
	accessToken, err := u.jwt.GenerateAccessToken(jwtID, getUser.ID, getUser.Email, getUser.Role)
	if err != nil {
		u.logger.Debug("generate access token failed", "email", email, "error", err.Error())
		return "", "", coreHttp.NewErrorWithDetails(coreHttp.ErrInternal, "error", err.Error())
	}
	// Генерируем refresh токен
	refreshToken, err := u.jwt.GenerateRefreshToken(jwtID, getUser.ID, getUser.Email, getUser.Role, remember)
	if err != nil {
		u.logger.Debug("generate refresh token failed", "email", email, "error", err.Error())
		return "", "", coreHttp.NewErrorWithDetails(coreHttp.ErrInternal, "error", err.Error())
	}
	// Добавляем запись refresh токена в redis
	err = u.tokeRepo.CreateRefresh(ctx, jwtID, getUser.ID, u.sessionTTL)
	if err != nil {
		u.logger.Debug("save refresh token failed", "email", email, "error", err.Error())
		return "", "", err
	}
	// Сохраняем мета информацию пользователя (ip, device...) в Redis
	err = u.tokeRepo.SaveSessionMeta(ctx, jwtID, meta, u.sessionTTL)
	if err != nil {
		u.logger.Debug("save session meta failed", "email", email, "error", err.Error())
		return "", "", err
	}

	// Добавляем jwtID этого устройства в список всех jwtID пользователя
	// У пользователя может быть несколько подключенных устройств
	err = u.tokeRepo.AddUserSession(ctx, getUser.ID, jwtID)
	if err != nil {
		u.logger.Error("add user session failed", "email", email, "error", err.Error())
		return "", "", err
	}

	u.logger.Info("user logged in", "email", email)
	return accessToken, refreshToken, nil
}
