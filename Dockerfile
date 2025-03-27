FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --only main

RUN poetry config virtualenvs.create false

COPY . ./

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "src.bot"]