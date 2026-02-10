# BioStage Enterprise Telegram Automation Platform

Professional darajadagi yechim: Telegram kanal postlarini avtomatik ravishda tahrirlovchi bot + boshqaruv uchun web admin panel.

## Stack
- **Backend:** FastAPI, python-telegram-bot v20+, SQLAlchemy (async), JWT auth
- **Frontend:** Next.js (React), Tailwind CSS, Axios
- **DB:** PostgreSQL (Docker), SQLite (local fallback)
- **Infra:** Docker, Docker Compose, webhook-ready bot runtime

## Clean Architecture (Backend)
```
backend/
  api/                # FastAPI routers va DI
  application/        # Use case/service layer
  bot/                # Telegram webhook runtime va handlers
  core/               # Config va global settings
  database/           # SQLAlchemy models va session
  domain/             # DTO va domain contracts
  infrastructure/     # Repository implementations
  repositories/       # Repository interfaces
  tests/              # Unit tests
```

## API endpoints
- `POST /api/auth/login`
- `GET /api/settings`
- `POST /api/settings/update`
- `GET /api/logs`
- `POST /api/preview`
- `POST /webhook/telegram`

## Bot workflow
1. `channel_post` update keladi.
2. Sozlamalar DB dan olinadi.
3. `target_text` topiladi.
4. `style` mapping asosida hyperlink format qilinadi (HTML).
5. Post `edit_message_text` orqali yangilanadi.
6. Natija `logs` jadvaliga yoziladi.

## Quick start (local)
```bash
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -e backend[dev]
uvicorn backend.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Docker run
```bash
docker compose up --build
```

## Test
```bash
pytest backend/tests -q
```
