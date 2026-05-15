.PHONY: up down logs build shell-backend shell-db restart clean

## Start all services (detached)
up:
	docker compose up -d --build

## Start all services in the foreground (stream logs)
dev:
	docker compose up --build

## Stop all services
down:
	docker compose down

## Stop and remove volumes (DESTRUCTIVE — wipes DB data)
clean:
	docker compose down -v

## Stream logs for all services
logs:
	docker compose logs -f

## Stream backend logs only
logs-backend:
	docker compose logs -f backend

## Shell into the backend container
shell-backend:
	docker compose exec backend bash

## psql shell into Postgres
shell-db:
	docker compose exec postgres psql -U postgres -d insightsql

## Rebuild without cache
rebuild:
	docker compose build --no-cache

## Check health / status of all containers
status:
	docker compose ps
