package redis

import (
	"context"
	"github.com/go-redis/redis/v8"
)

func Open(ctx context.Context, endpoint string, password string) (*redis.Client, error) {
	client := redis.NewClient(&redis.Options{
		Addr:     endpoint,
		Password: password,
	})
	err := client.Ping(ctx)
	if err.Err() != nil {
		return nil, err.Err()
	}
	return client, nil
}
