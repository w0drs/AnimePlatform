package redis

import (
	"fmt"
	"github.com/google/uuid"
)

func refreshKey(jti uuid.UUID) string {
	return fmt.Sprintf("refresh:%s", jti.String())
}

func sessionMetaKey(jti uuid.UUID) string {
	return fmt.Sprintf("session_meta:%s", jti.String())
}

func userSessionsKey(userID uuid.UUID) string {
	return fmt.Sprintf("user:%s:sessions", userID.String())
}
