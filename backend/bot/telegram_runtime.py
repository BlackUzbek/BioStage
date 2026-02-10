import logging

from fastapi import APIRouter, Header, HTTPException, Request, status
from telegram import Update
from telegram.ext import Application, ChannelPostHandler, CommandHandler, ContextTypes

from backend.application.post_editor_service import PostEditorService
from backend.core.config import get_settings
from backend.database.session import AsyncSessionLocal
from backend.domain.schemas import ChannelCreateDTO, ChannelUpdateDTO
from backend.infrastructure.repositories import (
    SQLAlchemyChannelsRepository,
    SQLAlchemyLogsRepository,
    SQLAlchemyUsersRepository,
)

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/webhook")
editor = PostEditorService()

telegram_app: Application | None = None


async def channel_post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.channel_post
    if not message or not message.text:
        return

    channel_id = str(message.chat_id)
    async with context.application.bot_data["session_factory"]() as session:
        channels_repo = SQLAlchemyChannelsRepository(session)
        logs_repo = SQLAlchemyLogsRepository(session)
        channel = await channels_repo.get_by_channel_id(channel_id)

        if channel is None:
            await logs_repo.create(channel_id=channel_id, message_id=message.message_id, status="skipped", error_text="Channel not configured")
            return

        if channel.target_text not in message.text:
            await logs_repo.create(channel_id=channel_id, message_id=message.message_id, status="skipped", error_text="Target text not found")
            return

        try:
            edited_text = editor.apply(message.text, channel)
            await context.bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=message.message_id,
                text=edited_text,
                parse_mode=settings.telegram_parse_mode,
                disable_web_page_preview=False,
            )
            await logs_repo.create(channel_id=channel_id, message_id=message.message_id, status="success")
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to edit channel post")
            await logs_repo.create(channel_id=channel_id, message_id=message.message_id, status="error", error_text=str(exc))


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return
    async with context.application.bot_data["session_factory"]() as session:
        user = await SQLAlchemyUsersRepository(session).get_or_create_by_telegram_id(update.effective_user.id)
    await update.message.reply_text(f"Xush kelibsiz! User ro'yxatdan o'tdi. ID: {user.telegram_user_id}")


async def add_channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return
    if not context.args:
        await update.message.reply_text("Foydalanish: /addchannel <channel_id>")
        return

    channel_id = context.args[0]
    async with context.application.bot_data["session_factory"]() as session:
        users_repo = SQLAlchemyUsersRepository(session)
        channels_repo = SQLAlchemyChannelsRepository(session)
        user = await users_repo.get_or_create_by_telegram_id(update.effective_user.id)
        created = await channels_repo.create_for_user(user.id, ChannelCreateDTO(channel_id=channel_id))
    await update.message.reply_text(f"Channel qo'shildi: {created.channel_id}")


async def set_link_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _set_channel_field(update, context, field="link")


async def set_style_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _set_channel_field(update, context, field="style")


async def set_text_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _set_channel_field(update, context, field="target_text")


async def _set_channel_field(update: Update, context: ContextTypes.DEFAULT_TYPE, field: str) -> None:
    if not update.effective_user or not update.message:
        return
    if len(context.args) < 2:
        await update.message.reply_text(f"Foydalanish: /set{'text' if field == 'target_text' else field} <channel_id> <value>")
        return

    channel_id = context.args[0]
    value = " ".join(context.args[1:])

    try:
        payload = ChannelUpdateDTO(**{field: value})
    except Exception:  # noqa: BLE001
        await update.message.reply_text("Noto'g'ri qiymat. /setstyle uchun: plain | bold | italic")
        return
    async with context.application.bot_data["session_factory"]() as session:
        users_repo = SQLAlchemyUsersRepository(session)
        channels_repo = SQLAlchemyChannelsRepository(session)
        user = await users_repo.get_by_telegram_id(update.effective_user.id)
        if user is None:
            await update.message.reply_text("Avval /start yuboring")
            return
        updated = await channels_repo.update_for_user(user.id, channel_id, payload)

    if updated is None:
        await update.message.reply_text("Channel topilmadi yoki sizga tegishli emas")
        return
    await update.message.reply_text(f"{field} yangilandi: {updated.channel_id}")


async def my_channels_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return
    async with context.application.bot_data["session_factory"]() as session:
        users_repo = SQLAlchemyUsersRepository(session)
        channels_repo = SQLAlchemyChannelsRepository(session)
        user = await users_repo.get_by_telegram_id(update.effective_user.id)
        if user is None:
            await update.message.reply_text("Sizda channel yo'q. /start va /addchannel dan boshlang.")
            return
        channels = await channels_repo.list_for_user(user.id)

    if not channels:
        await update.message.reply_text("Sizda channel sozlamalari mavjud emas")
        return

    lines = [f"{c.channel_id} | {c.style} | {c.link} | text: {c.target_text}" for c in channels]
    await update.message.reply_text("\n".join(lines))


async def init_telegram(session_factory=AsyncSessionLocal) -> Application | None:
    global telegram_app
    if not settings.telegram_bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN is empty; bot runtime disabled")
        return None

    telegram_app = Application.builder().token(settings.telegram_bot_token).build()
    telegram_app.add_handler(ChannelPostHandler(channel_post_handler))
    telegram_app.add_handler(CommandHandler("start", start_command))
    telegram_app.add_handler(CommandHandler("addchannel", add_channel_command))
    telegram_app.add_handler(CommandHandler("setlink", set_link_command))
    telegram_app.add_handler(CommandHandler("setstyle", set_style_command))
    telegram_app.add_handler(CommandHandler("settext", set_text_command))
    telegram_app.add_handler(CommandHandler("mychannels", my_channels_command))
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
