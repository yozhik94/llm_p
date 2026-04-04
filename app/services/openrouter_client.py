import httpx

from app.core.config import settings
from app.core.errors import ExternalServiceError


class OpenRouterClient:
    """Клиент для общения с API OpenRouter."""

    async def chat_completion(
        self, 
        messages: list[dict[str, str]], 
        temperature: float = 0.7
    ) -> str:
        """
        Отправляет список сообщений в OpenRouter и возвращает текст ответа.
        Ожидаемый формат messages: [{"role": "user", "content": "Привет"}]
        """
        if not settings.openrouter_api_key:
            raise ExternalServiceError("Ключ OpenRouter API не настроен в .env")

        # Формируем заголовки по документации OpenRouter
        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.openrouter_site_url,
            "X-Title": settings.openrouter_app_name,
        }

        # Формируем тело запроса
        payload = {
            "model": settings.openrouter_model,
            "messages": messages,
            "temperature": temperature,
        }

        # Делаем асинхронный HTTP-запрос
        # Используем timeout=60.0, так как LLM могут отвечать долго
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{settings.openrouter_base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
            except httpx.RequestError as exc:
                raise ExternalServiceError(f"Сетевая ошибка при запросе к OpenRouter: {exc}")

        # Проверяем HTTP статус-код (400, 401, 500 и т.д.)
        if response.status_code >= 400:
            raise ExternalServiceError(
                f"OpenRouter вернул ошибку: {response.status_code} - {response.text}"
            )

        # Пытаемся достать ответ из JSON
        try:
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            return reply
        except (KeyError, IndexError, ValueError) as exc:
            raise ExternalServiceError(f"Не удалось разобрать ответ OpenRouter: {exc}")