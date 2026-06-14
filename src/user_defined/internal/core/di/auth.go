package di

import (
	"context"
	"errors"
	"fmt"
	comHandlers "kuronami/internal/comments/infra/http/handlers"
	comRouter "kuronami/internal/comments/infra/http/router"
	comPG "kuronami/internal/comments/infra/postgres"
	comService "kuronami/internal/comments/service"
	"kuronami/internal/core/middleware"
	"kuronami/internal/core/pkg/closer"
	"kuronami/internal/core/pkg/utils"
	"kuronami/internal/core/postgres"
	redis2 "kuronami/internal/core/redis"
	"kuronami/internal/core/security"
	favHandlers "kuronami/internal/favorite/infra/http/handlers"
	favRouter "kuronami/internal/favorite/infra/http/router"
	favPG "kuronami/internal/favorite/infra/postgres"
	favService "kuronami/internal/favorite/service"
	"kuronami/internal/user/infra/http/handlers"
	"kuronami/internal/user/infra/http/router"
	userPG "kuronami/internal/user/infra/postgres"
	"kuronami/internal/user/infra/redis"
	"kuronami/internal/user/service"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
)

type AuthApp struct {
	logger *slog.Logger
	server *http.Server
	clsr   *closer.Closer
}

func NewAuthApp(ctx context.Context, logger *slog.Logger) *AuthApp {
	serverEndpoint := utils.GetEnv("SERVER_ENDPOINT", ":8002")
	postgresDSN := utils.GetEnv("USER_POSTGRES_DSN", "")
	redisDSN := utils.GetEnv("USER_REDIS_ENDPOINT", "")
	redisPass := utils.GetEnv("USER_REDIS_PASS", "redis")
	jwtSecret := utils.GetEnv("JWT_SECRET", "jwt-secret")
	accessTTL := utils.GetEnv("ACCESS_TTL", "10m")
	refreshTTL := utils.GetEnv("REFRESH_TTL", "7h")
	rememberTTL := utils.GetEnv("REMEMBER_TTL", "96h")
	sessionTTL := utils.GetEnv("SESSION_TTL", "24h")
	if serverEndpoint == "" {
		logger.Warn("No environment variable set for server")
		return nil
	}
	if postgresDSN == "" || redisDSN == "" {
		logger.Warn("User environment variables not set", "postgresDSN len", len(postgresDSN), "redisDSN len", len(redisDSN))
		return nil
	}
	accessTTLParsed, err := time.ParseDuration(accessTTL)
	if err != nil {
		logger.Warn("User access TTL parsing failed", "error", err.Error())
		return nil
	}
	refreshTTLParsed, err := time.ParseDuration(refreshTTL)
	if err != nil {
		logger.Warn("User refresh TTL parsing failed", "error", err.Error())
	}
	rememberTTLParsed, err := time.ParseDuration(rememberTTL)
	if err != nil {
		logger.Warn("User remember TTL parsing failed", "error", err.Error())
		return nil
	}
	sessionTTLParsed, err := time.ParseDuration(sessionTTL)
	if err != nil {
		logger.Warn("User session TTL parsing failed", "error", err.Error())
		return nil
	}
	clsr := closer.NewCloser(logger)

	pool, err := postgres.Open(ctx, postgresDSN)
	if err != nil {
		logger.Warn("Postgres pool open failed", "error", err.Error())
		return nil
	}
	clsr.AddFunc("postgres", pool.Close)
	redisPool, err := redis2.Open(ctx, redisDSN, redisPass)
	if err != nil {
		logger.Warn("Redis pool open failed", "error", err.Error())
		return nil
	}
	clsr.Add("redis", func(_ context.Context) error {
		return redisPool.Close()
	})
	//// Auth //////////////////////////////////////////////////////////////////////////////////////////////////////////
	userRepo := userPG.NewUserRepo(logger, pool)
	tokenRepo := redis.NewTokenRepository(logger, redisPool)
	jwt := security.NewJWTService(jwtSecret, accessTTLParsed, refreshTTLParsed, rememberTTLParsed)

	userService := service.NewUserService(logger, userRepo, tokenRepo, jwt, sessionTTLParsed)
	userHandlers := handlers.NewAuthHandlers(logger, userService, jwt)

	muxUserDefined := router.GetAuthRouter(logger, userHandlers, jwt, redisPool)
	////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

	/// Favorites //////////////////////////////////////////////////////////////////////////////////////////////////////
	favRepo := favPG.NewFavoritePG(logger, pool)
	favServ := favService.NewFavoriteService(logger, favRepo)
	favHandles := favHandlers.NewFavoriteHandler(logger, favServ)
	favRoutes := favRouter.FavoriteRouter(logger, favHandles, jwt, redisPool)

	favRoutes.Handle("/", muxUserDefined)
	////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

	/// Comments ///////////////////////////////////////////////////////////////////////////////////////////////////////
	comRepo := comPG.NewCommentsPG(logger, pool)
	comServ := comService.NewCommentService(logger, comRepo)
	comHandles := comHandlers.NewCommentsHandlers(logger, comServ)
	comRoutes := comRouter.CommentsRouter(logger, comHandles, jwt, redisPool)

	comRoutes.Handle("/", favRoutes)
	////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	// Logging middleware
	loggingMux := http.NewServeMux()
	loggingMux.Handle("/", middleware.Logging(logger)(comRoutes))

	// Recovery middleware
	recoveryMux := http.NewServeMux()
	recoveryMux.Handle("/", middleware.Recovery(logger)(loggingMux))
	////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	server := &http.Server{
		Addr:    serverEndpoint,
		Handler: recoveryMux,
	}
	return &AuthApp{
		logger: logger,
		server: server,
		clsr:   clsr,
	}
}

func (app *AuthApp) Start(ctx context.Context) error {
	if app == nil {
		return errors.New("app is nil")
	}
	errChan := make(chan error, 11)

	go func() {
		errChan <- app.server.ListenAndServe()
	}()
	app.logger.Info("auth server started", "addr", app.server.Addr)

	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	select {
	case err := <-errChan:
		app.logger.Error("Server error", "error", err.Error())
	case sig := <-sigChan:
		app.logger.Warn("signal received", "signal", sig.String())
	}

	shutdownCtx, shutdownCancel := context.WithTimeout(ctx, 30*time.Second)
	defer shutdownCancel()

	if err := app.clsr.Close(shutdownCtx); err != nil && !errors.Is(err, context.DeadlineExceeded) {
		return fmt.Errorf("app graceful shutdown: %w", err)
	}

	app.logger.Info("shutdown hook finished")
	return nil
}
