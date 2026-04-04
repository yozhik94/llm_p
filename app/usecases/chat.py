from app.repositories.chat_messages import ChatMessagesRepository
from app.schemas.chat import ChatRequest
from app.services.openrouter_client import OpenRouterClient


class ChatUseCase:
    """Бизнес-логика чата: формирование контекста, сохранение истории, запрос к LLM."""

    def __init__(
        self, 
        chat_repo: ChatMessagesRepository, 
        llm_client: OpenRouterClient
    ):
        self.chat_repo = chat_repo
        self.llm_client = llm_client

    async def ask(self, user_id: int, request: ChatRequest) -> str:
        """Обрабатывает запрос пользователя, получает ответ от LLM и сохраняет историю."""
        
        # 1. Собираем контекст для отправки в LLM
        messages_payload = []

        # 1.1. Если есть системный промпт, он всегда идёт первым
        if request.system:
            messages_payload.append({"role": "system", "content": request.system})

        # 1.2. Достаём историю переписки из базы
        if request.max_history > 0:
            history = await self.chat_repo.get_last_messages(
                user_id=user_id, 
                limit=request.max_history
            )
            for msg in history:
                messages_payload.append({"role": msg.role, "content": msg.content})

        # 1.3. Добавляем текущий вопрос пользователя в конец
        messages_payload.append({"role": "user", "content": request.prompt})

        # 2. Сохраняем текущий вопрос пользователя в базу данных
        await self.chat_repo.add_message(
            user_id=user_id,
            role="user",
            content=request.prompt
        )

        # 3. Отправляем весь собранный контекст в OpenRouter
        assistant_reply = await self.llm_client.chat_completion(
            messages=messages_payload,
            temperature=request.temperature
        )

        # 4. Сохраняем полученный ответ от LLM в базу данных
        await self.chat_repo.add_message(
            user_id=user_id,
            role="assistant",
            content=assistant_reply
        )

        # 5. Возвращаем текст ответа для отправки клиенту
        return assistant_reply
    
    async def get_history(self, user_id: int, limit: int = 50):
        """Возвращает историю сообщений пользователя."""
        return await self.chat_repo.get_last_messages(user_id, limit)

    async def clear_history(self, user_id: int) -> None:
        """Очищает историю сообщений пользователя."""
        await self.chat_repo.clear_history(user_id)