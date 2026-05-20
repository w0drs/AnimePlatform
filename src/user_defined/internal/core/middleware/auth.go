package middleware

import (
	"context"
	"fmt"
	"github.com/go-redis/redis/v8"
	"github.com/google/uuid"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/security"
	"log/slog"
	"net/http"
	"strings"
)

type claimsContextKey struct {
	name string
}

var ClaimsContextKey = claimsContextKey{name: "claims"}

func AuthMiddleware(logger *slog.Logger, authService *security.JWT, pool *redis.Client) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			authHeader := r.Header.Get("Authorization")
			if authHeader == "" {
				apiErr := coreHttp.NewErrorWithDetails(coreHttp.ErrUnauthorized,
					"authorization", "authorization header is missing")
				coreHttp.SendErrorJSON(logger, w, &apiErr)
				return
			}

			parts := strings.Split(authHeader, " ")
			if len(parts) != 2 || parts[0] != "Bearer" {
				apiErr := coreHttp.NewErrorWithDetails(coreHttp.ErrUnauthorized,
					"authorization", "authorization header is invalid")
				coreHttp.SendErrorJSON(logger, w, &apiErr)
				return
			}

			token := parts[1]

			claims, err := authService.ParseToken(token)
			if err != nil {
				logger.Error("error parsing token", "error", err.Error())
				apiErr := coreHttp.NewErrorWithDetails(coreHttp.ErrUnauthorized,
					"authorization", "invalid or expired token")
				coreHttp.SendErrorJSON(logger, w, &apiErr)
				return
			}

			exists, err := pool.Exists(r.Context(), refreshKey(claims.JwtID)).Result()
			if err != nil {
				logger.Error("check token existence failed", "jti", claims.JwtID.String(), "error", err.Error())
				apiErr := coreHttp.NewErrorWithDetails(coreHttp.ErrUnauthorized,
					"authorization", "invalid or expired token")
				coreHttp.SendErrorJSON(logger, w, &apiErr)
				return
			}
			if exists == 0 {
				apiErr := coreHttp.NewErrorWithDetails(coreHttp.ErrUnauthorized,
					"authorization", "invalid or expired token")
				coreHttp.SendErrorJSON(logger, w, &apiErr)
				return
			}

			ctx := context.WithValue(r.Context(), ClaimsContextKey, claims)
			next.ServeHTTP(w, r.WithContext(ctx))
		})
	}
}

// GetClaimsFromContext - возвращает claims пользователя
func GetClaimsFromContext(ctx context.Context) (*security.Claims, error) {
	user, ok := ctx.Value(ClaimsContextKey).(*security.Claims)
	if !ok {
		return nil, fmt.Errorf("claims not found in context")
	}
	return user, nil
}

func refreshKey(jti uuid.UUID) string {
	return fmt.Sprintf("refresh:%s", jti.String())
}
