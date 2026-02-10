from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import ChannelModel, LogModel, UserModel
from backend.domain.schemas import ChannelCreateDTO, ChannelDTO, ChannelUpdateDTO, LogDTO, UserDTO
from backend.repositories.interfaces import ChannelsRepository, LogsRepository, UsersRepository


class SQLAlchemyUsersRepository(UsersRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_create_by_telegram_id(self, telegram_user_id: int) -> UserDTO:
        row = await self._get_row(telegram_user_id)
        if row is None:
            row = UserModel(telegram_user_id=telegram_user_id)
            self.session.add(row)
            await self.session.commit()
            await self.session.refresh(row)
        return UserDTO.model_validate(row, from_attributes=True)

    async def get_by_telegram_id(self, telegram_user_id: int) -> UserDTO | None:
        row = await self._get_row(telegram_user_id)
        return UserDTO.model_validate(row, from_attributes=True) if row else None

    async def _get_row(self, telegram_user_id: int) -> UserModel | None:
        query = select(UserModel).where(UserModel.telegram_user_id == telegram_user_id)
        return (await self.session.execute(query)).scalar_one_or_none()


class SQLAlchemyChannelsRepository(ChannelsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_for_user(self, user_id: int, payload: ChannelCreateDTO) -> ChannelDTO:
        row = ChannelModel(
            user_id=user_id,
            channel_id=payload.channel_id,
            link=payload.link,
            style=payload.style,
            target_text=payload.target_text,
            is_active=payload.is_active,
        )
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return ChannelDTO.model_validate(row, from_attributes=True)

    async def list_for_user(self, user_id: int) -> list[ChannelDTO]:
        query = select(ChannelModel).where(ChannelModel.user_id == user_id).order_by(desc(ChannelModel.created_at))
        rows = (await self.session.execute(query)).scalars().all()
        return [ChannelDTO.model_validate(row, from_attributes=True) for row in rows]

    async def update_for_user(self, user_id: int, channel_id: str, payload: ChannelUpdateDTO) -> ChannelDTO | None:
        query = select(ChannelModel).where(ChannelModel.user_id == user_id, ChannelModel.channel_id == channel_id)
        row = (await self.session.execute(query)).scalar_one_or_none()
        if row is None:
            return None

        if payload.link is not None:
            row.link = payload.link
        if payload.style is not None:
            row.style = payload.style
        if payload.target_text is not None:
            row.target_text = payload.target_text
        if payload.is_active is not None:
            row.is_active = payload.is_active

        await self.session.commit()
        await self.session.refresh(row)
        return ChannelDTO.model_validate(row, from_attributes=True)

    async def get_by_channel_id(self, channel_id: str) -> ChannelDTO | None:
        query = select(ChannelModel).where(ChannelModel.channel_id == channel_id, ChannelModel.is_active.is_(True))
        row = (await self.session.execute(query)).scalar_one_or_none()
        return ChannelDTO.model_validate(row, from_attributes=True) if row else None


class SQLAlchemyLogsRepository(LogsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_recent(self, limit: int = 50) -> list[LogDTO]:
        query = select(LogModel).order_by(desc(LogModel.created_at)).limit(limit)
        rows = (await self.session.execute(query)).scalars().all()
        return [LogDTO.model_validate(row, from_attributes=True) for row in rows]

    async def create(self, channel_id: str, message_id: int, status: str, error_text: str | None = None) -> LogDTO:
        row = LogModel(channel_id=channel_id, message_id=message_id, status=status, error_text=error_text)
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return LogDTO.model_validate(row, from_attributes=True)
