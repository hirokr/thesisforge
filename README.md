# ThesisForge

ThesisForge is a multi-agent thesis review workspace. The repository is organized as a monorepo with a Next.js frontend and FastAPI backend.

## Apps

- `apps/web`: Next.js App Router frontend
- `apps/api`: FastAPI backend

## Prerequisites

- Node.js 22+
- Python 3.11+

## Frontend

```bash
npm install
npm run dev:web
```

The frontend runs at `http://localhost:3000`.

## Backend

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend runs at `http://localhost:8000`.

Health check:

```bash
curl http://localhost:8000/health
```

## Analysis Worker

Analysis runs are queued with RQ and Redis.

```bash
redis-server
cd apps/api
source .venv/bin/activate
rq worker thesisforge-analysis --url redis://localhost:6379/0
```

## Environment

Copy the examples before running services:

```bash
cp .env.example .env
cp apps/web/.env.local.example apps/web/.env.local
cp apps/api/.env.example apps/api/.env
```
