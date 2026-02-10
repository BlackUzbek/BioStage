# BioStage Enterprise Telegram Automation Platform (Multi-channel SaaS)

Telegram kanal postlarini avtomatik tahrirlovchi bot + web admin panel. Endi multi-user va multi-channel arxitektura bilan kengaytirilgan.

## Stack
- Backend: FastAPI, python-telegram-bot v20+, SQLAlchemy Async, JWT
- Frontend: Next.js, Tailwind CSS, Axios
- Database: PostgreSQL (Docker), SQLite (fallback)

## Backend arxitektura
- `domain/`: DTO va contractlar
- `repositories/`: repository interfeyslar
- `infrastructure/`: SQLAlchemy implementatsiya
- `application/`: use-case service qatlam
- `bot/`: Telegram command + channel_post handler
- `api/`: admin dashboard endpointlar

## Multi-channel SaaS model
- `users`: telegram userlar
- `channels`: userga tegishli channel sozlamalari
- `logs`: channel bo‘yicha edit loglar

## Bot commands
- `/start`
- `/addchannel <channel_id>`
- `/setlink <channel_id> <url>`
- `/setstyle <channel_id> <plain|bold|italic>`
- `/settext <channel_id> <target_text>`
- `/mychannels`

## API
- `POST /api/auth/login`
- `GET /api/channels`
- `POST /api/channels`
- `PATCH /api/channels/{channel_id}`
- `GET /api/logs`
- `POST /api/preview`
- Legacy compatibility:
  - `GET /api/settings`
  - `POST /api/settings/update`

## Run
```bash
cp .env.example .env
docker compose up --build
```
