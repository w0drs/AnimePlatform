package http

import (
	"log/slog"
	"net/http"
)

type APIError struct {
	StatusCode int            `json:"-"`
	ErrorCode  string         `json:"error"`
	Details    map[string]any `json:"details,omitempty"`
}

func (e APIError) Error() string {
	return e.ErrorCode
}

var (
	// Общие ошибки

	ErrInternal = APIError{
		StatusCode: http.StatusInternalServerError,
		ErrorCode:  "INTERNAL_ERROR",
	}

	ErrUnauthorized = APIError{
		StatusCode: http.StatusUnauthorized,
		ErrorCode:  "UNAUTHORIZED",
	}

	ErrInvalidBody = APIError{
		StatusCode: http.StatusBadRequest,
		ErrorCode:  "INVALID_BODY",
	}
	ErrInvalidPathValue = APIError{
		StatusCode: http.StatusBadRequest,
		ErrorCode:  "INVALID_PATH_VALUE",
	}

	// User Error

	ErrUserNotFound = APIError{
		StatusCode: http.StatusNotFound,
		ErrorCode:  "USER_NOT_FOUND",
	}

	ErrUserAlreadyExists = APIError{
		StatusCode: http.StatusConflict,
		ErrorCode:  "USER_ALREADY_EXISTS",
	}
	ErrInvalidCredentials = APIError{
		StatusCode: http.StatusUnauthorized,
		ErrorCode:  "INVALID_CREDENTIALS",
	}

	ErrInvalidUserParams = APIError{
		StatusCode: http.StatusBadRequest,
		ErrorCode:  "INVALID_USER_PARAMS",
	}

	ErrVerificationFailed = APIError{
		StatusCode: http.StatusForbidden,
		ErrorCode:  "VERIFICATION_FAILED",
	}

	ErrPermissionDenied = APIError{
		StatusCode: http.StatusForbidden,
		ErrorCode:  "PERMISSION_DENIED",
	}

	// Token/Session Errors

	ErrTokenNotFound = APIError{
		StatusCode: http.StatusNotFound,
		ErrorCode:  "TOKEN_NOT_FOUND",
	}

	ErrTokenIsInvalid = APIError{
		StatusCode: http.StatusBadRequest,
		ErrorCode:  "TOKEN_IS_INVALID",
	}

	ErrSessionMetaNotFound = APIError{
		StatusCode: http.StatusNotFound,
		ErrorCode:  "SESSION_META_NOT_FOUND",
	}

	ErrFavoriteNotFound = APIError{
		StatusCode: http.StatusNotFound,
		ErrorCode:  "FAVORITE_ANIME_NOT_FOUND",
	}
)

func NewValidationError(field string, message string) APIError {
	return APIError{
		StatusCode: http.StatusBadRequest,
		ErrorCode:  "VALIDATION_ERROR",
		Details: map[string]any{
			"field":   field,
			"message": message,
		},
	}
}

func NewErrorWithDetails(err APIError, field string, message any) APIError {
	return APIError{
		StatusCode: err.StatusCode,
		ErrorCode:  err.ErrorCode,
		Details:    map[string]any{field: message},
	}
}

func SendErrorJSON(logger *slog.Logger, w http.ResponseWriter, apiErr *APIError) {
	SendJSON(logger, w, apiErr, apiErr.StatusCode)
}
