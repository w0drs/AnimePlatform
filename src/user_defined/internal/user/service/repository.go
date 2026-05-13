package service

import (
	"context"
	"github.com/google/uuid"
	"kuronami/internal/user/domain"
	"time"
)

type UserRepository interface {
	// Create создает пользователя
	// Приходит Login, Email, Password, FirstName, IconURL, возвращает это только добавляется ID и Role
	Create(ctx context.Context, user *domain.User) (*domain.User, error)

	// GetByID - получение пользователя по ID
	GetByID(ctx context.Context, userID uuid.UUID) (*domain.User, error)
	// GetByEmail - получение пользователя по Email
	GetByEmail(ctx context.Context, email string) (*domain.User, error)
	// GetByLogin - получение пользователя по login
	GetByLogin(ctx context.Context, login string) (*domain.User, error)
	// GetByUserIDList - получает список пользователей по списку UUID (для агрегации на фронте надо)
	GetByUserIDList(ctx context.Context, userIDList []uuid.UUID) ([]domain.User, error)

	// ChangePassword - меняет пароль у пользователя
	ChangePassword(ctx context.Context, userID uuid.UUID, new string) error
	// Update - обновляет данные пользователя (без пароля)
	Update(ctx context.Context, user *domain.User) (*domain.User, error)

	// Deactivate - переводит аккаунт в состояние неактивного, меняется поле is_active на false, сама запись остается
	Deactivate(ctx context.Context, userID uuid.UUID) error
}

type TokenRepository interface {
	// CreateRefresh создает refresh маркер (jti -> userID)
	// Применяется при логине и после успешной ротации
	CreateRefresh(ctx context.Context, jti uuid.UUID, userID uuid.UUID, ttl time.Duration) error

	// GetUserIDByRefresh проверяет существование refresh токена и возвращает userID
	// Если ключа нет - значит токен уже использован (попытка взлома) или истек
	GetUserIDByRefresh(ctx context.Context, jti uuid.UUID) (*uuid.UUID, error)

	// DeleteRefresh удаляет refresh маркер
	// Применяется при logout, отзыве сессии, или после использования в ротации
	DeleteRefresh(ctx context.Context, jti uuid.UUID) error

	// SaveSessionMeta сохраняет метаданные сессии (устройство, ip и т.д.)
	SaveSessionMeta(ctx context.Context, jti uuid.UUID, meta domain.SessionMeta, ttl time.Duration) error

	// GetSessionMeta получает метаданные сессии
	GetSessionMeta(ctx context.Context, jti uuid.UUID) (*domain.SessionMeta, error)

	// UpdateSessionMeta обновляет ip и время последней активности
	UpdateSessionMeta(ctx context.Context, jti uuid.UUID, ip string) error

	// DeleteSessionMeta удаляет метаданные сессии
	DeleteSessionMeta(ctx context.Context, jti uuid.UUID) error

	// AddUserSession добавляет jti в список сессий пользователя
	AddUserSession(ctx context.Context, userID uuid.UUID, jti uuid.UUID) error

	// GetUserSessions возвращает все jti сессий пользователя
	GetUserSessions(ctx context.Context, userID uuid.UUID) ([]uuid.UUID, error)

	// RemoveUserSession удаляет jti из списка сессий пользователя
	RemoveUserSession(ctx context.Context, userID uuid.UUID, jti uuid.UUID) error

	// RemoveAllUserSessions удаляет все сессии пользователя
	RemoveAllUserSessions(ctx context.Context, userID uuid.UUID) error
}
