package handlers

import (
	"errors"
	"kuronami/internal/comments/infra/http/dto"
	coreHttp "kuronami/internal/core/http"
	"net/http"
	"strconv"
)

func (h *CommentsHandlers) GetAnimeComments(w http.ResponseWriter, r *http.Request) {
	animeIDStr := r.PathValue("anime_id")
	animeID, err := strconv.Atoi(animeIDStr)
	if err != nil {
		h.logger.Warn("invalid anime id", "anime_id", animeIDStr)
		coreHttp.SendErrorJSON(h.logger, w, &coreHttp.ErrInvalidPathValue)
		return
	}
	pageStr := r.URL.Query().Get("page")
	page, err := strconv.Atoi(pageStr)
	if err != nil || page <= 0 {
		if err != nil {
			h.logger.Debug("invalid page number, using default", "page", pageStr, "error", err)
		} else {
			h.logger.Debug("page <= 0, using default", "page", page)
		}
		page = 1
	}

	comments, err := h.comServ.GetAnimeComments(r.Context(), animeID, page)
	if err != nil {
		h.logger.Debug("get anime comment failed", "animeID", animeID, "page", page)
		var apiErr coreHttp.APIError
		if errors.As(err, &apiErr) {
			coreHttp.SendErrorJSON(h.logger, w, &apiErr)
			return
		}
		coreHttp.SendErrorJSON(h.logger, w, &coreHttp.ErrInternal)
		return
	}

	coreHttp.SendJSON(h.logger, w, dto.GetAnimeCommentsResponse{Comments: comments}, http.StatusOK)
	h.logger.Debug("anime comments get", "comments len", len(comments))
}

func (h *CommentsHandlers) GetNewsComments(w http.ResponseWriter, r *http.Request) {
	newsIDStr := r.PathValue("news_id")
	newsID, err := strconv.Atoi(newsIDStr)
	if err != nil {
		h.logger.Warn("invalid news id", "news_id", newsIDStr)
		coreHttp.SendErrorJSON(h.logger, w, &coreHttp.ErrInvalidPathValue)
		return
	}
	pageStr := r.URL.Query().Get("page")
	page, err := strconv.Atoi(pageStr)
	if err != nil || page <= 0 {
		if err != nil {
			h.logger.Debug("invalid page number, using default", "page", pageStr, "error", err)
		} else {
			h.logger.Debug("page <= 0, using default", "page", page)
		}
		page = 1
	}

	comments, err := h.comServ.GetNewsComments(r.Context(), newsID, page)
	if err != nil {
		h.logger.Debug("get news comment failed", "newsID", newsID, "page", page)
		var apiErr coreHttp.APIError
		if errors.As(err, &apiErr) {
			coreHttp.SendErrorJSON(h.logger, w, &apiErr)
			return
		}
		coreHttp.SendErrorJSON(h.logger, w, &coreHttp.ErrInternal)
		return
	}

	coreHttp.SendJSON(h.logger, w, dto.GetNewsCommentsResponse{Comments: comments}, http.StatusOK)
	h.logger.Debug("news comments get", "comments len", len(comments))
}
