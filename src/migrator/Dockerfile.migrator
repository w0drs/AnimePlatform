FROM golang:alpine

WORKDIR /app

RUN apk add --no-cache git make

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN go build -o /app/bin/migrator ./cmd/

CMD ["/app/bin/migrator"]