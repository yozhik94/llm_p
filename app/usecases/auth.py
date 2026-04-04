from app.core.errors import ConflictError, NotFoundError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User
from app.repositories.users import UsersRepository
from app.schemas.auth import RegisterRequest


class AuthUseCase:
    """Бизнес-логика аутентификации и работы с профилем пользователя."""

    def __init__(self, users_repo: UsersRepository):
        # Usecase не знает, откуда взялась БД, он просто принимает готовый репозиторий
        self.users_repo = users_repo

    async def register_user(self, payload: RegisterRequest) -> User:
        """Регистрирует нового пользователя."""
        # 1. Проверяем, существует ли уже пользователь с таким email
        existing_user = await self.users_repo.get_by_email(payload.email)
        if existing_user is not None:
            raise ConflictError("Пользователь с таким email уже существует")

        # 2. Хешируем пароль
        hashed_pwd = hash_password(payload.password)

        # 3. Сохраняем в базу через репозиторий
        new_user = await self.users_repo.create(
            email=payload.email,
            hashed_password=hashed_pwd,
            role="user"
        )
        return new_user

    async def login_user(self, email: str, plain_password: str) -> str:
        """Проверяет данные для входа и возвращает JWT токен."""
        # 1. Ищем пользователя по email
        user = await self.users_repo.get_by_email(email)
        if user is None:
            # Если пользователя нет, не уточняем, что именно неверно (для безопасности)
            raise UnauthorizedError("Неверный email или пароль")

        # 2. Проверяем пароль
        if not verify_password(plain_password, user.password_hash):
            raise UnauthorizedError("Неверный email или пароль")

        # 3. Генерируем и возвращаем токен
        token = create_access_token(subject=str(user.id), role=user.role)
        return token

    async def get_profile(self, user_id: int) -> User:
        """Возвращает профиль пользователя по ID."""
        user = await self.users_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("Пользователь не найден")
        return user