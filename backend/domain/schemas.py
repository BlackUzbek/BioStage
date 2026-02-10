from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


StyleType = Literal["plain", "bold", "italic"]


class SettingsDTO(BaseModel):
    id: int = 1
    link: str = Field(min_length=1)
    style: StyleType = "plain"
    target_text: str = Field(min_length=1)
    channel_id: str = Field(min_length=1)
    updated_at: datetime | None = None


class SettingsUpdateDTO(BaseModel):
    link: str = Field(min_length=1)
    style: StyleType
    target_text: str = Field(min_length=1)
    channel_id: str = Field(min_length=1)


class LogDTO(BaseModel):
    id: int
    message_id: int
    status: str
    error_text: str | None
    created_at: datetime


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PreviewRequest(BaseModel):
    text: str
