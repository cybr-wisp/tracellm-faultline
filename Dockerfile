FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first for cache
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy source
COPY src/ src/
COPY configs/ configs/
COPY datasets/ datasets/

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "faultline.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
