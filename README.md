# ThesisForge

Multi-agent thesis quality control powered by Band.

ThesisForge helps students and early-stage researchers turn scattered thesis materials into a structured review report. Users create a thesis project, paste or upload research materials, run a visible multi-agent workflow, and receive prioritized fixes, quality scores, citation notes, and defense questions.

## Problem

Thesis work usually lives across disconnected tools: papers in Google Scholar, references in Zotero or Mendeley, drafts in Word or LaTeX, result tables in spreadsheets, and supervisor feedback in chat or email. Because the pieces do not share context, students often discover major issues too late:

- The research gap is unclear or outdated.
- Claims are not strongly supported by citations.
- The methodology does not match the stated problem.
- Results are reported without enough interpretation.
- Supervisor feedback is hard to convert into concrete work.
- Defense preparation starts after the thesis is already assembled.

ThesisForge focuses on quality control rather than thesis writing. It helps users see what is weak, unsupported, inconsistent, or missing before submission.

## Solution

ThesisForge provides a SaaS-style research review workspace:

- Create thesis projects with structured metadata.
- Paste thesis text or upload PDF, DOCX, BibTeX, TXT, and CSV files.
- Parse documents into reviewable chunks.
- Run an asynchronous multi-agent thesis review.
- Show agent progress, collaboration logs, and handoffs.
- Generate a final report with scores, priority fixes, defense questions, and action tasks.
- Load a safe synthetic demo project for hackathon judging.

## Agent Workflow

The review workflow is intentionally visible so users can understand how the final report was produced.

1. Literature Review Agent checks literature coverage, missing themes, and weak synthesis.
2. Research Gap Agent evaluates whether the stated gap is specific, current, and defensible.
3. Citation Agent checks claim-to-reference alignment from uploaded references and thesis text.
4. Methodology Consistency Agent compares problem, objectives, methodology, dataset, and experiment details.
5. Results Interpretation Agent reviews CSV/result summaries when available.
6. Defense Preparation Agent generates likely panel questions and preparation guidance.
7. Report Generator Agent combines findings into the final thesis quality report and follow-up tasks.

Analysis runs are queued through Redis/RQ so the API can create a run immediately while a background worker executes the review.

## Band Integration

ThesisForge uses Band as the agent collaboration layer. The backend wraps Band calls in a dedicated service and records local agent messages for traceability. During a workflow, agents can send structured handoff messages, update shared context, and preserve a collaboration log that is surfaced in the review UI.

Band-related configuration is optional for local development, but required for a full hackathon demo that shows external agent collaboration.

## Tech Stack

- Frontend: Next.js App Router, React, TypeScript, Tailwind CSS, shadcn-style UI primitives
- Backend: FastAPI, Pydantic, SQLAlchemy, Alembic
- Auth: Supabase Auth JWT verification
- Database: Postgres with pgvector-ready migrations
- Jobs: Redis and RQ
- LLM boundary: provider-agnostic service with OpenAI support
- File parsing: PyMuPDF, python-docx, bibtexparser, pandas
- Deployment: Vercel for frontend, Render/Railway-compatible Docker backend

## Repository Layout

```text
.
├── apps
│   ├── api      # FastAPI backend, agents, services, migrations, tests
│   └── web      # Next.js frontend
├── examples     # Safe synthetic demo thesis dataset
├── FeatureTickets.md
├── TechnicalArchitecture.md
├── PRD.md
├── docker-compose.yml
├── render.yaml
└── vercel.json
```

## Prerequisites

- Node.js 22+
- Python 3.11+
- Postgres
- Redis
- Supabase project for authentication
- OpenAI API key for agent execution
- Band API credentials for the full collaboration demo

For local infrastructure, Docker Compose can start Postgres, Redis, and the backend service.

## Quick Start

Install frontend dependencies:

```bash
npm install
```

Create environment files:

```bash
cp .env.example .env
cp apps/web/.env.local.example apps/web/.env.local
cp apps/api/.env.example apps/api/.env
```

Start local infrastructure and the API:

```bash
docker compose up --build
```

Run migrations:

```bash
docker compose exec api alembic upgrade head
```

Start the web app:

```bash
npm run dev:web
```

Open the app at `http://localhost:3000`. The API health check is available at `http://localhost:8000/health`.

## Manual Backend Setup

If you are not using Docker for the API:

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Start the analysis worker in a second terminal:

```bash
cd apps/api
source .venv/bin/activate
rq worker thesisforge-analysis --url redis://localhost:6379/0
```

## Environment Variables

Frontend:

```text
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

Backend:

```text
APP_ENV=development
API_V1_PREFIX=/api/v1
FRONTEND_ORIGIN=http://localhost:3000
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/thesisforge
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-supabase-jwt-secret
SUPABASE_JWT_AUDIENCE=authenticated
BAND_API_BASE_URL=your-band-agent-api-url
BAND_API_KEY=your-band-api-key
BAND_PROJECT_ID=optional-band-project-id
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.aimlapi.com/v1
LLM_DEFAULT_PROVIDER=openai
LLM_DEFAULT_MODEL=gpt-4o
REDIS_URL=redis://localhost:6379/0
UPLOAD_STORAGE_DIR=storage/uploads
ANALYSIS_QUEUE_NAME=thesisforge-analysis
ANALYSIS_JOB_TIMEOUT_SECONDS=1800
RATE_LIMIT_WINDOW_SECONDS=60
RATE_LIMIT_FILE_UPLOADS_PER_WINDOW=60
RATE_LIMIT_ANALYSIS_RUNS_PER_WINDOW=20
```

Only `NEXT_PUBLIC_*` values should be exposed to the frontend deployment. Keep database credentials, Supabase service role keys, JWT secrets, LLM keys, and Band keys on the backend.

## Demo Data

The repository includes a safe synthetic thesis dataset in `examples/demo-thesis/`.

Use it manually:

1. Create a new project with values from `examples/demo-thesis/project.json`.
2. Paste `examples/demo-thesis/thesis_draft.txt` into the text document flow, or upload it as a `.txt` file.
3. Upload `examples/demo-thesis/references.bib`.
4. Upload `examples/demo-thesis/results.csv`.
5. Start a review from the project review page.

Use it through demo mode:

1. Sign in.
2. Go to the dashboard.
3. Click `Load demo project`.
4. Open the created project and start a review.

## Screenshots

Replace these placeholders with real screenshots before submitting the public repository:

- Dashboard: `docs/screenshots/dashboard.png`
- Project overview: `docs/screenshots/project-overview.png`
- Agent review progress: `docs/screenshots/analysis-progress.png`
- Final report: `docs/screenshots/final-report.png`

## Common Commands

```bash
npm run dev:web
npm run build --workspace apps/web
npm run typecheck --workspace apps/web
cd apps/api && .venv/bin/pytest
```

Run the frontend build before the frontend typecheck because the app uses generated Next.js types.

## Deployment

### Frontend on Vercel

The repository includes `vercel.json` for deploying the web app from the monorepo root. Configure the frontend environment variables in Vercel and point `NEXT_PUBLIC_API_BASE_URL` at the deployed backend API.

### Backend on Render or Railway

The repository includes `render.yaml` and an API Dockerfile. The backend starts with:

```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

Run `alembic upgrade head` during deployment, attach Postgres and Redis, and configure backend secrets in the hosting provider.

## Hackathon Notes

- ThesisForge was built for a multi-agent research workflow demo.
- Band is used for agent collaboration, handoffs, and traceability.
- The app includes visible workflow progress, collaboration logs, and final report surfaces.
- The included demo dataset is synthetic and safe for public judging.
- The product is scoped as a review and quality-control assistant, not an automated thesis writer.

## License

Add the final project license before publishing the repository.
