package handlers

import (
	"errors"
	"github.com/google/uuid"
	"kuronami/internal/comments/domain"
	"kuronami/internal/comments/infra/http/dto"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/middleware"
	"net/http"
	"strconv"
	"time"
)

func (h *CommentsHandlers) AddAnimeComment(w http.ResponseWriter, r *http.Request) {
	claims, err := middleware.GetClaimsFromContext(r.Context())
	if err != nil {
		h.logger.Warn("user is unauthorized")
		coreHttp.SendErrorJSON(h.logger, w, &coreHttp.ErrUnauthorized)
		return
	}
	animeID, err := strconv.Atoi(r.PathValue("anime_id"))
	if err != nil {
		h.logger.Warn("anime_id is invalid")
		validErr := coreHttp.NewValidationError("anime_id", "anime_id is invalid")
		coreHttp.SendErrorJSON(h.logger, w, &validErr)
		return
	}

	var req dto.AddAnimeCommentRequest
	if errBody := coreHttp.ParseJSONBody(h.logger, r, &req); errBody != nil {
		h.logger.Warn("invalid body", "error", errBody.Error())
		coreHttp.SendErrorJSON(h.logger, w, errBody)
		return
	}
	if animeID != req.AnimeID {
		h.logger.Warn("anime_id is invalid")
		validErr := coreHttp.NewValidationError("anime_id", "anime_id is invalid")
		coreHttp.SendErrorJSON(h.logger, w, &validErr)
		return
	}

	var taggedUserID *uuid.UUID
	if req.TaggedUserID != "" {
		uuidParse, err := uuid.Parse(req.TaggedUserID)
		if err != nil {
			h.logger.Warn("invalid tagged user id", "tagged_user_id", req.TaggedUserID, "error", err.Error())
			apiErr := coreHttp.NewValidationError("tagged_user_id", "invalid uuid format")
			coreHttp.SendErrorJSON(h.logger, w, &apiErr)
			return
		}
		taggedUserID = &uuidParse
	}

	newComment, err := h.comServ.AddAnimeComment(r.Context(), domain.AnimeComment{
		Text:         req.Text,
		UserID:       claims.UserID,
		AnimeID:      req.AnimeID,
		TaggedUserID: taggedUserID,
	})
	if err != nil {
		h.logger.Debug("error adding comment", "error", err.Error())
		var apiErr coreHttp.APIError
		if errors.As(err, &apiErr) {
			coreHttp.SendErrorJSON(h.logger, w, &apiErr)
			return
		}
		coreHttp.SendErrorJSON(h.logger, w, &coreHttp.ErrInternal)
		return
	}

	var taggedUserIDStr string
	if newComment.TaggedUserID != nil {
		taggedUserIDStr = newComment.TaggedUserID.String()
	}
	response := dto.AddAnimeCommentResponse{
		ID:           newComment.ID,
		Text:         newComment.Text,
		UserID:       newComment.UserID.String(),
		AnimeID:      newComment.AnimeID,
		TaggedUserID: taggedUserIDStr,
		CreatedAt:    newComment.CreatedAt.Format(time.RFC3339),
	}
	coreHttp.SendJSON(h.logger, w, response, http.StatusCreated)
	h.logger.Debug("anime comment added", "id", newComment.ID)
}

func (h *CommentsHandlers) AddNewsComment(w http.ResponseWriter, r *http.Request) {
	claims, err := middleware.GetClaimsFromContext(r.Context())
	if err != nil {
		h.logger.Debug("user is unauthorized")
		coreHttp.SendErrorJSON(h.logger, w, &coreHttp.ErrUnauthorized)
		return
	}

	newsID, err := strconv.Atoi(r.PathValue("news_id"))
	if err != nil {
		h.logger.Warn("news_id is invalid")
		validErr := coreHttp.NewValidationError("news_id", "news_id is invalid")
		coreHttp.SendErrorJSON(h.logger, w, &validErr)
		return
	}

	var req dto.AddNewsCommentRequest
	if errBody := coreHttp.ParseJSONBody(h.logger, r, &req); errBody != nil {
		h.logger.Warn("invalid body", "error", errBody.Error())
		coreHttp.SendErrorJSON(h.logger, w, errBody)
		return
	}
	if newsID != req.NewsID {
		h.logger.Warn("newsID is invalid")
		validErr := coreHttp.NewValidationError("newsID", "newsID is invalid")
		coreHttp.SendErrorJSON(h.logger, w, &validErr)
		return
	}

	var taggedUserID *uuid.UUID
	if req.TaggedUserID != "" {
		uuidParse, err := uuid.Parse(req.TaggedUserID)
		if err != nil {
			h.logger.Warn("invalid tagged user id", "tagged_user_id", req.TaggedUserID, "error", err.Error())
			apiErr := coreHttp.NewValidationError("tagged_user_id", "invalid uuid format")
			coreHttp.SendErrorJSON(h.logger, w, &apiErr)
			return
		}
		taggedUserID = &uuidParse
	}

	newComment, err := h.comServ.AddNewsComment(r.Context(), domain.NewsComment{
		Text:         req.Text,
		UserID:       claims.UserID,
		NewsID:       req.NewsID,
		TaggedUserID: taggedUserID,
	})
	if err != nil {
		h.logger.Debug("error adding comment", "error", err.Error())
		var apiErr coreHttp.APIError
		if errors.As(err, &apiErr) {
			coreHttp.SendErrorJSON(h.logger, w, &apiErr)
			return
		}
		coreHttp.SendErrorJSON(h.logger, w, &coreHttp.ErrInternal)
		return
	}

	var taggedUserIDStr string
	if newComment.TaggedUserID != nil {
		taggedUserIDStr = newComment.TaggedUserID.String()
	}
	response := dto.AddNewsCommentResponse{
		ID:           newComment.ID,
		Text:         newComment.Text,
		UserID:       newComment.UserID.String(),
		NewsID:       newComment.NewsID,
		TaggedUserID: taggedUserIDStr,
		CreatedAt:    newComment.CreatedAt.Format(time.RFC3339),
	}
	coreHttp.SendJSON(h.logger, w, response, http.StatusCreated)
	h.logger.Debug("news comment added", "id", newComment.ID)
}
