package postgres

import (
	"context"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/user/domain"
)

func (r *UserRepo) GetByUserIDList(ctx context.Context, userIDList []uuid.UUID) ([]domain.User, error) {
	// проверка наполненности и очистка от дубликатов
	if len(userIDList) == 0 {
		r.logger.Debug("get users by ids called with empty list")
		return []domain.User{}, nil
	}
	uniqueIDs := removeDuplicates(userIDList)

	query := `SELECT id, login, email, description, hashed_password as password, first_name, icon_url, role
	FROM users 
	WHERE id = ANY($1::uuid[]) and is_active = true`

	rows, err := r.pool.Query(ctx, query, uniqueIDs)
	if err != nil {
		r.logger.Error("get users by ids failed", "error", err.Error())
		return nil, coreHttp.ErrInternal
	}
	defer rows.Close()

	users, err := pgx.CollectRows(rows, pgx.RowToStructByName[domain.User])
	if err != nil {
		r.logger.Error("collect users by ids failed", "error", err.Error())
		return nil, coreHttp.NewErrorWithDetails(coreHttp.ErrInternal, "error", err.Error())
	}

	r.logger.Debug("get users by ids", "len users", len(users))
	return users, nil
}

func removeDuplicates(ids []uuid.UUID) []uuid.UUID {
	seen := make(map[uuid.UUID]bool)
	result := make([]uuid.UUID, 0, len(ids))
	for _, id := range ids {
		if !seen[id] {
			seen[id] = true
			result = append(result, id)
		}
	}
	return result
}
