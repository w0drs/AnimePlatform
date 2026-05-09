package redis

import (
	"context"
	"github.com/go-redis/redis/v8"
)

func Open(ctx context.Context, endpoint string) (*redis.Client, error) {
	client := redis.NewClient(&redis.Options{
		Addr: endpoint,
	})
	err := client.Ping(ctx)
	if err.Err() != nil {
		return nil, err.Err()
	}
	return client, nil
}
