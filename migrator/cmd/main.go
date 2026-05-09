package main

import (
	"kuronami-migrate/migration"
	"kuronami-migrate/pkg"
)

func main() {
	dsnPattern := pkg.GetEnv("POSTGRES_DSN_PATTERN", "POSTGRES_DSN")
	logFile, logger := pkg.NewSlogLogger("debug")
	defer logFile.Close()

	dsns := pkg.GetDSNsByPattern(dsnPattern)
	if len(dsns) == 0 {
		logger.Error("No valid DSNs found")
		return
	}
	logger.Debug("DSNs: ", "len", len(dsns))
	for i, dsn := range dsns {
		normalizedDSN := pkg.NormalizeDSN(dsn)
		logger.Debug("Migration", "i", i, "dsn", normalizedDSN)
		err := migration.Migrate(normalizedDSN)
		if err != nil {
			logger.Error("Migration", "i", i, "dsn", normalizedDSN, "message", "migration failed", "err", err.Error())
		} else {
			logger.Info("Migration", "i", i, "dsn", normalizedDSN, "message", "migration success")
		}
	}

	logger.Debug("Migration finished")
}
