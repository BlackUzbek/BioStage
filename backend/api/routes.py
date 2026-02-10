from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import db_session, require_admin
from backend.application.auth_service import AuthService
from backend.application.post_editor_service import PostEditorService
from backend.application.settings_service import SettingsService
from backend.domain.schemas import LoginRequest, PreviewRequest, SettingsDTO, SettingsUpdateDTO, TokenResponse
from backend.infrastructure.repositories import SQLAlchemyLogsRepository, SQLAlchemySettingsRepository

router = APIRouter(prefix="/api")
auth_service = AuthService()
editor_service = PostEditorService()


@router.post("/auth/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    if not auth_service.verify_admin(payload.username, payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = auth_service.create_access_token(payload.username)
    return TokenResponse(access_token=token)


@router.get("/settings", response_model=SettingsDTO)
async def get_settings(_: str = Depends(require_admin), session: AsyncSession = Depends(db_session)) -> SettingsDTO:
    service = SettingsService(SQLAlchemySettingsRepository(session))
    return await service.get_settings()


@router.post("/settings/update", response_model=SettingsDTO)
async def update_settings(
    payload: SettingsUpdateDTO,
    _: str = Depends(require_admin),
    session: AsyncSession = Depends(db_session),
) -> SettingsDTO:
    service = SettingsService(SQLAlchemySettingsRepository(session))
    return await service.update_settings(payload)


@router.get("/logs")
async def get_logs(
    limit: int = Query(default=50, ge=1, le=200),
    _: str = Depends(require_admin),
    session: AsyncSession = Depends(db_session),
) -> list:
    repo = SQLAlchemyLogsRepository(session)
    return await repo.list_recent(limit=limit)


@router.post("/preview")
async def preview(payload: PreviewRequest, session: AsyncSession = Depends(db_session), _: str = Depends(require_admin)) -> dict:
    settings = await SQLAlchemySettingsRepository(session).get()
    rendered = editor_service.apply(payload.text, settings)
    return {"preview": rendered}
