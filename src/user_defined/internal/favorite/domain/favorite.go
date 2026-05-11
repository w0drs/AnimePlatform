package domain

import "github.com/google/uuid"

type Favorite struct {
	UserID  uuid.UUID
	AnimeID int
}
