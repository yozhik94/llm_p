from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Схема запроса для отправки сообщения в LLM."""
    
    # Обязательное поле: текст запроса пользователя (ограничим длину от спама)
    prompt: str = Field(..., min_length=1, max_length=4000)
    
    # Необязательное поле: системный промпт (например: "Ты - добрый пират")
    system: str | None = Field(default=None, max_length=1000)
    
    # Настройки контекста: сколько предыдущих сообщений из базы прикрепить
    max_history: int = Field(default=5, ge=0, le=20)
    
    # Креативность модели: 0.0 - строгий и точный, 1.0 - креативный
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class ChatResponse(BaseModel):
    """Схема ответа от LLM."""
    answer: str
