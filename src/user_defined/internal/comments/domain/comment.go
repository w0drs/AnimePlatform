package domain

import "github.com/google/uuid"

type AnimeComment struct {
	ID           int
	Text         string
	UserID       uuid.UUID
	AnimeID      int
	TaggedUserID uuid.UUID
	IsDeleted    bool
}
