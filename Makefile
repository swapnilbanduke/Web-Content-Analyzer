# Makefile for Web Content Analyzer

.PHONY: help install install-backend install-frontend run run-backend run-frontend test clean docker-up docker-down docker-build

help:
	@echo "Web Content Analyzer - Available Commands:"
	@echo ""
	@echo "  make install          - Install all dependencies"
	@echo "  make run              - Run both backend and frontend"
	@echo "  make test             - Run all tests"
	@echo "  make docker-up        - Start Docker containers"
	@echo "  make docker-down      - Stop Docker containers"
	@echo "  make clean            - Clean temporary files"

install: install-backend install-frontend

install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && pip install -r requirements.txt

run-backend:
	cd backend && python main.py

run-frontend:
	cd frontend && streamlit run app.py

test:
	cd backend && pytest tests/ -v

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-build:
	docker-compose build --no-cache

docker-logs:
	docker-compose logs -f

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
