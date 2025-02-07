.PHONY: build up down restart logs shell dbshell install deps test clean

# Build and start the containers
build:
	docker-compose up --build -d

# Start the containers (without rebuilding)
up:
	docker-compose up -d

# Stop the containers
down:
	docker-compose down

# Restart the containers
restart: down up

# Show logs for the app
logs:
	docker logs -f amaia_scraper

# Open an interactive shell in the app container
shell:
	docker exec -it amaia_scraper /bin/bash

# Open PostgreSQL shell
dbshell:
	docker exec -it amaia_pg psql -U amaia_user -d amaia_db

# Install dependencies inside the running container
install:
	docker exec -it amaia_scraper pip install -r requirements.txt

# Install dependencies and update `requirements.txt`
deps:
	docker exec -it amaia_scraper pip freeze > requirements.txt

# Run database connection test
test:
	docker exec -it amaia_scraper python /app/src/main.py

# Clean everything (removes containers, volumes, and cache)
clean:
	docker-compose down -v --remove-orphans && docker system prune -f
