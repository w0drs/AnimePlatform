package domain

import (
	"github.com/google/uuid"
)

const (
	Admin     = "admin"
	Moderator = "moder"
	Client    = "user"
)

type User struct {
	ID          uuid.UUID
	Login       string
	Email       string
	Password    string // plain password или hashed password в сервисном слое обычный пароль на хеш меняется (при регистрации)
	Description string
	FirstName   string
	IconUrl     string
	Role        string
}
