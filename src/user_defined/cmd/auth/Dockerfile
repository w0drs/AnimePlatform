FROM golang:alpine AS builder

WORKDIR /app

RUN apk add --no-cache git make

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN go build -o /app/bin/auth ./cmd/auth


FROM alpine:latest

WORKDIR /app

RUN apk --no-cache add ca-certificates

COPY --from=builder /app/bin/auth /app/auth

EXPOSE 16767

CMD ["/app/auth"]
