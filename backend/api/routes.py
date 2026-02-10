from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import db_session, require_admin
from backend.application.auth_service import AuthService
from backend.application.channels_service import ChannelsService
from backend.application.post_editor_service import PostEditorService
from backend.domain.schemas import (
    ChannelCreateDTO,
    ChannelDTO,
    ChannelUpdateDTO,
    LoginRequest,
    PreviewRequest,
    TokenResponse,
)
from backend.infrastructure.repositories import (
    SQLAlchemyChannelsRepository,
    SQLAlchemyLogsRepository,
    SQLAlchemyUsersRepository,
)

router = APIRouter(prefix="/api")
auth_service = AuthService()
editor_service = PostEditorService()


async def _get_admin_user_id(session: AsyncSession) -> int:
    user = await SQLAlchemyUsersRepository(session).get_or_create_by_telegram_id(0)
    return user.id


@router.post("/auth/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    if not auth_service.verify_admin(payload.username, payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = auth_service.create_access_token(payload.username)
    return TokenResponse(access_token=token)


@router.get("/channels", response_model=list[ChannelDTO])
async def get_channels(_: str = Depends(require_admin), session: AsyncSession = Depends(db_session)) -> list[ChannelDTO]:
    admin_user_id = await _get_admin_user_id(session)
    service = ChannelsService(SQLAlchemyChannelsRepository(session))
    return await service.list_channels(admin_user_id)


@router.post("/channels", response_model=ChannelDTO)
async def create_channel(
    payload: ChannelCreateDTO,
    _: str = Depends(require_admin),
    session: AsyncSession = Depends(db_session),
) -> ChannelDTO:
    admin_user_id = await _get_admin_user_id(session)
    service = ChannelsService(SQLAlchemyChannelsRepository(session))
    return await service.create_channel(admin_user_id, payload)


@router.patch("/channels/{channel_id}", response_model=ChannelDTO)
async def update_channel(
    channel_id: str,
    payload: ChannelUpdateDTO,
    _: str = Depends(require_admin),
    session: AsyncSession = Depends(db_session),
) -> ChannelDTO:
    admin_user_id = await _get_admin_user_id(session)
    service = ChannelsService(SQLAlchemyChannelsRepository(session))
    result = await service.update_channel(admin_user_id, channel_id, payload)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    return result


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
    channel = await SQLAlchemyChannelsRepository(session).get_by_channel_id(payload.channel_id)
    if channel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    rendered = editor_service.apply(payload.text, channel)
    return {"preview": rendered}


@router.get("/settings", response_model=ChannelDTO)
async def get_settings_legacy(_: str = Depends(require_admin), session: AsyncSession = Depends(db_session)) -> ChannelDTO:
    admin_user_id = await _get_admin_user_id(session)
    channels = await ChannelsService(SQLAlchemyChannelsRepository(session)).list_channels(admin_user_id)
    if not channels:
        return await ChannelsService(SQLAlchemyChannelsRepository(session)).create_channel(
            admin_user_id,
            ChannelCreateDTO(channel_id="-1000000000000"),
        )
    return channels[0]


@router.post("/settings/update", response_model=ChannelDTO)
async def update_settings_legacy(
    payload: ChannelUpdateDTO,
    _: str = Depends(require_admin),
    session: AsyncSession = Depends(db_session),
) -> ChannelDTO:
    admin_user_id = await _get_admin_user_id(session)
    channels = await ChannelsService(SQLAlchemyChannelsRepository(session)).list_channels(admin_user_id)
    if not channels:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No channels configured")
    updated = await ChannelsService(SQLAlchemyChannelsRepository(session)).update_channel(admin_user_id, channels[0].channel_id, payload)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    return updated
