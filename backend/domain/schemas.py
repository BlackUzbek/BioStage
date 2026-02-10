from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


StyleType = Literal["plain", "bold", "italic"]


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserDTO(BaseModel):
    id: int
    telegram_user_id: int
    created_at: datetime


class ChannelDTO(BaseModel):
    id: int
    user_id: int
    channel_id: str = Field(min_length=1)
    link: str = Field(min_length=1)
    style: StyleType = "plain"
    target_text: str = Field(min_length=1)
    is_active: bool = True
    created_at: datetime


class ChannelCreateDTO(BaseModel):
    channel_id: str = Field(min_length=1)
    link: str = "https://example.com"
    style: StyleType = "plain"
    target_text: str = "BioStage"
    is_active: bool = True


class ChannelUpdateDTO(BaseModel):
    link: str | None = None
    style: StyleType | None = None
    target_text: str | None = None
    is_active: bool | None = None


class LogDTO(BaseModel):
    id: int
    channel_id: str
    message_id: int
    status: str
    error_text: str | None
    created_at: datetime


class PreviewRequest(BaseModel):
    text: str
    channel_id: str = Field(min_length=1)


class BotCommandResponse(BaseModel):
    message: str
