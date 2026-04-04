from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


class UsersRepository:
    def __init__(self, session: AsyncSession):
        """Принимаем сессию БД при создании объекта (Dependency Injection)."""
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        """Ищет пользователя в БД по email."""
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        """Ищет пользователя в БД по ID."""
        stmt = select(User).where(User.id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, email: str, hashed_password: str, role: str = "user") -> User:
        """Создает нового пользователя в БД. Пароль уже должен быть захеширован!"""
        new_user = User(
            email=email,
            password_hash=hashed_password,
            role=role
        )
        self._session.add(new_user)
        await self._session.commit()
        await self._session.refresh(new_user)
        
        return new_user