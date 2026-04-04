from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import AsyncSessionLocal
from app.repositories.chat_messages import ChatMessagesRepository
from app.repositories.users import UsersRepository
from app.services.openrouter_client import OpenRouterClient
from app.usecases.auth import AuthUseCase
from app.usecases.chat import ChatUseCase

# Настройка для Swagger UI (сообщает Swagger'у, куда слать данные для получения токена)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Выдает асинхронную сессию БД на время запроса и закрывает её после."""
    async with AsyncSessionLocal() as session:
        yield session


# === Фабрики для Usecases ===

def get_auth_usecase(
    session: AsyncSession = Depends(get_session)
) -> AuthUseCase:
    """Собирает AuthUseCase, подсовывая ему нужный репозиторий."""
    users_repo = UsersRepository(session)
    return AuthUseCase(users_repo)


def get_chat_usecase(
    session: AsyncSession = Depends(get_session)
) -> ChatUseCase:
    """Собирает ChatUseCase, подсовывая ему репозиторий и клиента API."""
    chat_repo = ChatMessagesRepository(session)
    llm_client = OpenRouterClient()
    return ChatUseCase(chat_repo, llm_client)


# === Аутентификация и проверка прав ===

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """
    Декодирует JWT токен из заголовка Authorization и возвращает ID пользователя.
    Если токен невалидный или просрочен, выбрасывает 401 Unauthorized.
    """
    try:
        payload = decode_token(token)
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise ValueError("Token missing 'sub' field")
        return int(user_id_str)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )