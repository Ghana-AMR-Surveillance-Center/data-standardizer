.PHONY: install dev lint test run-app run-api docker-build up down

install:
	pip install --upgrade pip
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt -r requirements-dev.txt

lint:
	ruff check .
	black --check .
	mypy .

test:
	pytest -q

run-app:
	python run.py

run-api:
	uvicorn api.app:app --host 0.0.0.0 --port 9000

docker-build:
	docker build -t glass-data-standardizer:latest .

up:
	docker compose up -d --build

down:
	docker compose down


