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

## Docker Local Development

Docker Compose can run the local backend dependencies and FastAPI service:

```bash
docker compose up --build
```

The Compose stack includes:

- Postgres with pgvector at `localhost:5432`
- Redis at `localhost:6379`
- FastAPI backend at `http://localhost:8000`

Run database migrations after the containers are up:

```bash
docker compose exec api alembic upgrade head
```

The backend container connects to Postgres with:

```text
postgresql+psycopg://postgres:postgres@postgres:5432/thesisforge
```

It connects to Redis with:

```text
redis://redis:6379/0
```

## Vercel Frontend Deployment

The repository includes `vercel.json` for deploying the Next.js app from the monorepo root. Configure these Vercel environment variables for Production, Preview, and Development as needed:

```text
NEXT_PUBLIC_APP_URL=https://your-vercel-app.vercel.app
NEXT_PUBLIC_API_BASE_URL=https://your-api-host.example.com/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

Only `NEXT_PUBLIC_*` values belong in the Vercel frontend project. Do not add backend-only secrets such as `DATABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET`, `OPENAI_API_KEY`, or `BAND_API_KEY` to the frontend deployment.

## Render Backend Deployment

The repository includes `render.yaml` for deploying the FastAPI backend as a Docker web service on Render. The service builds from `apps/api/Dockerfile`, starts with:

```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

Render runs migrations before deploy with:

```bash
alembic upgrade head
```

Set these backend environment variables in Render:

```text
APP_ENV=production
API_V1_PREFIX=/api/v1
FRONTEND_ORIGIN=https://your-vercel-app.vercel.app
DATABASE_URL=postgresql+psycopg://user:password@host:5432/database
REDIS_URL=redis://host:6379/0
SUPABASE_JWT_SECRET=your-supabase-jwt-secret
SUPABASE_JWT_AUDIENCE=authenticated
OPENAI_API_KEY=your-openai-api-key
LLM_DEFAULT_PROVIDER=openai
LLM_DEFAULT_MODEL=gpt-4.1-mini
BAND_API_BASE_URL=https://app.band.ai/api/v1/agent
BAND_API_KEY=optional-band-api-key
BAND_PROJECT_ID=optional-band-project-id
UPLOAD_STORAGE_DIR=storage/uploads
ANALYSIS_QUEUE_NAME=thesisforge-analysis
ANALYSIS_JOB_TIMEOUT_SECONDS=1800
RATE_LIMIT_WINDOW_SECONDS=60
RATE_LIMIT_FILE_UPLOADS_PER_WINDOW=60
RATE_LIMIT_ANALYSIS_RUNS_PER_WINDOW=20
```

After deployment, verify the backend health check:

```bash
curl https://your-render-service.onrender.com/health
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
