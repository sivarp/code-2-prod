FROM python:3.13-slim AS builder

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .[dev]

COPY src/ ./src/
COPY tests/ ./tests/

RUN python -m pylint src/ && \
    python -m pytest

FROM python:3.13-slim AS production

WORKDIR /app

COPY pyproject.toml ./
COPY src/ ./src/
RUN pip install --no-cache-dir . && rm -rf ./src

EXPOSE 8080

CMD ["gists-api"]