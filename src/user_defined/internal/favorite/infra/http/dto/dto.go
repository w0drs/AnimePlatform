package dto

import "kuronami/internal/favorite/domain"

type GetFavoritesResp struct {
	Favorites []*domain.Favorite `json:"favorites"`
}

type GetFavoriteResp struct {
	Favorite domain.Favorite `json:"favorite"`
}
