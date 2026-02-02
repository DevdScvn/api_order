# API Заказов: FastAPI + SQLAlchemy + Pydantic
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# uv для быстрой установки зависимостей
COPY pyproject.toml uv.lock* ./
RUN pip install --no-cache-dir uv \
    && uv sync --frozen --no-dev 2>/dev/null || uv sync --no-dev

COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
