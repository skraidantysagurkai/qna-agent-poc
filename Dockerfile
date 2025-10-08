FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock* /app/

# Install dependencies with uv
RUN uv sync --frozen --no-cache

# Copy application code
COPY . /app/

# Declare volume for data persistence
VOLUME ["/app/data"]

EXPOSE 8080

CMD ["uv", "run", "python", "main.py"]
