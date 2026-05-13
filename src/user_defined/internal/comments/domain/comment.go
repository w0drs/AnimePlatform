package domain

import "github.com/google/uuid"

const DefaultCommentsPerPage = 15

type AnimeComment struct {
	ID           int
	Text         string
	UserID       uuid.UUID
	AnimeID      int
	TaggedUserID *uuid.UUID
}

type NewsComment struct {
	ID           int
	Text         string
	UserID       uuid.UUID
	NewsID       int
	TaggedUserID *uuid.UUID
}
