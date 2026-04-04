from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_chat_usecase, get_current_user_id
from app.core.errors import ExternalServiceError
from app.schemas.chat import ChatRequest, ChatResponse
from app.usecases.chat import ChatUseCase

router = APIRouter(tags=["chat"])


@router.post(
    "/",
    response_model=ChatResponse,
    summary="Отправить сообщение в LLM"
)
async def chat_with_llm(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    usecase: ChatUseCase = Depends(get_chat_usecase)
):
    try:
        answer = await usecase.ask(user_id=user_id, request=request)
        return ChatResponse(answer=answer)
    except ExternalServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, 
            detail=str(exc)
        )


@router.get(
    "/history",
    summary="Получить историю переписки текущего пользователя"
)
async def get_chat_history(
    limit: int = 50,
    user_id: int = Depends(get_current_user_id),
    usecase: ChatUseCase = Depends(get_chat_usecase)
) -> list[dict[str, Any]]:
    # Возвращаем список словарей (схема тут не обязательна, можно вернуть сырые данные)
    history = await usecase.get_history(user_id=user_id, limit=limit)
    return [
        {"id": msg.id, "role": msg.role, "content": msg.content, "created_at": msg.created_at} 
        for msg in history
    ]


@router.delete(
    "/history",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Очистить историю переписки"
)
async def clear_chat_history(
    user_id: int = Depends(get_current_user_id),
    usecase: ChatUseCase = Depends(get_chat_usecase)
):
    await usecase.clear_history(user_id=user_id)
    return None