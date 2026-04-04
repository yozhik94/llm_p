from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Схема входных данных для регистрации пользователя."""
    email: EmailStr
    # Обязательное ограничение пароля (как требует задание)
    password: str = Field(min_length=8, max_length=50)


class TokenResponse(BaseModel):
    """Схема ответа с JWT-токеном при успешном логине."""
    access_token: str
    token_type: str = "bearer"
