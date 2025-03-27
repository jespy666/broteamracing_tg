bot:
	python3 -m src.bot

lint:
	poetry run ruff check ./src

lint-fix:
	ruff check ./src --fix

install:
	poetry install --no-root

install-no-dev:
	poetry install --no-root --only main