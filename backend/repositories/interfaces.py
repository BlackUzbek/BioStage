from abc import ABC, abstractmethod

from backend.domain.schemas import LogDTO, SettingsDTO, SettingsUpdateDTO


class SettingsRepository(ABC):
    @abstractmethod
    async def get(self) -> SettingsDTO:
        raise NotImplementedError

    @abstractmethod
    async def upsert(self, payload: SettingsUpdateDTO) -> SettingsDTO:
        raise NotImplementedError


class LogsRepository(ABC):
    @abstractmethod
    async def list_recent(self, limit: int = 50) -> list[LogDTO]:
        raise NotImplementedError

    @abstractmethod
    async def create(self, message_id: int, status: str, error_text: str | None = None) -> LogDTO:
        raise NotImplementedError
