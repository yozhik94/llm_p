from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_auth import router as auth_router
from app.api.routes_chat import router as chat_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Выполняется при старте приложения (до того, как оно начнёт принимать запросы).
    Здесь мы автоматически создаём все таблицы в базе данных SQLite.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield  # Приложение работает...
    
    # Здесь можно было бы закрыть соединения при выключении (shutdown)
    await engine.dispose()


def create_app() -> FastAPI:
    """Фабрика для сборки и настройки приложения."""
    app = FastAPI(
        title=settings.app_name,
        description="FastAPI сервис с JWT, SQLite и OpenRouter LLM",
        version="0.1.0",
        lifespan=lifespan
    )

    # Настройка CORS (разрешаем всем делать запросы к нашему API)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Подключение роутеров из других файлов
    app.include_router(auth_router, prefix="/auth")
    app.include_router(chat_router, prefix="/chat")

    # Технический эндпоинт проверки  сервера
    @app.get("/health", tags=["system"], summary="Проверка состояния сервера")
    async def health_check():
        return {
            "status": "ok",
            "environment": settings.env,
            "app_name": settings.app_name
        }

    return app


# Создаем глобальный объект приложения для uvicorn
app = create_app()