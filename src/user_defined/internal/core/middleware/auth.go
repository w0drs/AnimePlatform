package middleware

import (
	"context"
	"fmt"
	"kuronami/internal/core/security"
	"net/http"
	"strings"
)

type claimsContextKey struct {
	name string
}

var ClaimsContextKey = claimsContextKey{name: "claims"}

func AuthMiddleware(authService *security.JWT) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			authHeader := r.Header.Get("Authorization")
			if authHeader == "" {
				http.Error(w, "authorization header required", http.StatusUnauthorized)
				return
			}

			parts := strings.Split(authHeader, " ")
			if len(parts) != 2 || parts[0] != "Bearer" {
				http.Error(w, "invalid authorization header format", http.StatusUnauthorized)
				return
			}

			token := parts[1]

			claims, err := authService.ParseToken(token)
			if err != nil {
				http.Error(w, "invalid or expired token", http.StatusUnauthorized)
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
