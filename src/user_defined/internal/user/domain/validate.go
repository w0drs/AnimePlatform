package domain

import (
	"net/mail"
	"net/url"

	coreHttp "kuronami/internal/core/http"
)

const (
	UsernameMinLength        = 4
	UsernameMaxLength        = 128
	UserPasswordMinLength    = 8
	UserPasswordMaxLength    = 512
	UserDescriptionMaxLength = 512
)

func ValidateUser(user *User) error {
	if user == nil {
		return coreHttp.NewValidationError("user", "user is nil")
	}

	if len(user.Login) < UsernameMinLength {
		return coreHttp.NewValidationError("username", "username is too short")
	}
	if len(user.Login) > UsernameMaxLength {
		return coreHttp.NewValidationError("username", "username is too long")
	}

	if len(user.FirstName) < UsernameMinLength {
		return coreHttp.NewValidationError("first name", "first name is too short")
	}
	if len(user.FirstName) > UsernameMaxLength {
		return coreHttp.NewValidationError("first name", "first name is too long")
	}
	if len(user.Description) > UserDescriptionMaxLength {
		return coreHttp.NewValidationError("description", "description is too long")
	}

	if _, err := mail.ParseAddress(user.Email); err != nil {
		return coreHttp.NewValidationError("email", "email is invalid")
	}

	_, err := url.Parse(user.IconUrl)
	if err != nil {
		return coreHttp.NewValidationError("icon_url", "icon_url is invalid")
	}

	if len(user.Password) < UserPasswordMinLength {
		return coreHttp.NewValidationError("user password", "password is too short")
	}
	if len(user.Password) > UserPasswordMaxLength {
		return coreHttp.NewValidationError("user password", "password is too long")
	}

	return nil
}
