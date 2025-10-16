.PHONY: help install install-dev lint format type-check check clean

help:
	@echo "Available commands:"
	@echo "  make install       - Install production dependencies"
	@echo "  make install-dev   - Install development dependencies"
	@echo "  make lint          - Run ruff linter"
	@echo "  make format        - Format code with ruff"
	@echo "  make type-check    - Run mypy type checker"
	@echo "  make check         - Run all checks (lint + type-check)"
	@echo "  make clean         - Remove cache files"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

lint:
	ruff check .

format:
	ruff format .

type-check:
	mypy src/ cli.py

check: lint type-check
	@echo "All checks passed!"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
