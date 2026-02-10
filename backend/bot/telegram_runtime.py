import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from telegram import Update
from telegram.ext import Application, ChannelPostHandler, ContextTypes

from backend.api.deps import db_session
from backend.application.post_editor_service import PostEditorService
from backend.core.config import get_settings
from backend.infrastructure.repositories import SQLAlchemyLogsRepository, SQLAlchemySettingsRepository

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/webhook")
editor = PostEditorService()

telegram_app: Application | None = None


async def channel_post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.channel_post
    if not message or not message.text:
        return

    async with context.application.bot_data["session_factory"]() as session:
        settings_repo = SQLAlchemySettingsRepository(session)
        logs_repo = SQLAlchemyLogsRepository(session)
        current = await settings_repo.get()

        if current.channel_id and str(message.chat_id) != str(current.channel_id):
            return

        if current.target_text not in message.text:
            await logs_repo.create(message_id=message.message_id, status="skipped", error_text="Target text not found")
            return

        try:
            edited_text = editor.apply(message.text, current)
            await context.bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=message.message_id,
                text=edited_text,
                parse_mode=settings.telegram_parse_mode,
                disable_web_page_preview=False,
            )
            await logs_repo.create(message_id=message.message_id, status="success")
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to edit channel post")
            await logs_repo.create(message_id=message.message_id, status="error", error_text=str(exc))


async def init_telegram(session_factory) -> Application | None:
    global telegram_app
    if not settings.telegram_bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN is empty; bot runtime disabled")
        return None

    telegram_app = Application.builder().token(settings.telegram_bot_token).build()
    telegram_app.add_handler(ChannelPostHandler(channel_post_handler))
    telegram_app.bot_data["session_factory"] = session_factory
    await telegram_app.initialize()
    return telegram_app


@router.post("/telegram")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict:
    if settings.telegram_webhook_secret and x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook secret")

    if telegram_app is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Telegram bot is not initialized")

    payload = await request.json()
    update = Update.de_json(payload, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}
