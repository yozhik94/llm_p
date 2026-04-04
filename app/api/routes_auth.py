from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_usecase, get_current_user_id
from app.core.errors import ConflictError, NotFoundError, UnauthorizedError
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic
from app.usecases.auth import AuthUseCase

# APIRouter для группировки маршрутов авторизации
router = APIRouter(tags=["auth"])


@router.post(
    "/register", 
    response_model=UserPublic, 
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя"
)
async def register(
    request: RegisterRequest,
    usecase: AuthUseCase = Depends(get_auth_usecase)
):
    try:
        user = await usecase.register_user(request)
        # Так как UserPublic имеет model_config = from_attributes=True,
        # мы можем вернуть ORM-модель напрямую, FastAPI сам её сериализует
        return user
    except ConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(exc)
        )


@router.post(
    "/login", 
    response_model=TokenResponse,
    summary="Логин и получение JWT токена"
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    usecase: AuthUseCase = Depends(get_auth_usecase)
):
    # form_data.username - это стандартное поле OAuth2, 
    # мы ожидаем, что пользователь введёт туда свой email.
    try:
        token = await usecase.login_user(
            email=form_data.username, 
            plain_password=form_data.password
        )
        return TokenResponse(access_token=token)
    except UnauthorizedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/me", 
    response_model=UserPublic,
    summary="Получение профиля текущего пользователя"
)
async def get_my_profile(
    user_id: int = Depends(get_current_user_id),
    usecase: AuthUseCase = Depends(get_auth_usecase)
):
    try:
        user = await usecase.get_profile(user_id)
        return user
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(exc)
        )