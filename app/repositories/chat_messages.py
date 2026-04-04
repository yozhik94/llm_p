from typing import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChatMessage


class ChatMessagesRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_message(self, user_id: int, role: str, content: str) -> ChatMessage:
        """Добавляет одно сообщение (от пользователя или от ассистента) в БД."""
        msg = ChatMessage(
            user_id=user_id,
            role=role,
            content=content
        )
        self._session.add(msg)
        await self._session.commit()
        await self._session.refresh(msg)
        return msg

    async def get_last_messages(self, user_id: int, limit: int = 5) -> Sequence[ChatMessage]:
        """
        Возвращает последние N сообщений пользователя.
        Сначала берем последние (desc), чтобы не тянуть всю базу,
        затем в самом коде они могут быть перевернуты в прямой порядок.
        """
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        # Получаем список (Sequence) ORM-объектов
        messages = result.scalars().all()
        
        # Возвращаем их в прямом хронологическом порядке (от старых к новым),
        # так как это обычно нужно для контекста LLM.
        return list(reversed(messages))

    async def clear_history(self, user_id: int) -> None:
        """Удаляет всю историю сообщений конкретного пользователя."""
        stmt = delete(ChatMessage).where(ChatMessage.user_id == user_id)
        await self._session.execute(stmt)
        await self._session.commit()