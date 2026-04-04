from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Формируем строку подключения для асинхронного SQLite
DATABASE_URL = f"sqlite+aiosqlite:///{settings.sqlite_path}"

# Создаем асинхронный движок (engine)
engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
)

# Создаем фабрику сессий, которая будет выдавать нам объекты AsyncSession
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)