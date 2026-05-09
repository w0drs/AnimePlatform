package service

import (
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/security"
)

func (u *UserService) GetClaims(accessToken string) (*security.Claims, error) {
	if accessToken == "" {
		u.logger.Warn("access token is empty")
		return nil, coreHttp.ErrInvalidCredentials
	}

	claims, err := u.jwt.ParseToken(accessToken)
	if err != nil {
		u.logger.Warn("access token is invalid")
		return nil, coreHttp.ErrInvalidCredentials
	}

	u.logger.Info("access token is valid", "userID", claims.UserID.String())
	return claims, nil
}
