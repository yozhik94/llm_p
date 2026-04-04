from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Настройка контекста для хеширования паролей с использованием bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хеширует пароль."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет совпадение открытого пароля с хешированным."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str,
    role: str = "user",
    expires_minutes: int | None = None
) -> str:
    """Генерирует JWT access token."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(
        minutes=expires_minutes or settings.access_token_expire_minutes
    )
    
    payload: dict[str, Any] = {
        "sub": subject,         # идентификатор пользователя
        "role": role,           # роль
        "iat": now,             # время выдачи
        "exp": expire           # время истечения
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)


def decode_token(token: str) -> dict[str, Any]:
    """Декодирует и валидирует JWT токен."""
    try:
        # Библиотека python-jose сама проверяет алгоритм, подпись и поле 'exp'
        payload = jwt.decode(
            token, 
            settings.jwt_secret, 
            algorithms=[settings.jwt_alg]
        )
        return payload
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc