import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.categories import router as categories_router
from api.nomenclature import router as nomenclature_router
from api.orders import router as orders_router
from database import db_helper, init_db
from settings.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Создание таблиц БД при старте, закрытие пула при остановке."""
    init_db()
    yield
    await db_helper.dispose()


app = FastAPI(
    title="API Заказов",
    description=(
        "REST-API для работы с заказами. "
        "**Добавление товара в заказ**: POST `/orders/items` — принимает ID заказа, ID номенклатуры и количество; "
        "если товар уже в заказе — количество увеличивается; при отсутствии товара в наличии возвращается ошибка."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(orders_router, prefix="/api")
app.include_router(nomenclature_router, prefix="/api")
app.include_router(categories_router, prefix="/api")


@app.get("/")
def root() -> dict[str, str]:
    """Корневой эндпоинт: приветствие и ссылка на документацию."""
    return {
        "message": "Hello World",
        "docs": "/docs",
        "redoc": "/redoc",
    }


def run_app() -> None:
    """Запускает FastAPI-приложение через uvicorn."""
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )


if __name__ == "__main__":
    run_app()
