package dto

import "kuronami/internal/comments/domain"

type AddAnimeCommentRequest struct {
	Text         string `json:"text"`
	AnimeID      int    `json:"anime_id"`
	TaggedUserID string `json:"tagged_user_id,omitempty"`
}

type AddNewsCommentRequest struct {
	Text         string `json:"text"`
	NewsID       int    `json:"news_id"`
	TaggedUserID string `json:"tagged_user_id,omitempty"`
}

type AddAnimeCommentResponse struct {
	ID           int    `json:"id"`
	Text         string `json:"text"`
	UserID       string `json:"user_id"`
	AnimeID      int    `json:"anime_id"`
	TaggedUserID string `json:"tagged_user_id,omitempty"`
	CreatedAt    string `json:"created_at"`
}

type AddNewsCommentResponse struct {
	ID           int    `json:"id"`
	Text         string `json:"text"`
	UserID       string `json:"user_id"`
	NewsID       int    `json:"news_id"`
	TaggedUserID string `json:"tagged_user_id,omitempty"`
	CreatedAt    string `json:"created_at"`
}

type GetAnimeCommentsResponse struct {
	Comments []*domain.AnimeComment `json:"comments"`
}

type GetNewsCommentsResponse struct {
	Comments []*domain.NewsComment `json:"comments"`
}
