from backend.domain.schemas import ChannelCreateDTO, ChannelDTO, ChannelUpdateDTO
from backend.repositories.interfaces import ChannelsRepository


class ChannelsService:
    def __init__(self, repository: ChannelsRepository) -> None:
        self.repository = repository

    async def create_channel(self, user_id: int, payload: ChannelCreateDTO) -> ChannelDTO:
        return await self.repository.create_for_user(user_id, payload)

    async def list_channels(self, user_id: int) -> list[ChannelDTO]:
        return await self.repository.list_for_user(user_id)

    async def update_channel(self, user_id: int, channel_id: str, payload: ChannelUpdateDTO) -> ChannelDTO | None:
        return await self.repository.update_for_user(user_id, channel_id, payload)
