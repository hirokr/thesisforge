# Technical Architecture Document

## Product: ThesisForge

### Multi-Agent Research Workflow Assistant Powered by Band

## 1. Executive Summary

ThesisForge is a SaaS-style multi-agent research workflow assistant for thesis students, researchers, and academic teams. The system helps users review research gaps, citations, methodology, results, supervisor feedback, and defense readiness.

The application accepts thesis-related input such as text, PDF, DOCX, BibTeX, and CSV files. It then runs a structured multi-agent workflow where specialized agents collaborate through Band and produce a final thesis quality report.

The architecture should support two goals:

1. Build quickly for the hackathon MVP.
2. Be scalable enough to become a real SaaS product later.

The recommended architecture is:

```text
Next.js Frontend
        ↓
FastAPI Backend
        ↓
LangGraph Agent Orchestration
        ↓
Band Agent Collaboration Layer
        ↓
LLM Provider
        ↓
Postgres + pgvector + Object Storage
```

## 2. Core Architecture Principles

### 2.1 MVP First, SaaS Ready

The system should be simple enough to build quickly but structured enough to avoid a full rewrite later.

For version one, avoid unnecessary complexity such as microservices, Kubernetes, payment systems, complex role-based permissions, and real-time collaboration.

### 2.2 Agent Workflow Must Be Visible

Because the product is built for a multi-agent hackathon, agent collaboration must not be hidden. The app should visibly show:

* Which agent worked on what
* What message each agent sent
* What context was passed
* What the final report used from each agent

### 2.3 Backend Owns the Intelligence

The frontend should only handle user experience. All core logic should live in the backend:

* File parsing
* Agent workflow
* Band communication
* LLM calls
* Report generation
* Database writes
* Access control checks

### 2.4 Store Raw Inputs and Structured Outputs Separately

The system should store:

* Original user-provided content
* Parsed text chunks
* Agent messages
* Agent findings
* Final report

This allows future features like reruns, version history, search, audit logs, and supervisor review.

## 3. Recommended Tech Stack

## 3.1 Frontend

### Recommended: Next.js with App Router

**Why:**

* Good for SaaS dashboards
* Supports server-side rendering and client-side interactivity
* Easy deployment on Vercel
* Good ecosystem for authentication, UI components, forms, and file uploads
* More production-ready than Streamlit

**Use For:**

* Landing page
* Auth pages
* Dashboard
* Project creation
* Thesis input forms
* File upload UI
* Agent workflow progress page
* Final report page

**Alternative for Hackathon Speed:** Streamlit

Streamlit is faster for quick demos, but if the goal is to build a real SaaS product, use Next.js.

### Frontend Libraries

| Need               | Recommended Tool                   |
| ------------------ | ---------------------------------- |
| UI components      | shadcn/ui                          |
| Styling            | Tailwind CSS                       |
| Forms              | React Hook Form                    |
| Validation         | Zod                                |
| API calls          | TanStack Query                     |
| Markdown rendering | react-markdown                     |
| Charts/scores      | Recharts                           |
| File upload UI     | UploadDropzone or custom component |

## 3.2 Backend

### Recommended: FastAPI

**Why:**

* Python-native, which is ideal for AI/LLM workflows
* Async support for long-running requests and external API calls
* Easy to create REST APIs
* Works well with Pydantic validation
* Good for integrating LangGraph, file parsers, and LLM SDKs

**Use For:**

* User project APIs
* File processing APIs
* Thesis analysis workflow
* Agent execution
* Band integration
* Report generation
* Database access

### Backend Libraries

| Need                  | Recommended Tool              |
| --------------------- | ----------------------------- |
| API framework         | FastAPI                       |
| Data validation       | Pydantic                      |
| ORM                   | SQLAlchemy                    |
| Migrations            | Alembic                       |
| Background jobs       | Celery or RQ                  |
| Queue broker          | Redis                         |
| PDF parsing           | PyMuPDF                       |
| DOCX parsing          | python-docx                   |
| BibTeX parsing        | bibtexparser                  |
| CSV parsing           | pandas                        |
| Auth JWT verification | Supabase JWT / PyJWT          |
| Logging               | structlog or standard logging |
| Testing               | pytest                        |

## 3.3 Agent Orchestration

### Recommended: LangGraph

**Why:**

* Good for structured multi-agent workflows
* Lets each agent act as a node in a graph
* Supports state passing between agents
* Easier to debug than a fully free-form autonomous agent setup
* Good fit for thesis review because the workflow has clear stages

**Use For:**

* Literature Review Agent
* Research Gap Agent
* Citation Agent
* Methodology Consistency Agent
* Results Interpretation Agent
* Defense Preparation Agent
* Report Generator Agent

## 3.4 Agent Collaboration Layer

### Required: Band

**Why:**

* The hackathon specifically requires Band.
* Band should be used for agent-to-agent communication, not just final output.
* It should store or transmit structured agent messages, handoffs, and shared context.

**Use Band For:**

* Agent registration
* Agent-to-agent messages
* Task handoffs
* Shared context updates
* Collaboration logs
* Workflow traceability

## 3.5 Database

### Recommended: Supabase Postgres

**Why:**

* Gives you Postgres, Auth, Storage, and vector search in one platform
* Good for MVP speed
* Can scale beyond the hackathon
* Reduces backend infrastructure work

### Vector Search

Use `pgvector` inside Postgres for storing thesis chunks and embeddings.

**Use For:**

* Searching thesis sections
* Finding relevant claims
* Matching citations to claims
* Future semantic search across projects

## 3.6 File Storage

### Recommended: Supabase Storage

**Use For:**

* Uploaded thesis PDFs
* DOCX drafts
* BibTeX files
* CSV result files
* Generated reports

For MVP, store files in a private bucket.

## 3.7 Background Jobs

### Recommended: Redis + Celery

**Why:**

Thesis analysis may take time. You do not want the HTTP request to stay open while agents process the file.

**Use For:**

* File parsing
* Embedding generation
* Long-running agent workflow
* Report generation
* Retry failed agent runs

For the hackathon, you can simplify this by running the workflow synchronously first, then adding background jobs if time allows.

## 3.8 LLM Provider

### Recommended: Provider-Agnostic LLM Layer

Create an internal wrapper so you can switch between:

* OpenAI
* Gemini
* AI/ML API
* Featherless AI
* Local/open-source model

Do not directly call the provider everywhere in the codebase. Use one internal service:

```text
llm_service.py
```

This makes the app easier to maintain.

## 4. High-Level System Architecture

```text
┌────────────────────────────────────────────┐
│                Next.js Frontend             │
│ Dashboard, Upload, Agent Log, Report UI     │
└───────────────────────┬────────────────────┘
                        │
                        │ REST API
                        ↓
┌────────────────────────────────────────────┐
│                FastAPI Backend              │
│ Auth, Projects, Files, Reports, Workflows   │
└───────────────────────┬────────────────────┘
                        │
                        ↓
┌────────────────────────────────────────────┐
│             Workflow Service                │
│ LangGraph controls agent execution order    │
└───────────────────────┬────────────────────┘
                        │
                        ↓
┌────────────────────────────────────────────┐
│             Band Integration Layer          │
│ Agent messages, context sharing, handoffs   │
└───────────────────────┬────────────────────┘
                        │
                        ↓
┌────────────────────────────────────────────┐
│              Specialized Agents             │
│ Literature, Gap, Citation, Methodology,     │
│ Results, Defense, Report                    │
└───────────────────────┬────────────────────┘
                        │
                        ↓
┌────────────────────────────────────────────┐
│         LLM Provider + Embedding Provider   │
└───────────────────────┬────────────────────┘
                        │
                        ↓
┌────────────────────────────────────────────┐
│      Supabase Postgres + pgvector + Storage │
└────────────────────────────────────────────┘
```

## 5. Core Backend Modules

## 5.1 Auth Module

Responsible for:

* Verifying user JWT
* Mapping authenticated user to internal profile
* Protecting user-owned resources

## 5.2 Project Module

Responsible for:

* Creating thesis projects
* Updating project metadata
* Listing projects
* Deleting projects
* Fetching project overview

## 5.3 Document Module

Responsible for:

* Uploading thesis files
* Storing file metadata
* Parsing PDF, DOCX, TXT, BibTeX, and CSV
* Creating text chunks
* Sending chunks for embedding

## 5.4 Embedding Module

Responsible for:

* Generating embeddings for thesis chunks
* Storing vectors in Postgres
* Running similarity search
* Returning relevant chunks to agents

## 5.5 Agent Module

Responsible for:

* Defining agent prompts
* Running each agent
* Validating agent output
* Saving agent findings
* Sending messages through Band

## 5.6 Workflow Module

Responsible for:

* Creating analysis runs
* Starting LangGraph workflows
* Tracking workflow status
* Handling failed runs
* Saving final report

## 5.7 Report Module

Responsible for:

* Combining all agent outputs
* Creating final thesis health report
* Generating scores
* Exporting markdown or PDF later

## 6. Agent Architecture

## 6.1 Minimum MVP Agents

### 1. Literature Review Agent

**Input:**

* References
* Extracted thesis chunks
* User problem statement
* User research gap

**Output:**

* Paper themes
* Claim-support mapping
* Weak citation warnings
* Missing literature areas

### 2. Research Gap Agent

**Input:**

* User research gap
* Literature agent findings
* Problem statement
* Objectives

**Output:**

* Gap quality score
* Gap weaknesses
* Improved gap suggestion
* Missing evidence

### 3. Citation Agent

**Input:**

* Thesis claims
* References
* Literature findings

**Output:**

* Unsupported claims
* Weak citations
* Missing references
* Citation improvement suggestions

### 4. Methodology Consistency Agent

**Input:**

* Methodology
* Objectives
* Research gap
* Results summary

**Output:**

* Methodology alignment score
* Missing baselines
* Missing ablation studies
* Dataset/method mismatch warnings

### 5. Results Interpretation Agent

**Input:**

* Results summary
* Metrics
* Methodology
* Research objectives

**Output:**

* Result explanation quality
* Overclaiming warnings
* Missing comparison warnings
* Suggested result discussion points

### 6. Defense Preparation Agent

**Input:**

* All previous agent findings

**Output:**

* Likely panel questions
* Risk level per question
* Suggested answer points

### 7. Report Generator Agent

**Input:**

* All agent outputs
* Agent collaboration logs
* Thesis project metadata

**Output:**

* Final thesis health report
* Priority fixes
* Final score
* Next-step action list

## 6.2 Agent Workflow

```text
Start Analysis
     ↓
Parse Documents
     ↓
Generate Chunks + Embeddings
     ↓
Literature Review Agent
     ↓
Research Gap Agent
     ↓
Citation Agent
     ↓
Methodology Consistency Agent
     ↓
Results Interpretation Agent
     ↓
Defense Preparation Agent
     ↓
Report Generator Agent
     ↓
Final Report
```

## 6.3 Band Message Format

Every agent handoff should be saved in a consistent format.

```json
{
  "run_id": "uuid",
  "project_id": "uuid",
  "from_agent": "literature_review_agent",
  "to_agent": "research_gap_agent",
  "message_type": "handoff",
  "task": "validate_research_gap",
  "summary": "The current gap is too broad and needs stronger citation support.",
  "context": {
    "weak_claims": [],
    "recommended_focus": "interpretable multimodal reasoning"
  },
  "status": "sent"
}
```

## 7. Complete Project Folder Structure

Recommended monorepo structure:

```text
thesisforge/
│
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml
├── package.json
├── turbo.json
│
├── apps/
│   │
│   ├── web/
│   │   ├── package.json
│   │   ├── next.config.ts
│   │   ├── tsconfig.json
│   │   ├── tailwind.config.ts
│   │   ├── postcss.config.js
│   │   ├── .env.local.example
│   │   │
│   │   ├── public/
│   │   │   ├── logo.svg
│   │   │   └── placeholder-cover.png
│   │   │
│   │   └── src/
│   │       ├── app/
│   │       │   ├── layout.tsx
│   │       │   ├── page.tsx
│   │       │   ├── globals.css
│   │       │   │
│   │       │   ├── login/
│   │       │   │   └── page.tsx
│   │       │   │
│   │       │   ├── register/
│   │       │   │   └── page.tsx
│   │       │   │
│   │       │   ├── dashboard/
│   │       │   │   └── page.tsx
│   │       │   │
│   │       │   ├── projects/
│   │       │   │   ├── page.tsx
│   │       │   │   ├── new/
│   │       │   │   │   └── page.tsx
│   │       │   │   └── [projectId]/
│   │       │   │       ├── page.tsx
│   │       │   │       ├── upload/
│   │       │   │       │   └── page.tsx
│   │       │   │       ├── review/
│   │       │   │       │   └── page.tsx
│   │       │   │       ├── runs/
│   │       │   │       │   └── [runId]/
│   │       │   │       │       └── page.tsx
│   │       │   │       └── report/
│   │       │   │           └── [reportId]/
│   │       │   │               └── page.tsx
│   │       │   │
│   │       │   └── settings/
│   │       │       └── page.tsx
│   │       │
│   │       ├── components/
│   │       │   ├── ui/
│   │       │   ├── layout/
│   │       │   │   ├── sidebar.tsx
│   │       │   │   ├── navbar.tsx
│   │       │   │   └── app-shell.tsx
│   │       │   ├── projects/
│   │       │   │   ├── project-card.tsx
│   │       │   │   ├── project-form.tsx
│   │       │   │   └── project-status-badge.tsx
│   │       │   ├── upload/
│   │       │   │   ├── file-upload.tsx
│   │       │   │   └── uploaded-file-list.tsx
│   │       │   ├── agents/
│   │       │   │   ├── agent-timeline.tsx
│   │       │   │   ├── agent-log-card.tsx
│   │       │   │   └── agent-status-card.tsx
│   │       │   └── reports/
│   │       │       ├── thesis-score-card.tsx
│   │       │       ├── report-section.tsx
│   │       │       └── priority-fix-list.tsx
│   │       │
│   │       ├── lib/
│   │       │   ├── api-client.ts
│   │       │   ├── auth.ts
│   │       │   ├── supabase-client.ts
│   │       │   ├── constants.ts
│   │       │   └── utils.ts
│   │       │
│   │       ├── hooks/
│   │       │   ├── use-projects.ts
│   │       │   ├── use-analysis-run.ts
│   │       │   └── use-report.ts
│   │       │
│   │       └── types/
│   │           ├── project.ts
│   │           ├── document.ts
│   │           ├── agent.ts
│   │           └── report.ts
│   │
│   └── api/
│       ├── pyproject.toml
│       ├── requirements.txt
│       ├── alembic.ini
│       ├── Dockerfile
│       ├── .env.example
│       │
│       ├── alembic/
│       │   ├── env.py
│       │   └── versions/
│       │
│       ├── app/
│       │   ├── __init__.py
│       │   ├── main.py
│       │   │
│       │   ├── core/
│       │   │   ├── config.py
│       │   │   ├── security.py
│       │   │   ├── logging.py
│       │   │   └── exceptions.py
│       │   │
│       │   ├── db/
│       │   │   ├── session.py
│       │   │   ├── base.py
│       │   │   └── models/
│       │   │       ├── user_profile.py
│       │   │       ├── project.py
│       │   │       ├── document.py
│       │   │       ├── document_chunk.py
│       │   │       ├── reference.py
│       │   │       ├── analysis_run.py
│       │   │       ├── agent.py
│       │   │       ├── agent_message.py
│       │   │       ├── agent_finding.py
│       │   │       ├── report.py
│       │   │       ├── task.py
│       │   │       └── audit_log.py
│       │   │
│       │   ├── schemas/
│       │   │   ├── auth.py
│       │   │   ├── project.py
│       │   │   ├── document.py
│       │   │   ├── analysis_run.py
│       │   │   ├── agent.py
│       │   │   ├── report.py
│       │   │   └── common.py
│       │   │
│       │   ├── api/
│       │   │   ├── deps.py
│       │   │   └── v1/
│       │   │       ├── router.py
│       │   │       ├── auth_routes.py
│       │   │       ├── project_routes.py
│       │   │       ├── document_routes.py
│       │   │       ├── analysis_routes.py
│       │   │       ├── agent_routes.py
│       │   │       └── report_routes.py
│       │   │
│       │   ├── services/
│       │   │   ├── auth_service.py
│       │   │   ├── project_service.py
│       │   │   ├── document_service.py
│       │   │   ├── parsing_service.py
│       │   │   ├── embedding_service.py
│       │   │   ├── vector_search_service.py
│       │   │   ├── llm_service.py
│       │   │   ├── band_service.py
│       │   │   ├── workflow_service.py
│       │   │   ├── report_service.py
│       │   │   └── storage_service.py
│       │   │
│       │   ├── agents/
│       │   │   ├── base_agent.py
│       │   │   ├── literature_review_agent.py
│       │   │   ├── research_gap_agent.py
│       │   │   ├── citation_agent.py
│       │   │   ├── methodology_agent.py
│       │   │   ├── results_agent.py
│       │   │   ├── defense_agent.py
│       │   │   └── report_agent.py
│       │   │
│       │   ├── workflows/
│       │   │   ├── thesis_review_state.py
│       │   │   ├── thesis_review_graph.py
│       │   │   └── nodes/
│       │   │       ├── parse_documents_node.py
│       │   │       ├── literature_node.py
│       │   │       ├── gap_node.py
│       │   │       ├── citation_node.py
│       │   │       ├── methodology_node.py
│       │   │       ├── results_node.py
│       │   │       ├── defense_node.py
│       │   │       └── report_node.py
│       │   │
│       │   ├── parsers/
│       │   │   ├── pdf_parser.py
│       │   │   ├── docx_parser.py
│       │   │   ├── txt_parser.py
│       │   │   ├── bibtex_parser.py
│       │   │   └── csv_parser.py
│       │   │
│       │   ├── prompts/
│       │   │   ├── system_prompts.py
│       │   │   ├── literature_review_prompt.py
│       │   │   ├── research_gap_prompt.py
│       │   │   ├── citation_prompt.py
│       │   │   ├── methodology_prompt.py
│       │   │   ├── results_prompt.py
│       │   │   ├── defense_prompt.py
│       │   │   └── report_prompt.py
│       │   │
│       │   ├── workers/
│       │   │   ├── celery_app.py
│       │   │   └── tasks.py
│       │   │
│       │   └── tests/
│       │       ├── test_projects.py
│       │       ├── test_documents.py
│       │       ├── test_agents.py
│       │       └── test_workflow.py
│
├── packages/
│   ├── shared-types/
│   │   ├── package.json
│   │   └── src/
│   │       ├── project.ts
│   │       ├── agent.ts
│   │       └── report.ts
│   │
│   └── config/
│       ├── eslint/
│       └── tsconfig/
│
├── infra/
│   ├── supabase/
│   │   ├── schema.sql
│   │   ├── policies.sql
│   │   └── seed.sql
│   │
│   ├── docker/
│   │   ├── api.Dockerfile
│   │   └── worker.Dockerfile
│   │
│   └── scripts/
│       ├── setup-dev.sh
│       ├── reset-db.sh
│       └── seed-demo-data.sh
│
└── docs/
    ├── PRD.md
    ├── TECHNICAL_ARCHITECTURE.md
    ├── API_SPEC.md
    ├── AGENT_DESIGN.md
    └── DEMO_SCRIPT.md
```

## 8. Database Design Overview

The database is centered around five concepts:

1. Users
2. Thesis projects
3. Documents and parsed chunks
4. Analysis runs and agent collaboration
5. Reports and action tasks

## 9. Database Schema

Database: PostgreSQL
Recommended extensions:

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;
```

## 9.1 Table: user_profiles

Stores application-level profile data for each authenticated user.

Supabase Auth stores the actual login account. This table stores product-specific user information.

| Field        | Type        | Required | Description                                       |
| ------------ | ----------- | -------: | ------------------------------------------------- |
| id           | uuid        |      Yes | Internal profile ID                               |
| auth_user_id | uuid        |      Yes | References the auth provider user ID              |
| full_name    | text        |       No | User’s full name                                  |
| email        | text        |      Yes | User email                                        |
| role         | text        |      Yes | User role: student, researcher, supervisor, admin |
| institution  | text        |       No | University or organization name                   |
| avatar_url   | text        |       No | Profile image URL                                 |
| created_at   | timestamptz |      Yes | Profile creation time                             |
| updated_at   | timestamptz |      Yes | Last profile update time                          |

Relationship:

```text
One user_profile has many thesis_projects.
```

## 9.2 Table: thesis_projects

Stores each thesis or research project created by a user.

| Field               | Type        | Required | Description                                                    |
| ------------------- | ----------- | -------: | -------------------------------------------------------------- |
| id                  | uuid        |      Yes | Project ID                                                     |
| owner_id            | uuid        |      Yes | References user_profiles.id                                    |
| title               | text        |      Yes | Thesis title                                                   |
| research_area       | text        |       No | Example: AI, NLP, cybersecurity, bioinformatics                |
| thesis_stage        | text        |       No | proposal, literature_review, methodology, results, final_draft |
| problem_statement   | text        |       No | User-provided problem statement                                |
| research_gap        | text        |       No | User-provided research gap                                     |
| objectives          | jsonb       |       No | List of research objectives                                    |
| methodology_summary | text        |       No | Short methodology description                                  |
| dataset_summary     | text        |       No | Dataset or experiment summary                                  |
| results_summary     | text        |       No | Result summary                                                 |
| status              | text        |      Yes | draft, ready_for_review, reviewing, completed, archived        |
| created_at          | timestamptz |      Yes | Project creation time                                          |
| updated_at          | timestamptz |      Yes | Last update time                                               |

Relationship:

```text
One thesis_project belongs to one user_profile.
One thesis_project has many documents.
One thesis_project has many analysis_runs.
One thesis_project has many reports.
```

## 9.3 Table: documents

Stores uploaded files and manually pasted content.

| Field          | Type        | Required | Description                                                |
| -------------- | ----------- | -------: | ---------------------------------------------------------- |
| id             | uuid        |      Yes | Document ID                                                |
| project_id     | uuid        |      Yes | References thesis_projects.id                              |
| owner_id       | uuid        |      Yes | References user_profiles.id                                |
| document_type  | text        |      Yes | thesis_draft, reference_file, result_file, feedback, other |
| file_name      | text        |       No | Original file name                                         |
| file_mime_type | text        |       No | PDF, DOCX, TXT, CSV, BibTeX                                |
| storage_path   | text        |       No | Path in Supabase Storage                                   |
| raw_text       | text        |       No | Extracted or pasted raw text                               |
| parse_status   | text        |      Yes | pending, parsed, failed                                    |
| parse_error    | text        |       No | Error message if parsing fails                             |
| metadata       | jsonb       |       No | Page count, word count, file size, etc.                    |
| created_at     | timestamptz |      Yes | Upload time                                                |
| updated_at     | timestamptz |      Yes | Last update time                                           |

Relationship:

```text
One document belongs to one thesis_project.
One document has many document_chunks.
```

## 9.4 Table: document_chunks

Stores parsed pieces of text from uploaded documents.

This table is important for retrieval and citation checking.

| Field         | Type        | Required | Description                          |
| ------------- | ----------- | -------: | ------------------------------------ |
| id            | uuid        |      Yes | Chunk ID                             |
| document_id   | uuid        |      Yes | References documents.id              |
| project_id    | uuid        |      Yes | References thesis_projects.id        |
| chunk_index   | integer     |      Yes | Order of chunk inside document       |
| section_title | text        |       No | Detected heading or section name     |
| content       | text        |      Yes | Chunk text                           |
| token_count   | integer     |       No | Estimated token count                |
| page_number   | integer     |       No | Source page number if PDF            |
| embedding     | vector      |       No | Vector embedding for semantic search |
| metadata      | jsonb       |       No | Extra parser details                 |
| created_at    | timestamptz |      Yes | Creation time                        |

Relationship:

```text
One document_chunk belongs to one document.
Many chunks are searched by agents during analysis.
```

## 9.5 Table: references

Stores parsed bibliography entries.

| Field        | Type        | Required | Description                         |
| ------------ | ----------- | -------: | ----------------------------------- |
| id           | uuid        |      Yes | Reference ID                        |
| project_id   | uuid        |      Yes | References thesis_projects.id       |
| document_id  | uuid        |       No | Source BibTeX document if available |
| citation_key | text        |       No | Example: Dolhansky2020DFDC          |
| title        | text        |       No | Paper title                         |
| authors      | jsonb       |       No | List of authors                     |
| year         | integer     |       No | Publication year                    |
| venue        | text        |       No | Journal, conference, or source      |
| doi          | text        |       No | DOI if available                    |
| url          | text        |       No | Paper URL                           |
| abstract     | text        |       No | Abstract if provided                |
| raw_bibtex   | text        |       No | Original BibTeX entry               |
| metadata     | jsonb       |       No | Extra reference data                |
| created_at   | timestamptz |      Yes | Creation time                       |

Relationship:

```text
One thesis_project has many references.
References can be linked to claims through citation_checks.
```

## 9.6 Table: analysis_runs

Stores every time a user runs a thesis review.

| Field          | Type        | Required | Description                                            |
| -------------- | ----------- | -------: | ------------------------------------------------------ |
| id             | uuid        |      Yes | Analysis run ID                                        |
| project_id     | uuid        |      Yes | References thesis_projects.id                          |
| user_id        | uuid        |      Yes | References user_profiles.id                            |
| run_type       | text        |      Yes | full_review, gap_review, citation_review, defense_prep |
| status         | text        |      Yes | queued, running, completed, failed, cancelled          |
| started_at     | timestamptz |       No | Run start time                                         |
| completed_at   | timestamptz |       No | Run completion time                                    |
| error_message  | text        |       No | Error if run fails                                     |
| input_snapshot | jsonb       |       No | Project input at the time of run                       |
| config         | jsonb       |       No | Model, agents enabled, settings                        |
| created_at     | timestamptz |      Yes | Run creation time                                      |
| updated_at     | timestamptz |      Yes | Last update time                                       |

Relationship:

```text
One thesis_project has many analysis_runs.
One analysis_run has many agent_messages.
One analysis_run has many agent_findings.
One analysis_run may generate one report.
```

## 9.7 Table: agents

Stores agent definitions.

This lets you change prompts and configurations later without rewriting the database.

| Field          | Type        | Required | Description                          |
| -------------- | ----------- | -------: | ------------------------------------ |
| id             | uuid        |      Yes | Agent ID                             |
| name           | text        |      Yes | Human-readable name                  |
| slug           | text        |      Yes | Unique identifier                    |
| description    | text        |       No | What the agent does                  |
| system_prompt  | text        |      Yes | Agent system instruction             |
| model_provider | text        |       No | openai, gemini, aimlapi, featherless |
| model_name     | text        |       No | Model used by this agent             |
| temperature    | numeric     |       No | LLM creativity setting               |
| is_active      | boolean     |      Yes | Whether the agent is enabled         |
| created_at     | timestamptz |      Yes | Creation time                        |
| updated_at     | timestamptz |      Yes | Last update time                     |

Relationship:

```text
One agent can produce many agent_messages.
One agent can produce many agent_findings.
```

## 9.8 Table: agent_messages

Stores communication between agents.

This is one of the most important tables for the hackathon because it proves multi-agent collaboration.

| Field           | Type        | Required | Description                                         |
| --------------- | ----------- | -------: | --------------------------------------------------- |
| id              | uuid        |      Yes | Message ID                                          |
| run_id          | uuid        |      Yes | References analysis_runs.id                         |
| project_id      | uuid        |      Yes | References thesis_projects.id                       |
| from_agent_id   | uuid        |       No | References agents.id                                |
| to_agent_id     | uuid        |       No | References agents.id                                |
| message_type    | text        |      Yes | handoff, request, response, critique, final_summary |
| task            | text        |       No | Task being passed                                   |
| summary         | text        |      Yes | Human-readable message summary                      |
| payload         | jsonb       |       No | Structured context passed between agents            |
| band_message_id | text        |       No | External Band message ID                            |
| status          | text        |      Yes | pending, sent, received, failed                     |
| created_at      | timestamptz |      Yes | Message creation time                               |

Relationship:

```text
One analysis_run has many agent_messages.
Messages connect one agent to another agent.
```

## 9.9 Table: agent_findings

Stores structured outputs from each agent.

| Field          | Type        | Required | Description                                                                    |
| -------------- | ----------- | -------: | ------------------------------------------------------------------------------ |
| id             | uuid        |      Yes | Finding ID                                                                     |
| run_id         | uuid        |      Yes | References analysis_runs.id                                                    |
| project_id     | uuid        |      Yes | References thesis_projects.id                                                  |
| agent_id       | uuid        |      Yes | References agents.id                                                           |
| finding_type   | text        |      Yes | gap_issue, citation_warning, method_mismatch, result_warning, defense_question |
| severity       | text        |      Yes | low, medium, high, critical                                                    |
| title          | text        |      Yes | Short title of finding                                                         |
| description    | text        |      Yes | Detailed explanation                                                           |
| evidence       | jsonb       |       No | Source sections, chunks, citations, or references                              |
| recommendation | text        |       No | Suggested fix                                                                  |
| score_impact   | integer     |       No | How much this affects total score                                              |
| created_at     | timestamptz |      Yes | Creation time                                                                  |

Relationship:

```text
One agent produces many findings.
Findings are used by the final report.
```

## 9.10 Table: citation_checks

Stores claim-to-citation validation results.

| Field           | Type        | Required | Description                                 |
| --------------- | ----------- | -------: | ------------------------------------------- |
| id              | uuid        |      Yes | Citation check ID                           |
| run_id          | uuid        |      Yes | References analysis_runs.id                 |
| project_id      | uuid        |      Yes | References thesis_projects.id               |
| reference_id    | uuid        |       No | References references.id                    |
| claim_text      | text        |      Yes | Thesis claim being checked                  |
| citation_key    | text        |       No | Citation key used in thesis                 |
| support_level   | text        |      Yes | strong, partial, weak, unsupported, unknown |
| explanation     | text        |       No | Why the support level was assigned          |
| source_chunk_id | uuid        |       No | References document_chunks.id               |
| created_at      | timestamptz |      Yes | Creation time                               |

Relationship:

```text
One analysis_run has many citation_checks.
Citation checks may link a thesis claim to a reference.
```

## 9.11 Table: reports

Stores final generated thesis review reports.

| Field             | Type        | Required | Description                    |
| ----------------- | ----------- | -------: | ------------------------------ |
| id                | uuid        |      Yes | Report ID                      |
| run_id            | uuid        |      Yes | References analysis_runs.id    |
| project_id        | uuid        |      Yes | References thesis_projects.id  |
| user_id           | uuid        |      Yes | References user_profiles.id    |
| title             | text        |      Yes | Report title                   |
| overall_score     | integer     |       No | Thesis health score out of 100 |
| gap_score         | integer     |       No | Research gap score             |
| citation_score    | integer     |       No | Citation support score         |
| methodology_score | integer     |       No | Methodology consistency score  |
| results_score     | integer     |       No | Results interpretation score   |
| defense_score     | integer     |       No | Defense readiness score        |
| executive_summary | text        |       No | Short summary                  |
| report_markdown   | text        |      Yes | Full report in markdown        |
| report_json       | jsonb       |       No | Structured report sections     |
| status            | text        |      Yes | draft, generated, failed       |
| created_at        | timestamptz |      Yes | Report creation time           |
| updated_at        | timestamptz |      Yes | Last update time               |

Relationship:

```text
One analysis_run generates one report.
One thesis_project can have many reports over time.
```

## 9.12 Table: action_tasks

Stores recommended improvement tasks generated by the agents.

| Field       | Type        | Required | Description                                                          |
| ----------- | ----------- | -------: | -------------------------------------------------------------------- |
| id          | uuid        |      Yes | Task ID                                                              |
| project_id  | uuid        |      Yes | References thesis_projects.id                                        |
| run_id      | uuid        |       No | References analysis_runs.id                                          |
| report_id   | uuid        |       No | References reports.id                                                |
| title       | text        |      Yes | Task title                                                           |
| description | text        |       No | Task details                                                         |
| category    | text        |      Yes | literature, gap, citation, methodology, results, defense, formatting |
| priority    | text        |      Yes | low, medium, high, urgent                                            |
| status      | text        |      Yes | open, in_progress, completed, dismissed                              |
| due_date    | date        |       No | Optional due date                                                    |
| created_at  | timestamptz |      Yes | Creation time                                                        |
| updated_at  | timestamptz |      Yes | Last update time                                                     |

Relationship:

```text
One report can generate many action_tasks.
Users can track thesis improvements through tasks.
```

## 9.13 Table: supervisor_feedback

Stores feedback from supervisors or mentors.

This is nice-to-have for MVP but should be included in the scalable schema.

| Field         | Type        | Required | Description                              |
| ------------- | ----------- | -------: | ---------------------------------------- |
| id            | uuid        |      Yes | Feedback ID                              |
| project_id    | uuid        |      Yes | References thesis_projects.id            |
| user_id       | uuid        |      Yes | References user_profiles.id              |
| feedback_text | text        |      Yes | Raw supervisor feedback                  |
| source        | text        |       No | meeting, email, document_comment, manual |
| feedback_date | date        |       No | When feedback was received               |
| parsed_tasks  | jsonb       |       No | Tasks extracted from feedback            |
| created_at    | timestamptz |      Yes | Creation time                            |

Relationship:

```text
One thesis_project can have many supervisor_feedback entries.
Feedback can later become action_tasks.
```

## 9.14 Table: audit_logs

Stores important system events for debugging and traceability.

| Field       | Type        | Required | Description                                            |
| ----------- | ----------- | -------: | ------------------------------------------------------ |
| id          | uuid        |      Yes | Audit log ID                                           |
| user_id     | uuid        |       No | References user_profiles.id                            |
| project_id  | uuid        |       No | References thesis_projects.id                          |
| action      | text        |      Yes | upload_document, start_analysis, generate_report, etc. |
| entity_type | text        |       No | project, document, run, report                         |
| entity_id   | uuid        |       No | ID of related entity                                   |
| metadata    | jsonb       |       No | Extra event details                                    |
| created_at  | timestamptz |      Yes | Event time                                             |

Relationship:

```text
Audit logs track important user and system actions.
```

## 10. Simplified SQL Schema

```sql
CREATE TABLE user_profiles (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    auth_user_id uuid UNIQUE NOT NULL,
    full_name text,
    email text NOT NULL,
    role text NOT NULL DEFAULT 'student',
    institution text,
    avatar_url text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE thesis_projects (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id uuid NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    title text NOT NULL,
    research_area text,
    thesis_stage text,
    problem_statement text,
    research_gap text,
    objectives jsonb,
    methodology_summary text,
    dataset_summary text,
    results_summary text,
    status text NOT NULL DEFAULT 'draft',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE documents (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id uuid NOT NULL REFERENCES thesis_projects(id) ON DELETE CASCADE,
    owner_id uuid NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    document_type text NOT NULL,
    file_name text,
    file_mime_type text,
    storage_path text,
    raw_text text,
    parse_status text NOT NULL DEFAULT 'pending',
    parse_error text,
    metadata jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE document_chunks (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id uuid NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    project_id uuid NOT NULL REFERENCES thesis_projects(id) ON DELETE CASCADE,
    chunk_index integer NOT NULL,
    section_title text,
    content text NOT NULL,
    token_count integer,
    page_number integer,
    embedding vector(1536),
    metadata jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE references (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id uuid NOT NULL REFERENCES thesis_projects(id) ON DELETE CASCADE,
    document_id uuid REFERENCES documents(id) ON DELETE SET NULL,
    citation_key text,
    title text,
    authors jsonb,
    year integer,
    venue text,
    doi text,
    url text,
    abstract text,
    raw_bibtex text,
    metadata jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE analysis_runs (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id uuid NOT NULL REFERENCES thesis_projects(id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    run_type text NOT NULL DEFAULT 'full_review',
    status text NOT NULL DEFAULT 'queued',
    started_at timestamptz,
    completed_at timestamptz,
    error_message text,
    input_snapshot jsonb,
    config jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE agents (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    name text NOT NULL,
    slug text UNIQUE NOT NULL,
    description text,
    system_prompt text NOT NULL,
    model_provider text,
    model_name text,
    temperature numeric DEFAULT 0.2,
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE agent_messages (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id uuid NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
    project_id uuid NOT NULL REFERENCES thesis_projects(id) ON DELETE CASCADE,
    from_agent_id uuid REFERENCES agents(id) ON DELETE SET NULL,
    to_agent_id uuid REFERENCES agents(id) ON DELETE SET NULL,
    message_type text NOT NULL,
    task text,
    summary text NOT NULL,
    payload jsonb,
    band_message_id text,
    status text NOT NULL DEFAULT 'pending',
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE agent_findings (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id uuid NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
    project_id uuid NOT NULL REFERENCES thesis_projects(id) ON DELETE CASCADE,
    agent_id uuid NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    finding_type text NOT NULL,
    severity text NOT NULL DEFAULT 'medium',
    title text NOT NULL,
    description text NOT NULL,
    evidence jsonb,
    recommendation text,
    score_impact integer,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE citation_checks (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id uuid NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
    project_id uuid NOT NULL REFERENCES thesis_projects(id) ON DELETE CASCADE,
    reference_id uuid REFERENCES references(id) ON DELETE SET NULL,
    claim_text text NOT NULL,
    citation_key text,
    support_level text NOT NULL,
    explanation text,
    source_chunk_id uuid REFERENCES document_chunks(id) ON DELETE SET NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE reports (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id uuid NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
    project_id uuid NOT NULL REFERENCES thesis_projects(id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    title text NOT NULL,
    overall_score integer,
    gap_score integer,
    citation_score integer,
    methodology_score integer,
    results_score integer,
    defense_score integer,
    executive_summary text,
    report_markdown text NOT NULL,
    report_json jsonb,
    status text NOT NULL DEFAULT 'generated',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE action_tasks (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id uuid NOT NULL REFERENCES thesis_projects(id) ON DELETE CASCADE,
    run_id uuid REFERENCES analysis_runs(id) ON DELETE SET NULL,
    report_id uuid REFERENCES reports(id) ON DELETE SET NULL,
    title text NOT NULL,
    description text,
    category text NOT NULL,
    priority text NOT NULL DEFAULT 'medium',
    status text NOT NULL DEFAULT 'open',
    due_date date,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE supervisor_feedback (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id uuid NOT NULL REFERENCES thesis_projects(id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    feedback_text text NOT NULL,
    source text,
    feedback_date date,
    parsed_tasks jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE audit_logs (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id uuid REFERENCES user_profiles(id) ON DELETE SET NULL,
    project_id uuid REFERENCES thesis_projects(id) ON DELETE SET NULL,
    action text NOT NULL,
    entity_type text,
    entity_id uuid,
    metadata jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);
```

## 11. Important Indexes

Add these indexes for performance:

```sql
CREATE INDEX idx_projects_owner_id ON thesis_projects(owner_id);
CREATE INDEX idx_documents_project_id ON documents(project_id);
CREATE INDEX idx_chunks_project_id ON document_chunks(project_id);
CREATE INDEX idx_references_project_id ON references(project_id);
CREATE INDEX idx_runs_project_id ON analysis_runs(project_id);
CREATE INDEX idx_agent_messages_run_id ON agent_messages(run_id);
CREATE INDEX idx_agent_findings_run_id ON agent_findings(run_id);
CREATE INDEX idx_reports_project_id ON reports(project_id);
CREATE INDEX idx_tasks_project_id ON action_tasks(project_id);

CREATE INDEX idx_document_chunks_embedding
ON document_chunks
USING ivfflat (embedding vector_cosine_ops);
```

Note: The embedding dimension must match your embedding model. If your embedding model outputs 768 dimensions, use:

```sql
embedding vector(768)
```

If it outputs 1536 dimensions, use:

```sql
embedding vector(1536)
```

## 12. API Design

## 12.1 Project APIs

```text
POST   /api/v1/projects
GET    /api/v1/projects
GET    /api/v1/projects/{project_id}
PATCH  /api/v1/projects/{project_id}
DELETE /api/v1/projects/{project_id}
```

## 12.2 Document APIs

```text
POST   /api/v1/projects/{project_id}/documents
GET    /api/v1/projects/{project_id}/documents
GET    /api/v1/documents/{document_id}
DELETE /api/v1/documents/{document_id}
POST   /api/v1/documents/{document_id}/parse
```

## 12.3 Analysis APIs

```text
POST   /api/v1/projects/{project_id}/analysis-runs
GET    /api/v1/projects/{project_id}/analysis-runs
GET    /api/v1/analysis-runs/{run_id}
GET    /api/v1/analysis-runs/{run_id}/status
GET    /api/v1/analysis-runs/{run_id}/agent-messages
GET    /api/v1/analysis-runs/{run_id}/findings
```

## 12.4 Report APIs

```text
GET    /api/v1/projects/{project_id}/reports
GET    /api/v1/reports/{report_id}
POST   /api/v1/reports/{report_id}/export
```

## 12.5 Task APIs

```text
GET    /api/v1/projects/{project_id}/tasks
PATCH  /api/v1/tasks/{task_id}
DELETE /api/v1/tasks/{task_id}
```

## 13. Environment Variables

## 13.1 Frontend Environment Variables

File:

```text
apps/web/.env.local
```

Variables:

```env
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1

NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
```

### Explanation

| Variable                      | Purpose                               |
| ----------------------------- | ------------------------------------- |
| NEXT_PUBLIC_APP_URL           | Public URL of the frontend            |
| NEXT_PUBLIC_API_BASE_URL      | Backend API base URL                  |
| NEXT_PUBLIC_SUPABASE_URL      | Supabase project URL                  |
| NEXT_PUBLIC_SUPABASE_ANON_KEY | Public Supabase key for frontend auth |

## 13.2 Backend Environment Variables

File:

```text
apps/api/.env
```

Variables:

```env
APP_ENV=development
APP_NAME=ThesisForge
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/thesisforge
ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/thesisforge

SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_JWT_SECRET=
SUPABASE_STORAGE_BUCKET=thesisforge-documents

REDIS_URL=redis://localhost:6379/0

LLM_PROVIDER=openai
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

GEMINI_API_KEY=
AIML_API_KEY=
FEATHERLESS_API_KEY=

BAND_API_KEY=
BAND_PROJECT_ID=
BAND_WORKSPACE_ID=
BAND_BASE_URL=

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

MAX_UPLOAD_MB=25
MAX_CHUNKS_PER_DOCUMENT=300
MAX_AGENT_RETRIES=2

LOG_LEVEL=INFO
SENTRY_DSN=
```

### Explanation

| Variable                  | Purpose                                       |
| ------------------------- | --------------------------------------------- |
| APP_ENV                   | development, staging, or production           |
| DATABASE_URL              | Main database connection                      |
| SUPABASE_SERVICE_ROLE_KEY | Backend-only key for storage/admin operations |
| SUPABASE_JWT_SECRET       | Used to verify Supabase JWTs                  |
| REDIS_URL                 | Redis connection for jobs                     |
| LLM_PROVIDER              | Selects active model provider                 |
| OPENAI_API_KEY            | OpenAI key if using OpenAI                    |
| BAND_API_KEY              | Key for Band integration                      |
| BAND_PROJECT_ID           | Band project identifier                       |
| MAX_UPLOAD_MB             | Upload size limit                             |
| MAX_AGENT_RETRIES         | Retry count for failed agent calls            |
| SENTRY_DSN                | Optional error tracking                       |

## 14. Configuration Notes Before Building

## 14.1 Never Expose Service Role Keys

The Supabase service role key must only be used in the backend. Never put it in the frontend.

Safe for frontend:

```text
NEXT_PUBLIC_SUPABASE_ANON_KEY
```

Not safe for frontend:

```text
SUPABASE_SERVICE_ROLE_KEY
```

## 14.2 Embedding Dimension Must Match Database

If you choose an embedding model with 1536 dimensions, your database column should be:

```sql
embedding vector(1536)
```

If you switch to another embedding model, update this dimension before storing vectors.

## 14.3 Use Background Jobs for Long Analysis

For early demo, synchronous analysis is acceptable.

For real SaaS, use:

```text
FastAPI → Celery Task → Redis Queue → Worker → Database Updates
```

This prevents request timeout issues.

## 14.4 Store Agent Outputs as JSON

Do not store only plain text. Each agent should return structured JSON.

Example:

```json
{
  "score": 72,
  "findings": [
    {
      "severity": "high",
      "title": "Research gap is too broad",
      "description": "The gap mentions multimodal deepfake detection generally but does not clearly isolate interpretability.",
      "recommendation": "Focus the gap on interpretable multimodal reasoning."
    }
  ]
}
```

This makes reports, charts, filtering, and tasks easier.

## 14.5 Keep Prompts Versioned

Agent prompts will change often. Store prompt versions in code for MVP. Later, move them to the database.

A future table could be:

```text
agent_prompt_versions
```

For MVP, code-based prompts are simpler.

## 14.6 Use Row Level Security Later

For hackathon MVP, backend-level authorization is enough if only the backend talks to the database.

For production SaaS, enable Row Level Security policies so users can only access their own projects, documents, reports, and tasks.

## 14.7 Keep File Uploads Private

Uploaded thesis files may contain unpublished research. Store them in a private bucket and generate signed URLs only when needed.

## 14.8 Add Disclaimers

Because this is an academic tool, include a clear disclaimer:

```text
ThesisForge is a research review assistant. It does not replace supervisor review and should not be used to generate dishonest academic work.
```

## 15. MVP Build Order

Build in this order:

### Step 1: Backend Foundation

* FastAPI app setup
* Database connection
* Project CRUD
* Document CRUD
* Basic auth verification

### Step 2: File Input

* Manual text input first
* PDF parser second
* DOCX parser third
* BibTeX parser fourth

### Step 3: Agents Without Band

First make agents work locally.

* Literature Review Agent
* Research Gap Agent
* Methodology Agent
* Defense Agent

### Step 4: Add Band

After the agent workflow works, add Band communication between agents.

Save all Band messages to `agent_messages`.

### Step 5: Add Frontend

* Dashboard
* Project creation
* Thesis input page
* Run analysis button
* Agent collaboration timeline
* Final report page

### Step 6: Demo Polish

* Add sample thesis data
* Add loading states
* Add visible agent messages
* Add README
* Add demo video script

## 16. MVP Deployment Architecture

## 16.1 Simple Deployment

```text
Frontend: Vercel
Backend: Render or Railway
Database: Supabase
Storage: Supabase Storage
Redis: Upstash Redis or Railway Redis
```

## 16.2 Local Development

Use Docker Compose:

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: thesisforge
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  api:
    build: ./apps/api
    ports:
      - "8000:8000"
    env_file:
      - ./apps/api/.env
    depends_on:
      - postgres
      - redis
```

## 17. Security Considerations

### Authentication

* Use Supabase Auth for login.
* Backend verifies JWT before processing requests.
* Every project query must check `owner_id`.

### Authorization

For MVP:

```text
User can only access projects where thesis_projects.owner_id = current_user.id
```

For future:

* Add organizations
* Add team roles
* Add supervisor access
* Add project sharing permissions

### File Security

* Store uploaded files in private storage.
* Limit upload size.
* Validate file type.
* Scan file extension and MIME type.
* Do not execute uploaded files.

### LLM Safety

* Do not let user content override system instructions.
* Wrap user thesis text as data, not instruction.
* Ask agents to cite provided sections.
* Log model input/output for debugging, but avoid exposing private content publicly.

## 18. Scalability Plan

## 18.1 MVP Scale

Good enough for:

* Hackathon demo
* Dozens of users
* Small thesis files
* Manual project review

## 18.2 Early SaaS Scale

Add:

* Background workers
* Queue-based processing
* Report caching
* Prompt versioning
* Usage limits
* Better vector indexing
* Error tracking
* Billing

## 18.3 Later SaaS Scale

Add:

* Organization accounts
* Team collaboration
* Supervisor review dashboard
* Zotero integration
* Google Drive integration
* Multi-document semantic search
* Report version comparison
* Advanced analytics

## 19. What Not to Overbuild in Version One

Do not build these in the first version:

1. Payment system
2. Team workspace
3. Supervisor dashboard
4. Zotero/Mendeley sync
5. Google Scholar crawler
6. Full plagiarism detection
7. Full LaTeX compiler
8. Real-time collaborative editing
9. Mobile app
10. Complex admin panel
11. Multi-tenant organization billing
12. Kubernetes infrastructure

The MVP should prove one thing clearly:

```text
A thesis student can upload or paste thesis material, run a multi-agent Band-powered review, and receive an actionable research quality report.
```

## 20. Recommended First Sprint

### Sprint Goal

Build a working end-to-end demo.

### Backend Tasks

* Set up FastAPI
* Create database schema
* Add project creation API
* Add document text input API
* Add four agents
* Add LangGraph workflow
* Add Band message logging
* Generate final report

### Frontend Tasks

* Set up Next.js
* Build project creation page
* Build thesis input page
* Build run analysis button
* Build agent timeline
* Build report page

### Demo Tasks

* Create sample thesis input
* Add README
* Add screenshots
* Record video
* Prepare submission text

## 21. Final Architecture Recommendation

For the hackathon and future SaaS potential, build ThesisForge as:

```text
Frontend: Next.js + Tailwind + shadcn/ui
Backend: FastAPI + Pydantic + SQLAlchemy
Agents: LangGraph
Agent Collaboration: Band
Database: Supabase Postgres
Vector Search: pgvector
Storage: Supabase Storage
Queue: Redis + Celery
Deployment: Vercel + Render/Railway + Supabase
```

This gives you the best balance between speed, clarity, and scalability.
