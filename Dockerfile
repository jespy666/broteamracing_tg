FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN pip install --no-cache-dir poetry

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --only main

COPY . /app

CMD ["python", "-m", "src.bot"]