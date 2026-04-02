.PHONY: migrate migrate-new migrate-show lint lint-fix format format-check

migrate:
	docker compose exec backend python manage.py migrate

# Create a new migration: make migrate-new name=<migration_name>
migrate-new:
	docker compose exec backend python manage.py makemigrations api --name $(name)

migrate-show:
	docker compose exec backend python manage.py showmigrations

lint:
	docker compose exec backend ruff check .

lint-fix:
	docker compose exec backend ruff check --fix .

format-check:
	docker compose exec backend ruff format --check .

format:
	docker compose exec backend ruff format .