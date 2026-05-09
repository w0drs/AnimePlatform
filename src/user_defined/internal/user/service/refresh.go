package service

import (
	"context"
	"errors"
	"github.com/google/uuid"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/security"
)

func (u *UserService) Refresh(ctx context.Context, claims security.Claims) (string, string, error) {

	userID, err := u.tokeRepo.GetUserIDByRefresh(ctx, claims.JwtID)
	if err != nil {
		u.logger.Debug("jwtID is empty", "error", err.Error())
		if errors.As(err, &coreHttp.ErrTokenNotFound) {
			// еcли нет, то значит уже был refresh, украли
			err := u.disconnection(ctx, claims)
			if err != nil {
				return "", "", err
			}
			return "", "", coreHttp.ErrInvalidCredentials
		}
		return "", "", coreHttp.ErrInternal
	}
	// удаляем текущую сессию
	err = u.tokeRepo.DeleteRefresh(ctx, claims.JwtID)
	if err != nil {
		u.logger.Warn("failed to delete refresh token", "error", err.Error())
		return "", "", err
	}
	// сохраняем мету, чтобы переиспользовать
	meta, err := u.tokeRepo.GetSessionMeta(ctx, claims.JwtID)
	if err != nil {
		u.logger.Warn("failed to get session meta", "error", err.Error())
		return "", "", err
	}
	// удаляем мету
	err = u.tokeRepo.DeleteSessionMeta(ctx, claims.JwtID)
	if err != nil {
		u.logger.Warn("failed to delete session meta", "error", err.Error())
		return "", "", err
	}
	// удаляем из списка сессий
	err = u.tokeRepo.RemoveUserSession(ctx, *userID, claims.JwtID)
	if err != nil {
		u.logger.Warn("failed to remove user session", "error", err.Error())
		return "", "", err
	}

	// Создаем новое

	newJwtId := uuid.New()

	accessToken, err := u.jwt.GenerateAccessToken(newJwtId, *userID, claims.Email, claims.Role)
	if err != nil {
		u.logger.Warn("failed to generate access token", "error", err.Error())
		return "", "", coreHttp.NewErrorWithDetails(coreHttp.ErrInternal, "error", err.Error())
	}

	refreshToken, err := u.jwt.GenerateRefreshToken(newJwtId, *userID, claims.Email, claims.Role, false)
	if err != nil {
		u.logger.Warn("failed to generate refresh token", "error", err.Error())
		return "", "", coreHttp.NewErrorWithDetails(coreHttp.ErrInternal, "error", err.Error())
	}

	err = u.tokeRepo.CreateRefresh(ctx, *userID, newJwtId, u.sessionTTL)
	if err != nil {
		u.logger.Warn("failed to create refresh token", "error", err.Error())
		return "", "", err
	}

	err = u.tokeRepo.SaveSessionMeta(ctx, newJwtId, *meta, u.sessionTTL)
	if err != nil {
		u.logger.Warn("failed to save session meta", "error", err.Error())
		return "", "", err
	}

	err = u.tokeRepo.AddUserSession(ctx, *userID, newJwtId)
	if err != nil {
		u.logger.Warn("failed to add user session", "error", err.Error())
		return "", "", err
	}

	u.logger.Info("successfully refreshed user", "user", userID.String())
	return accessToken, refreshToken, nil
}

func (u *UserService) disconnection(ctx context.Context, claims security.Claims) error {
	// получаем все сессии
	sessions, err := u.tokeRepo.GetUserSessions(ctx, claims.UserID)
	if err != nil {
		u.logger.Error("Error getting user sessions", "error", err)
		return err
	}
	u.logger.Debug("disconnected users sessions", "count", len(sessions))

	// удаляем список сессий
	err = u.tokeRepo.RemoveAllUserSessions(ctx, claims.UserID)
	if err != nil {
		u.logger.Error("error removing user sessions", "error", err)
		return err
	}

	// перебираем каждую и отключаем
	for _, jwtID := range sessions {
		// удаляем все refresh токены
		err = u.tokeRepo.DeleteRefresh(ctx, jwtID)
		if err != nil {
			u.logger.Error("error deleting refresh", "error", err.Error())
		}

		// удаляем все мета о сессиях
		err = u.tokeRepo.DeleteSessionMeta(ctx, jwtID)
		if err != nil {
			u.logger.Error("error deleting session meta", "error", err.Error())
		}
	}

	u.logger.Debug("disconnected users sessions", "count", len(sessions))
	return nil
}
