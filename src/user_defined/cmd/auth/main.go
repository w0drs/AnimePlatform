package main

import (
	"context"
	"kuronami/internal/core/di"
	pkg "kuronami/internal/core/pkg/logger"
	"kuronami/internal/core/pkg/utils"
)

func main() {
	ctx := context.Background()

	logLevel := utils.GetEnv("LOG_LEVEL", "info")
	logFile, logs := pkg.NewSlogLogger(logLevel)
	defer func() {
		if err := logFile.Close(); err != nil {
			logs.Error("error closing log file")
		}
	}()

	app := di.NewAuthApp(ctx, logs)
	if err := app.Start(ctx); err != nil {
		logs.Error("server error", "error", err.Error())
	}
	logs.Info("server stopped")
}
