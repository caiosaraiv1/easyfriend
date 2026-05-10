.PHONY: up down logs seed test build

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

seed:
	docker compose exec api python -c "from db import seed; seed.run()"

test:
	docker compose exec api pytest -q

build:
	docker compose build --no-cache
