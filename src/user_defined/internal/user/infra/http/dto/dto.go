package dto

import "kuronami/internal/user/domain"

type LoginRequest struct {
	Email    string `json:"email"`
	Password string `json:"password"`
	Remember bool   `json:"remember"`
}

type LoginResponse struct {
	Token string `json:"access_token"`
}

type RegisterRequest struct {
	Login       string `json:"login"`
	Email       string `json:"email"`
	Password    string `json:"password"`
	Description string `json:"description"`
	FirstName   string `json:"first_name"`
	IconURL     string `json:"icon_url"`
}

type RegisterResponse struct {
	ID          string `json:"id"`
	Login       string `json:"login"`
	Email       string `json:"email"`
	Password    string `json:"password"`
	Description string `json:"description"`
	FirstName   string `json:"first_name"`
	IconUrl     string `json:"icon_url"`
	Role        string `json:"role"`
}

type ChangePassRequest struct {
	OldPassword string `json:"old_password"`
	NewPassword string `json:"new_password"`
}

type ChangePassResponse struct {
	Message string `json:"message"`
}

type RefreshResponse struct {
	Token string `json:"access_token"`
}

type CheckAuthRequest struct {
	Token string `json:"access_token"`
}

type CheckAuthResponse struct {
	UserID string `json:"user_id"`
	Email  string `json:"email"`
	Role   string `json:"role"`
}

type GetUserResponse struct {
	Login       string `json:"login"`
	Email       string `json:"email"`
	Description string `json:"description"`
	FirstName   string `json:"first_name"`
	IconUrl     string `json:"icon_url"`
}

type UpdateUserRequest struct {
	Description string `json:"description"`
	FirstName   string `json:"first_name"`
	IconUrl     string `json:"icon_url"`
}

type UpdateUserResponse struct {
	Message string `json:"message"`
}

type DeactivateUserResponse struct {
	Message string `json:"message"`
}

type GetSessionsResponse struct {
	Sessions []domain.SessionInfo `json:"sessions"`
}

type DeleteSessionResponse struct {
	Message string `json:"message"`
}

type LogoutResponse struct {
	Message string `json:"message"`
}
