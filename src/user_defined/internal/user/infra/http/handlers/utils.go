package handlers

import (
	"github.com/mssola/user_agent"
	"kuronami/internal/user/domain"
	"net"
	"net/http"
	"strings"
)

func ExtractSessionMeta(r *http.Request) domain.SessionMeta {
	ip := getClientIP(r)

	userAgentString := r.UserAgent()

	device := parseUserAgent(userAgentString)

	return domain.SessionMeta{
		IP:        ip,
		Device:    device,
		UserAgent: userAgentString,
	}
}

// getClientIP получает реальный IP клиента (учитывая прокси)
func getClientIP(r *http.Request) string {
	// Проверяем X-Forwarded-For (если за прокси)
	if xff := r.Header.Get("X-Forwarded-For"); xff != "" {
		// X-Forwarded-For может содержать несколько IP: client, proxy1, proxy2
		ips := strings.Split(xff, ",")
		if len(ips) > 0 {
			return strings.TrimSpace(ips[0]) // первый - реальный IP клиента
		}
	}

	// Проверяем X-Real-IP (nginx часто добавляет)
	if xri := r.Header.Get("X-Real-IP"); xri != "" {
		return strings.TrimSpace(xri)
	}

	// Если прокси нет - берем RemoteAddr
	ip := r.RemoteAddr

	// Удаляем порт если есть (RemoteAddr часто приходит как "192.168.1.100:54321")
	if host, _, err := net.SplitHostPort(ip); err == nil {
		ip = host
	}

	return ip
}

// parseUserAgent парсит User-Agent в читаемое название устройства/браузера
func parseUserAgent(userAgentString string) string {
	ua := user_agent.New(userAgentString)

	name, version := ua.Browser()

	// Формируем название устройства
	device := ""

	// Определяем тип устройства
	if ua.Mobile() {
		device = "Mobile - "
	} else if ua.Bot() {
		device = "Bot - "
	} else {
		device = ""
	}

	// Добавляем браузер
	if name != "" {
		device += name
		if version != "" {
			device += " " + version
		}
	} else {
		device += "Unknown Browser"
	}

	// Добавляем ОС
	os := ua.OS()
	if os != "" {
		device += " on " + os
	}

	return device
}
