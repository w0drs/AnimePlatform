package pkg

import (
	"log/slog"
	"os"
	"strconv"
	"strings"
)

func GetEnv(key string, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}

func GetEnvAsBool(key string, defaultValue bool) bool {
	if valueStr := GetEnv(key, ""); valueStr != "" {
		if value, err := strconv.ParseBool(valueStr); err == nil {
			return value
		}
	}
	return defaultValue
}

func GetEnvAsInt(key string, defaultValue int) int {
	if valueStr := GetEnv(key, ""); valueStr != "" {
		if value, err := strconv.Atoi(valueStr); err == nil {
			return value
		}
	}
	return defaultValue
}

func CheckEnv(vars []string) (int, bool) {
	flag := true
	empties := make([]string, len(vars))
	for _, v := range vars {
		if v == "" {
			flag = false
			empties = append(empties, v)
		}
	}
	return len(empties), flag
}

func SlogLevelByString(logLevel string) slog.Level {
	switch logLevel {
	case "debug":
		return slog.LevelDebug
	case "info":
		return slog.LevelInfo
	case "warn":
		return slog.LevelWarn
	case "error":
		return slog.LevelError
	default:
		return slog.LevelInfo
	}
}

func GetDSNsByPattern(pattern string) []string {
	var dsnList []string

	for _, env := range os.Environ() {
		pair := strings.SplitN(env, "=", 2)
		key := pair[0]

		if strings.Contains(key, pattern) {
			dsnList = append(dsnList, pair[1])
		}
	}

	return dsnList
}

func NormalizeDSN(dsn string) string {
	if !strings.Contains(dsn, "sslmode=") {
		separator := "?"
		if strings.Contains(dsn, "?") {
			separator = "&"
		}
		dsn += separator + "sslmode=disable"
	}
	return dsn
}
