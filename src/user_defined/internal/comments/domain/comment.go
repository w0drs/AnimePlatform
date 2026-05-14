package domain

import (
	"github.com/google/uuid"
	"time"
)

const (
	DefaultCommentsPerPage = 15
	MaxPageSize            = 200
)

type AnimeComment struct {
	ID           int
	Text         string
	UserID       uuid.UUID
	AnimeID      int
	TaggedUserID *uuid.UUID

	CreatedAt time.Time
}

type NewsComment struct {
	ID           int
	Text         string
	UserID       uuid.UUID
	NewsID       int
	TaggedUserID *uuid.UUID

	CreatedAt time.Time
}
