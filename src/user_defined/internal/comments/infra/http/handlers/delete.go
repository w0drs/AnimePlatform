package handlers

import (
	"errors"
	coreHttp "kuronami/internal/core/http"
	"kuronami/internal/core/middleware"
	domainUser "kuronami/internal/user/domain"
	"net/http"
	"strconv"
)

func (h *CommentsHandlers) DeleteAnimeComments(w http.ResponseWriter, r *http.Request) {
	claims, err := middleware.GetClaimsFromContext(r.Context())
	if err != nil {
		h.logger.Warn("user is unauthorized")
		coreHttp.SendErrorJSON(h.logger, w, &coreHttp.ErrUnauthorized)
		return
	}

	commentIDStr := r.PathValue("comment_id")
	commentID, err := strconv.Atoi(commentIDStr)
	if err != nil {
		h.logger.Warn("invalid comment id", "comment_id", commentIDStr)
		coreHttp.SendErrorJSON(h.logger, w, &coreHttp.ErrInvalidPathValue)
		return
	}

	err = h.comServ.DeleteAnimeComment(r.Context(), domainUser.User{
		ID:    claims.UserID,
		Email: claims.Email,
		Role:  claims.Role,
	}, commentID)

	if err != nil {
		h.logger.Debug("error deleting anime comment", "commentID", commentID, "userID", claims.UserID.String(),
			"role", claims.Role, "error", err.Error())
		var apiErr coreHttp.APIError
		if errors.As(err, &apiErr) {
			coreHttp.SendErrorJSON(h.logger, w, &apiErr)
			return
		}
		coreHttp.SendErrorJSON(h.logger, w, &coreHttp.ErrInternal)
		return
	}

	w.WriteHeader(http.StatusNoContent)
	h.logger.Debug("deleted anime comment", "commentID", commentID, "userID", claims.UserID.String())
}

func (h *CommentsHandlers) DeleteNewsComments(w http.ResponseWriter, r *http.Request) {
	claims, err := middleware.GetClaimsFromContext(r.Context())
	if err != nil {
		h.logger.Warn("user is unauthorized")
		coreHttp.SendErrorJSON(h.logger, w, &coreHttp.ErrUnauthorized)
		return
	}

	commentIDStr := r.PathValue("comment_id")
	commentID, err := strconv.Atoi(commentIDStr)
	if err != nil {
		h.logger.Warn("invalid comment id")
		coreHttp.SendErrorJSON(h.logger, w, &coreHttp.ErrInvalidPathValue)
		return
	}

	err = h.comServ.DeleteNewsComment(r.Context(), domainUser.User{
		ID:    claims.UserID,
		Email: claims.Email,
		Role:  claims.Role,
	}, commentID)

	if err != nil {
		h.logger.Debug("error deleting news comment", "commentID", commentID, "userID", claims.UserID.String(),
			"role", claims.Role, "error", err.Error())
		var apiErr coreHttp.APIError
		if errors.As(err, &apiErr) {
			coreHttp.SendErrorJSON(h.logger, w, &apiErr)
			return
		}
		coreHttp.SendErrorJSON(h.logger, w, &coreHttp.ErrInternal)
		return
	}

	w.WriteHeader(http.StatusNoContent)
	h.logger.Debug("deleted news comment", "commentID", commentID, "userID", claims.UserID.String())
}
