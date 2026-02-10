from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import LogModel, SettingsModel
from backend.domain.schemas import LogDTO, SettingsDTO, SettingsUpdateDTO
from backend.repositories.interfaces import LogsRepository, SettingsRepository


class SQLAlchemySettingsRepository(SettingsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self) -> SettingsDTO:
        row = await self.session.get(SettingsModel, 1)
        if row is None:
            row = SettingsModel(id=1, link="https://example.com", style="plain", target_text="BioStage", channel_id="")
            self.session.add(row)
            await self.session.commit()
            await self.session.refresh(row)
        return SettingsDTO.model_validate(row, from_attributes=True)

    async def upsert(self, payload: SettingsUpdateDTO) -> SettingsDTO:
        row = await self.session.get(SettingsModel, 1)
        if row is None:
            row = SettingsModel(id=1)
            self.session.add(row)

        row.link = payload.link
        row.style = payload.style
        row.target_text = payload.target_text
        row.channel_id = payload.channel_id

        await self.session.commit()
        await self.session.refresh(row)
        return SettingsDTO.model_validate(row, from_attributes=True)


class SQLAlchemyLogsRepository(LogsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_recent(self, limit: int = 50) -> list[LogDTO]:
        query = select(LogModel).order_by(desc(LogModel.created_at)).limit(limit)
        rows = (await self.session.execute(query)).scalars().all()
        return [LogDTO.model_validate(row, from_attributes=True) for row in rows]

    async def create(self, message_id: int, status: str, error_text: str | None = None) -> LogDTO:
        row = LogModel(message_id=message_id, status=status, error_text=error_text)
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return LogDTO.model_validate(row, from_attributes=True)
