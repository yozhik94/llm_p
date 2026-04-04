from pydantic import BaseModel, ConfigDict, EmailStr


class UserPublic(BaseModel):
    """Публичная схема пользователя (возвращается в ответах API)."""
    
    # Позволяет Pydantic читать данные напрямую из объектов SQLAlchemy (ORM)
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: str