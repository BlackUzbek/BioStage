from abc import ABC, abstractmethod

from backend.domain.schemas import ChannelCreateDTO, ChannelDTO, ChannelUpdateDTO, LogDTO, UserDTO


class UsersRepository(ABC):
    @abstractmethod
    async def get_or_create_by_telegram_id(self, telegram_user_id: int) -> UserDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_by_telegram_id(self, telegram_user_id: int) -> UserDTO | None:
        raise NotImplementedError


class ChannelsRepository(ABC):
    @abstractmethod
    async def create_for_user(self, user_id: int, payload: ChannelCreateDTO) -> ChannelDTO:
        raise NotImplementedError

    @abstractmethod
    async def list_for_user(self, user_id: int) -> list[ChannelDTO]:
        raise NotImplementedError

    @abstractmethod
    async def update_for_user(self, user_id: int, channel_id: str, payload: ChannelUpdateDTO) -> ChannelDTO | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_channel_id(self, channel_id: str) -> ChannelDTO | None:
        raise NotImplementedError


class LogsRepository(ABC):
    @abstractmethod
    async def list_recent(self, limit: int = 50) -> list[LogDTO]:
        raise NotImplementedError

    @abstractmethod
    async def create(self, channel_id: str, message_id: int, status: str, error_text: str | None = None) -> LogDTO:
        raise NotImplementedError
