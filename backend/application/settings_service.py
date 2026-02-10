from backend.domain.schemas import SettingsDTO, SettingsUpdateDTO
from backend.repositories.interfaces import SettingsRepository


class SettingsService:
    def __init__(self, repository: SettingsRepository) -> None:
        self.repository = repository

    async def get_settings(self) -> SettingsDTO:
        return await self.repository.get()

    async def update_settings(self, payload: SettingsUpdateDTO) -> SettingsDTO:
        return await self.repository.upsert(payload)
