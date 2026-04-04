class AppError(Exception):
    """Базовое исключение для всех ошибок приложения."""
    pass


class ConflictError(AppError):
    """Конфликт данных (например, email уже существует)."""
    pass


class UnauthorizedError(AppError):
    """Ошибка аутентификации (неверный логин, пароль или токен)."""
    pass


class ForbiddenError(AppError):
    """Ошибка авторизации (нет прав для действия)."""
    pass


class NotFoundError(AppError):
    """Объект не найден в базе данных."""
    pass


class ExternalServiceError(AppError):
    """Ошибка при обращении к внешнему API (например, OpenRouter)."""
    pass