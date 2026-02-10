from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from backend.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def verify_admin(self, username: str, password: str) -> bool:
        if username != self.settings.admin_username:
            return False
        return pwd_context.verify(password, self.settings.admin_password_hash)

    def create_access_token(self, subject: str) -> str:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=self.settings.jwt_expire_minutes)
        payload = {"sub": subject, "exp": expire}
        return jwt.encode(payload, self.settings.jwt_secret_key, algorithm=self.settings.jwt_algorithm)
