# Migrator
## Описание

Migration Tool - это часть проекта для автоматического применения миграций баз данных PostgreSQL. Она находит все DSN (Data Source Names) в переменных окружения по шаблону и применяет миграции к каждой базе данных.

## Утилита ищет все переменные окружения, содержащие подстроку DSN. Рекомендуемый формат:
```bash
export USERS_DATABASE_DSN="postgresql://user1:password@localhost:5432/users_db?sslmode=disable"
export NEWS_POSTGRES_DSN="postgresql://user2:password@192.168.1.10:5432/news_db?sslmode=disable"
export PG_DSN="postgresql://user3:password@192.168.3.160:5432/pg_db?sslmode=disable"
```

## Миграции находятся по пути migrator/migration/migrations в .sql формате
### формат файла: {timestamp}_{description}.up.sql
```text
20260509_210600_create_anime_tables.up.sql
20260510_210900_create_news_tables.up.sql
```
