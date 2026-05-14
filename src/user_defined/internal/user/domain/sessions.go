package domain

import (
	"github.com/google/uuid"
	"time"
)

// SessionMeta метаданные сессии (хранится в session_meta:{jti})
type SessionMeta struct {
	IP           string    `json:"ip"`
	Device       string    `json:"device"`        // "Yandex 26", "Chrome on Windows" и т.д.
	UserAgent    string    `json:"user_agent"`    // полный User-Agent
	LastActivity time.Time `json:"last_activity"` // время последнего запроса
}

// SessionInfo полная информация о сессии (для ответа клиенту)
type SessionInfo struct {
	JTI          uuid.UUID `json:"jti"`
	IP           string    `json:"ip"`
	Device       string    `json:"device"`
	LastActivity time.Time `json:"last_activity"`
}
