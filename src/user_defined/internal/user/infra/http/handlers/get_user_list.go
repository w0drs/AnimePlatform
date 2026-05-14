package handlers

import (
	"errors"
	"github.com/google/uuid"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/user/domain"
	"kuronami/internal/user/infra/http/dto"
	"net/http"
)

func (a *AuthHandlers) GetUserList(w http.ResponseWriter, r *http.Request) {
	// Парсим тело запроса
	var req dto.GetUserListRequest
	err := coreHttp.ParseJSONBody(a.logger, r, &req)
	if err != nil {
		a.logger.Warn("get user list body invalid", "error", err.Error())
		coreHttp.SendErrorJSON(a.logger, w, err)
		return
	}

	// Если тело было пустым возвращаем пустой список
	if len(req.UserIDs) == 0 {
		a.logger.Debug("get user list called with empty ids")
		coreHttp.SendJSON(a.logger, w, &dto.GetUserListResponse{
			Users: []domain.User{},
		}, http.StatusOK)
		return
	}

	var userList []uuid.UUID
	var failedIDs []string

	// Парсим id которые в запросе были
	for _, id := range req.UserIDs {
		userIDParsed, err := uuid.Parse(id)
		if err != nil {
			a.logger.Warn("failed to parse user uuid", "user_id", id, "error", err.Error())
			failedIDs = append(failedIDs, id)
			continue
		}
		userList = append(userList, userIDParsed)
	}

	// Если после парсинга список пуст, это проблема
	if len(userList) == 0 {
		a.logger.Warn("no valid user ids provided", "invalid_ids", failedIDs)
		validateErr := coreHttp.NewValidationError("user_ids", "no valid user IDs provided")
		coreHttp.SendErrorJSON(a.logger, w, &validateErr)
		return
	}

	// Передаем список id на получение пользователей
	users, errL := a.userService.GetUserList(r.Context(), userList)
	if errL != nil {
		a.logger.Debug("fail to get user list", "err", errL.Error())
		var apiErr coreHttp.APIError
		if errors.As(errL, &apiErr) {
			coreHttp.SendErrorJSON(a.logger, w, &apiErr)
			return
		}
		coreHttp.SendErrorJSON(a.logger, w, &coreHttp.ErrInternal)
		return
	}

	// Ответ
	coreHttp.SendJSON(a.logger, w, &dto.GetUserListResponse{
		Users: users,
	}, http.StatusOK)
	a.logger.Debug("success get user list", "users len", len(users))
	return
}
