package dto

import "kuronami/internal/favorite/domain"

type GetFavoritesResp struct {
	Favorites []*domain.Favorite `json:"favorites"`
}
