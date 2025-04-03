FROM python:3.12-slim

WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv/ /uvx/ /bin/

COPY . /app
RUN uv sync --frozen --no-cache
