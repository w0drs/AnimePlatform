package security

import (
	"fmt"
	"github.com/google/uuid"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

type JWT struct {
	secretKey string
	accessTTL time.Duration
	// defRefreshTTL - обычный refresh duration (8-10 часов)
	defRefreshTTL time.Duration
	// remRefreshTTL - refresh при использовании юзером `флажка запомнить меня` - 14 дней например
	remRefreshTTL time.Duration
}

func NewJWTService(secretKey string, accessTTL, defRefreshTTL, remRefreshTTL time.Duration) *JWT {
	return &JWT{
		secretKey:     secretKey,
		accessTTL:     accessTTL,
		defRefreshTTL: defRefreshTTL,
		remRefreshTTL: remRefreshTTL,
	}
}

type Claims struct {
	JwtID  uuid.UUID `json:"jwt_id"`
	UserID uuid.UUID `json:"user_id"`
	Email  string    `json:"email"`
	Role   string    `json:"role"`
	jwt.RegisteredClaims
}

func (j *JWT) GenerateAccessToken(jwtID, userID uuid.UUID, email, role string) (string, error) {
	claims := Claims{
		UserID: userID,
		Email:  email,
		Role:   role,
		JwtID:  jwtID,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(j.accessTTL)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(j.secretKey))
}

func (j *JWT) GenerateRefreshToken(jwtID, userID uuid.UUID, email, role string, remember bool) (string, error) {
	refreshTTL := j.defRefreshTTL
	if remember {
		refreshTTL = j.remRefreshTTL
	}

	claims := Claims{
		UserID: userID,
		Email:  email,
		Role:   role,
		JwtID:  jwtID,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(refreshTTL)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(j.secretKey))
}

func (j *JWT) ParseToken(tokenString string) (*Claims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return []byte(j.secretKey), nil
	})

	if err != nil {
		return nil, err
	}

	if claims, ok := token.Claims.(*Claims); ok && token.Valid {
		return claims, nil
	}

	return nil, fmt.Errorf("invalid token")
}
