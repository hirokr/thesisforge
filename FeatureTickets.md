# ThesisForge Feature Ticket List

## Multi-Agent Research Workflow Assistant

## Priority Labels

* **Must-have for launch:** Required for MVP and hackathon demo.
* **Should-have:** Important, but can be added after the core MVP works.
* **Nice-to-have:** Useful for polish or future SaaS expansion.

---

# Epic 1: Project Foundation

## TF-001: Initialize Monorepo Project Structure

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Create the initial monorepo structure for ThesisForge with separate frontend and backend applications. The frontend should use Next.js, Tailwind CSS, and shadcn/ui. The backend should use FastAPI. Include shared configuration files, environment examples, README, and basic local development setup.

**Acceptance Criteria:**

* A root `thesisforge/` repository exists.
* `apps/web/` contains a working Next.js app.
* `apps/api/` contains a working FastAPI app.
* Root `.gitignore` is configured.
* `.env.example` files exist for frontend and backend.
* `README.md` explains how to run frontend and backend locally.
* Frontend starts successfully on port `3000`.
* Backend starts successfully on port `8000`.
* Backend exposes a health check route at `/health`.

**Dependencies:**
None.

**AI Coding Prompt:**
Build the initial ThesisForge monorepo with `apps/web` for a Next.js frontend and `apps/api` for a FastAPI backend. Add Tailwind CSS and shadcn/ui to the frontend. Add a `/health` endpoint to the backend. Include `.env.example`, `.gitignore`, and README setup instructions.

---

## TF-002: Configure Global Design System

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Implement the ThesisForge design system in the frontend using Tailwind CSS. Add brand colors, typography, spacing, border radius, shadows, and reusable UI tokens.

**Acceptance Criteria:**

* Tailwind config includes ThesisForge colors:

  * Primary Navy `#1E3A5F`
  * Primary Blue `#2563EB`
  * Soft Blue `#DBEAFE`
  * Research Violet `#7C3AED`
  * Background `#F8FAFC`
  * Border `#E2E8F0`
  * Success `#16A34A`
  * Warning `#F59E0B`
  * Danger `#DC2626`
* App uses Inter or system sans-serif font.
* Global app background is `#F8FAFC`.
* Shared style tokens exist for cards, buttons, inputs, badges, and modals.
* Basic responsive layout rules are applied.

**Dependencies:**
TF-001.

**AI Coding Prompt:**
Implement the ThesisForge design system in the Next.js frontend. Configure Tailwind with the provided color palette, typography, spacing, radius, and shadow rules. Create reusable base styles for buttons, cards, inputs, badges, and modals.

---

## TF-003: Create Shared Frontend Layout

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Build the authenticated app shell with sidebar navigation, top navbar, and main content area. This layout will wrap dashboard, project, upload, review, and report pages.

**Acceptance Criteria:**

* App shell includes sidebar and top navbar.
* Sidebar contains links:

  * Dashboard
  * Projects
  * Reports
  * Settings
* Sidebar is collapsible or mobile-friendly.
* Main content area has max width and consistent padding.
* Active route is visually highlighted.
* Layout works on desktop and mobile.

**Dependencies:**
TF-001, TF-002.

**AI Coding Prompt:**
Create the authenticated app shell for ThesisForge with a sidebar, top navbar, and main content container. Add navigation links for Dashboard, Projects, Reports, and Settings. Make it responsive and visually aligned with the ThesisForge design system.

---

# Epic 2: Authentication and User Access

## TF-004: Configure Supabase Auth Client

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Set up Supabase Auth in the frontend. Add a Supabase client, environment variables, and session handling utilities.

**Acceptance Criteria:**

* Frontend has a reusable Supabase client.
* Environment variables are used:

  * `NEXT_PUBLIC_SUPABASE_URL`
  * `NEXT_PUBLIC_SUPABASE_ANON_KEY`
* Auth session can be read from the frontend.
* Access token can be retrieved for backend API calls.
* No private service role key is exposed in frontend code.

**Dependencies:**
TF-001.

**AI Coding Prompt:**
Set up Supabase Auth in the Next.js frontend. Create a reusable Supabase client using `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`. Add helper functions to get the current session and access token.

---

## TF-005: Build Signup Page

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Create a signup page where users can register using email and password.

**Acceptance Criteria:**

* Page exists at `/register`.
* Form fields:

  * Full name
  * Email
  * Password
  * Confirm password
* Form uses validation.
* Password and confirm password must match.
* On success, user sees a message to verify email or is redirected if session exists.
* Errors are shown in plain English.
* Page matches ThesisForge design system.

**Dependencies:**
TF-004.

**AI Coding Prompt:**
Build a signup page for ThesisForge at `/register` using Supabase Auth. Include full name, email, password, and confirm password fields with validation. Show friendly errors and success state. Use the ThesisForge design system.

---

## TF-006: Build Login Page

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Create a login page where users can sign in using email and password.

**Acceptance Criteria:**

* Page exists at `/login`.
* Form fields:

  * Email
  * Password
* Uses Supabase `signInWithPassword`.
* On success, redirects to `/dashboard`.
* Invalid login shows a generic error.
* Includes links to signup and forgot password pages.
* Uses ThesisForge design system.

**Dependencies:**
TF-004.

**AI Coding Prompt:**
Build a login page for ThesisForge at `/login` using Supabase Auth. Include email and password fields, friendly validation, redirect to `/dashboard` on success, and links to signup and forgot password.

---

## TF-007: Build Google OAuth Login

**Priority:** Should-have

**Status:** Done

**Description:**
Add “Continue with Google” login support using Supabase OAuth.

**Acceptance Criteria:**

* Login page includes Google login button.
* Signup page includes Google login button.
* Supabase OAuth redirect is configured.
* After successful OAuth, user lands on dashboard.
* Failed OAuth returns user to login with a friendly error.

**Dependencies:**
TF-004, TF-005, TF-006.

**AI Coding Prompt:**
Add Google OAuth login to the ThesisForge login and signup pages using Supabase Auth. Configure redirect handling so successful login sends users to `/dashboard`.

---

## TF-008: Implement Protected Routes

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Protect all authenticated app pages so only logged-in users can access them.

**Acceptance Criteria:**

* Unauthenticated users cannot access:

  * `/dashboard`
  * `/projects`
  * `/projects/new`
  * `/projects/:projectId`
  * `/settings`
* Unauthenticated users are redirected to `/login`.
* Authenticated users visiting `/login` or `/register` are redirected to `/dashboard`.
* Loading state appears while session is being checked.

**Dependencies:**
TF-004, TF-006.

**AI Coding Prompt:**
Implement route protection in the Next.js frontend. Redirect unauthenticated users from app routes to `/login`, and redirect logged-in users away from `/login` and `/register` to `/dashboard`.

---

## TF-009: Backend JWT Verification Middleware

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Add backend middleware/dependencies to verify Supabase JWT tokens on protected FastAPI routes.

**Acceptance Criteria:**

* Backend reads `Authorization: Bearer <token>`.
* Invalid or missing token returns `401`.
* Verified user ID is available to route handlers.
* Protected route dependency can be reused across APIs.
* No raw token is logged.

**Dependencies:**
TF-001, TF-004.

**AI Coding Prompt:**
Add Supabase JWT verification to the FastAPI backend. Create a reusable dependency that reads the bearer token, validates it, extracts the authenticated user ID, and blocks unauthorized requests with a safe 401 error.

---

# Epic 3: Database and Data Layer

## TF-010: Create Database Schema and Migrations

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Create the initial Postgres schema for ThesisForge using SQLAlchemy models and Alembic migrations.

**Acceptance Criteria:**

* Database models exist for:

  * user_profiles
  * thesis_projects
  * documents
  * document_chunks
  * references
  * analysis_runs
  * agents
  * agent_messages
  * agent_findings
  * citation_checks
  * reports
  * action_tasks
  * supervisor_feedback
  * audit_logs
* Alembic migration creates all tables.
* Foreign key relationships are correctly defined.
* UUID primary keys are used.
* `created_at` and `updated_at` fields are included where needed.

**Dependencies:**
TF-001.

**AI Coding Prompt:**
Create the ThesisForge database models in FastAPI using SQLAlchemy and Alembic. Add models and migrations for users, thesis projects, documents, chunks, references, analysis runs, agents, agent messages, findings, citation checks, reports, action tasks, supervisor feedback, and audit logs.

---

## TF-011: Seed Default Agents

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Create a seed script that inserts the default ThesisForge agents into the database.

**Acceptance Criteria:**

* Seed script inserts:

  * Literature Review Agent
  * Research Gap Agent
  * Citation Agent
  * Methodology Consistency Agent
  * Results Interpretation Agent
  * Defense Preparation Agent
  * Report Generator Agent
* Each agent has:

  * name
  * slug
  * description
  * system prompt
  * default model provider
  * default model name
  * temperature
  * active status
* Seed script is idempotent and does not create duplicates.

**Dependencies:**
TF-010.

**AI Coding Prompt:**
Create a seed script for ThesisForge that inserts the default agent records into the `agents` table. Make it idempotent so running it multiple times does not create duplicates.

---

## TF-012: Implement Row-Level Ownership Checks in Backend

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Before full database RLS is configured, backend services must enforce ownership checks for all project-related operations.

**Acceptance Criteria:**

* Every project API checks `owner_id`.
* Document APIs verify the document belongs to a project owned by the user.
* Analysis APIs verify the run belongs to a project owned by the user.
* Report APIs verify the report belongs to a project owned by the user.
* Unauthorized access returns safe `404`.
* Users cannot update `owner_id`.

**Dependencies:**
TF-009, TF-010.

**AI Coding Prompt:**
Add ownership checks to all ThesisForge backend services. Ensure users can only access projects, documents, analysis runs, reports, and tasks that belong to them. Return a safe 404 when access is denied.

---

## TF-013: Add Supabase/Postgres RLS Policies

**Priority:** Should-have

**Status:** Done

**Description:**
Add database Row-Level Security policies for user-owned data tables.

**Acceptance Criteria:**

* RLS is enabled on user-data tables.
* Users can only select their own projects.
* Users can only access documents for their own projects.
* Users can only access analysis runs, reports, findings, messages, and tasks for their own projects.
* Users cannot update ownership fields.
* Audit logs are not visible to normal users.

**Dependencies:**
TF-010, TF-012.

**AI Coding Prompt:**
Create SQL Row-Level Security policies for the ThesisForge Supabase/Postgres database. Enable RLS on all user-data tables and enforce project ownership for projects, documents, runs, reports, findings, messages, and tasks.

---

# Epic 4: Backend Core APIs

## TF-014: Create User Profile API

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Create backend logic to create and fetch the current user profile.

**Acceptance Criteria:**

* Endpoint exists: `GET /api/v1/me`.
* If authenticated user has no profile, backend creates one.
* Response includes:

  * id
  * auth_user_id
  * email
  * full_name
  * role
  * institution
* User profile is tied to Supabase Auth user ID.
* User cannot set themselves as admin.

**Dependencies:**
TF-009, TF-010.

**AI Coding Prompt:**
Build the `/api/v1/me` endpoint in FastAPI. It should return the current user profile, create one if missing, and prevent users from assigning privileged roles to themselves.

---

## TF-015: Create Project CRUD API

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Build backend APIs for creating, listing, viewing, updating, and deleting thesis projects.

**Acceptance Criteria:**

* Endpoints:

  * `POST /api/v1/projects`
  * `GET /api/v1/projects`
  * `GET /api/v1/projects/{project_id}`
  * `PATCH /api/v1/projects/{project_id}`
  * `DELETE /api/v1/projects/{project_id}`
* Project creation saves owner ID.
* Users only see their own projects.
* Update validates ownership.
* Delete removes or archives project safely.
* API uses Pydantic request/response schemas.

**Dependencies:**
TF-009, TF-010, TF-012, TF-014.

**AI Coding Prompt:**
Build the ThesisForge project CRUD API in FastAPI. Add endpoints to create, list, get, update, and delete thesis projects. Enforce authenticated ownership checks and use Pydantic schemas.

---

## TF-016: Create Document Metadata API

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Build backend APIs for creating, listing, viewing, and deleting document records.

**Acceptance Criteria:**

* Endpoints:

  * `GET /api/v1/projects/{project_id}/documents`
  * `GET /api/v1/documents/{document_id}`
  * `DELETE /api/v1/documents/{document_id}`
* Users only see documents from their own projects.
* Delete removes database document record.
* Related chunks are deleted through cascade.
* Safe errors are returned for missing or unauthorized documents.

**Dependencies:**
TF-015.

**AI Coding Prompt:**
Build document metadata APIs for ThesisForge in FastAPI. Users should be able to list, view, and delete documents that belong to their own projects only.

---

# Epic 5: Frontend Project Experience

## TF-017: Build Dashboard Page

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Create the dashboard page that shows a user’s thesis projects and recent activity.

**Acceptance Criteria:**

* Page exists at `/dashboard`.
* Fetches projects from backend.
* Shows project cards with:

  * title
  * research area
  * thesis stage
  * status
  * latest score if available
  * updated date
* Includes “Create project” button.
* Shows empty state if no projects exist.
* Handles loading and error states.

**Dependencies:**
TF-003, TF-008, TF-015.

**AI Coding Prompt:**
Build the ThesisForge dashboard page. Fetch the authenticated user’s projects from the backend and display them as cards. Include empty, loading, and error states plus a Create Project button.

---

## TF-018: Build Create Project Page

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Create the page where users can enter basic thesis project information.

**Acceptance Criteria:**

* Page exists at `/projects/new`.
* Form fields:

  * thesis title
  * research area
  * thesis stage
  * problem statement
  * research gap
  * objectives
  * methodology summary
  * dataset summary
  * results summary
* Required field: title.
* On submit, creates project through backend.
* Redirects to project overview on success.
* Shows field-level validation errors.

**Dependencies:**
TF-003, TF-008, TF-015.

**AI Coding Prompt:**
Build the Create Project page for ThesisForge. Add a validated form for thesis metadata and submit it to the backend project creation API. Redirect to the project overview after success.

---

## TF-019: Build Project Overview Page

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Create a project detail page that summarizes thesis metadata, uploaded documents, latest run, latest report, and next actions.

**Acceptance Criteria:**

* Page exists at `/projects/[projectId]`.
* Fetches project detail from backend.
* Displays thesis metadata.
* Shows document summary.
* Shows latest analysis status if available.
* Shows latest report score if available.
* Includes buttons:

  * Upload documents
  * Run thesis review
  * View latest report
* Handles unauthorized or missing project with safe error.

**Dependencies:**
TF-015, TF-016, TF-017.

**AI Coding Prompt:**
Build the ThesisForge project overview page. Fetch project details by ID, display thesis metadata and next actions, and include links to upload documents, run review, and view reports.

---

## TF-020: Build Edit Project Details

**Priority:** Should-have

**Status:** Done

**Description:**
Allow users to edit thesis project metadata after creation.

**Acceptance Criteria:**

* Edit mode exists on project overview or separate page.
* User can update:

  * research area
  * thesis stage
  * problem statement
  * research gap
  * objectives
  * methodology summary
  * dataset summary
  * results summary
* Save calls backend `PATCH /projects/{project_id}`.
* User sees success toast.
* Cancel returns to read-only view.

**Dependencies:**
TF-015, TF-019.

**AI Coding Prompt:**
Add edit project functionality to ThesisForge. Allow users to update thesis metadata from the project overview page and save changes through the backend PATCH project API.

---

# Epic 6: File Upload and Parsing

## TF-021: Build Pasted Text Document API

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Add backend API for users to paste thesis content directly instead of uploading files.

**Acceptance Criteria:**

* Endpoint exists: `POST /api/v1/projects/{project_id}/documents/text`.
* Request includes:

  * document_type
  * title
  * raw_text
* Backend validates project ownership.
* Backend saves document with `parse_status = parsed`.
* Backend creates initial chunks from text.
* Returns document ID and word count.

**Dependencies:**
TF-016.

**AI Coding Prompt:**
Build a FastAPI endpoint for adding pasted text as a ThesisForge document. Save the raw text, mark it parsed, split it into chunks, and return document metadata.

---

## TF-022: Build Text Chunking Service

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Create a service that splits thesis text into manageable chunks for agent analysis and future embedding.

**Acceptance Criteria:**

* Chunking service accepts raw text.
* Splits text into chunks of reasonable length.
* Preserves order using `chunk_index`.
* Stores chunk content in `document_chunks`.
* Attempts to preserve section headings if possible.
* Handles empty text safely.

**Dependencies:**
TF-010, TF-021.

**AI Coding Prompt:**
Create a text chunking service in the FastAPI backend. It should split document raw text into ordered chunks, store them in the `document_chunks` table, and preserve section titles when possible.

---

## TF-023: Build File Upload Backend API

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Create backend endpoint for uploading files to a project.

**Acceptance Criteria:**

* Endpoint exists: `POST /api/v1/projects/{project_id}/documents`.
* Accepts multipart file upload.
* Supports file types:

  * PDF
  * DOCX
  * TXT
  * BIB
  * CSV
* Rejects unsupported file types.
* Rejects files over 25 MB.
* Stores metadata in `documents`.
* Uploads file to private storage or local storage for MVP.
* Returns document metadata.

**Dependencies:**
TF-016.

**AI Coding Prompt:**
Build a file upload endpoint in FastAPI for ThesisForge. Accept PDF, DOCX, TXT, BIB, and CSV files up to 25 MB, validate ownership, store file metadata, upload the file to storage, and return document metadata.

---

## TF-024: Build PDF Parser

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Create a parser that extracts text from uploaded PDF thesis drafts.

**Acceptance Criteria:**

* Parser accepts PDF file path or bytes.
* Extracts text using PyMuPDF.
* Handles corrupted or unreadable PDFs.
* Detects empty scanned PDFs and returns friendly parse failure.
* Saves extracted text to `documents.raw_text`.
* Creates chunks through chunking service.
* Updates `parse_status`.

**Dependencies:**
TF-022, TF-023.

**AI Coding Prompt:**
Build a PDF parsing service using PyMuPDF. Extract text from uploaded PDFs, handle corrupted or scanned PDFs safely, save extracted text to the document record, create chunks, and update parse status.

---

## TF-025: Build DOCX Parser

**Priority:** Should-have

**Status:** Done

**Description:**
Create a parser that extracts text from uploaded DOCX files.

**Acceptance Criteria:**

* Parser accepts DOCX file.
* Extracts paragraph text.
* Handles empty or malformed DOCX files.
* Saves raw text.
* Creates chunks.
* Updates parse status.

**Dependencies:**
TF-022, TF-023.

**AI Coding Prompt:**
Build a DOCX parser for ThesisForge using python-docx. Extract text, handle malformed files safely, save raw text, generate chunks, and update the document parse status.

---

## TF-026: Build BibTeX Parser

**Priority:** Should-have

**Status:** Done

**Description:**
Create a parser for `.bib` files that extracts references into the `references` table.

**Acceptance Criteria:**

* Parser accepts BibTeX text or file.
* Extracts citation key, title, authors, year, venue, DOI, URL, and raw BibTeX.
* Handles malformed entries safely.
* Stores valid references in `references`.
* Links references to the project and source document.
* Updates document parse status.

**Dependencies:**
TF-023.

**AI Coding Prompt:**
Build a BibTeX parser for ThesisForge. Parse uploaded `.bib` files, extract reference metadata, store references in the database, handle malformed entries safely, and link references to the project and source document.

---

## TF-027: Build CSV Result Parser

**Priority:** Nice-to-have

**Status:** Done

**Description:**
Create a parser for result CSV files.

**Acceptance Criteria:**

* Parser accepts CSV files.
* Reads columns safely using pandas.
* Saves basic metadata:

  * row count
  * column names
  * sample rows
* Extracted summary can be used by Results Interpretation Agent.
* Handles malformed CSV files safely.

**Dependencies:**
TF-023.

**AI Coding Prompt:**
Build a CSV parser for ThesisForge result files. Parse CSV files safely, extract column names, row count, and sample rows, save metadata, and handle malformed files with friendly errors.

---

## TF-028: Build Upload Page

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Create frontend page for adding thesis materials through file upload or pasted text.

**Acceptance Criteria:**

* Page exists at `/projects/[projectId]/upload`.
* User can upload supported files.
* User can paste text manually.
* User selects document type:

  * thesis draft
  * reference file
  * result file
  * supervisor feedback
  * other
* Shows uploaded document list.
* Shows parse status.
* Shows upload errors clearly.
* Includes link back to project overview.

**Dependencies:**
TF-021, TF-023, TF-024.

**AI Coding Prompt:**
Build the ThesisForge upload page. Allow users to upload supported files or paste thesis text, select document type, submit to backend APIs, and display uploaded documents with parse status.

---

# Epic 7: LLM and Agent Services

## TF-029: Create Provider-Agnostic LLM Service

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Create a backend service that wraps LLM calls so agents do not directly depend on a specific provider.

**Acceptance Criteria:**

* `llm_service.py` exists.
* Supports at least one provider, preferably OpenAI.
* Accepts:

  * system prompt
  * user prompt
  * model
  * temperature
  * JSON mode preference if available
* Returns normalized response:

  * text
  * usage
  * provider
  * model
* Handles provider errors safely.
* Does not expose API keys in logs.

**Dependencies:**
TF-001.

**AI Coding Prompt:**
Create a provider-agnostic LLM service in the FastAPI backend. Implement OpenAI as the first provider. The service should accept prompts and model settings, return normalized responses, and handle provider errors safely without exposing secrets.

---

## TF-030: Create Base Agent Class

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Create a base class that all ThesisForge agents inherit from.

**Acceptance Criteria:**

* `BaseAgent` supports:

  * agent name
  * slug
  * system prompt
  * input validation
  * LLM call
  * output parsing
  * error handling
* Base agent can return structured findings.
* Base agent logs start, success, and failure.
* Base agent does not directly access unrelated project data.

**Dependencies:**
TF-029.

**AI Coding Prompt:**
Create a `BaseAgent` class for ThesisForge. It should define common behavior for all agents including prompt construction, LLM calls through the LLM service, output parsing, error handling, and structured result formatting.

---

## TF-031: Build Literature Review Agent

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Implement the Literature Review Agent, which reviews references and thesis content to extract themes and citation support.

**Acceptance Criteria:**

* Agent accepts project context, references, and document chunks.
* Outputs:

  * major literature themes
  * claim-support observations
  * weak or missing citation warnings
  * suggested literature gaps
* Saves findings to `agent_findings`.
* Sends handoff summary to Research Gap Agent through workflow state.
* Handles missing references gracefully.

**Dependencies:**
TF-030, TF-011.

**AI Coding Prompt:**
Implement the Literature Review Agent for ThesisForge. It should analyze project references and thesis chunks, identify major literature themes, weak citation support, and possible gaps, then return structured JSON findings.

---

## TF-032: Build Research Gap Agent

**Priority:** Must-have for launch

**Status:** Done

**Description:**
Implement the Research Gap Agent, which checks whether the research gap is clear, specific, supported, and aligned with the problem statement.

**Acceptance Criteria:**

* Agent accepts problem statement, research gap, objectives, and literature findings.
* Outputs:

  * gap quality score
  * weaknesses in current gap
  * improved research gap suggestion
  * missing evidence
* Saves findings to `agent_findings`.
* Handles empty research gap with actionable feedback.

**Dependencies:**
TF-031.

**AI Coding Prompt:**
Implement the Research Gap Agent for ThesisForge. It should evaluate the user’s research gap using literature findings and project context, then return a score, weaknesses, improved gap suggestion, and recommendations.

---

## TF-033: Build Citation Agent

**Priority:** Must-have for launch

**Description:**
Implement the Citation Agent, which checks whether thesis claims appear to be supported by provided references.

**Acceptance Criteria:**

* Agent accepts thesis chunks, references, and literature findings.
* Identifies unsupported or weakly supported claims.
* Creates records in `citation_checks`.
* Saves citation-related findings to `agent_findings`.
* Handles missing references gracefully.
* Does not claim external verification unless no web search is implemented.

**Dependencies:**
TF-026, TF-031.

**AI Coding Prompt:**
Implement the Citation Agent for ThesisForge. It should compare thesis claims with provided references, identify weak or unsupported claims, create citation check records, and return structured findings.

---

## TF-034: Build Methodology Consistency Agent

**Priority:** Must-have for launch

**Description:**
Implement the Methodology Consistency Agent, which checks whether the methodology matches the research gap, objectives, datasets, and results.

**Acceptance Criteria:**

* Agent accepts:

  * research gap
  * objectives
  * methodology summary
  * dataset summary
  * results summary
  * previous agent findings
* Outputs:

  * methodology consistency score
  * mismatch warnings
  * missing baselines or ablations
  * suggested fixes
* Saves findings to `agent_findings`.

**Dependencies:**
TF-032.

**AI Coding Prompt:**
Implement the Methodology Consistency Agent for ThesisForge. It should check whether the methodology aligns with the research gap, objectives, datasets, and results, and return structured findings with a score and recommendations.

---

## TF-035: Build Results Interpretation Agent

**Priority:** Should-have

**Description:**
Implement the Results Interpretation Agent, which reviews result summaries and identifies overclaiming, weak comparisons, or missing analysis.

**Acceptance Criteria:**

* Agent accepts results summary, methodology, objectives, and optional CSV metadata.
* Outputs:

  * results interpretation score
  * overclaiming warnings
  * missing comparison warnings
  * suggested discussion points
* Saves findings to `agent_findings`.
* Handles missing results summary gracefully.

**Dependencies:**
TF-034.

**AI Coding Prompt:**
Implement the Results Interpretation Agent for ThesisForge. It should review result summaries, detect overclaiming or missing comparisons, and return structured findings with a score and discussion suggestions.

---

## TF-036: Build Defense Preparation Agent

**Priority:** Must-have for launch

**Description:**
Implement the Defense Preparation Agent, which generates likely thesis panel questions based on weaknesses found by other agents.

**Acceptance Criteria:**

* Agent accepts all previous agent findings.
* Outputs:

  * likely defense questions
  * category per question
  * risk level per question
  * suggested answer points
* Saves findings to `agent_findings`.
* At least 8 defense questions are generated for a full review.

**Dependencies:**
TF-032, TF-034.

**AI Coding Prompt:**
Implement the Defense Preparation Agent for ThesisForge. It should use previous agent findings to generate likely thesis defense questions, risk levels, categories, and suggested answer points.

---

## TF-037: Build Report Generator Agent

**Priority:** Must-have for launch

**Description:**
Implement the Report Generator Agent, which combines all agent outputs into a final thesis health report.

**Acceptance Criteria:**

* Agent accepts all findings, citation checks, project metadata, and agent messages.
* Generates:

  * overall thesis health score
  * score breakdown
  * executive summary
  * major risks
  * priority fixes
  * defense questions
  * markdown report
  * structured JSON report
* Saves report to `reports`.
* Generates action tasks from priority fixes.
* Handles partial agent failures.

**Dependencies:**
TF-031, TF-032, TF-034, TF-036.

**AI Coding Prompt:**
Implement the Report Generator Agent for ThesisForge. It should combine all agent findings into a final thesis health report with scores, executive summary, risks, recommendations, defense questions, markdown output, structured JSON, and generated action tasks.

---

# Epic 8: Band Integration and Workflow

## TF-038: Create Band Service Wrapper

**Priority:** Must-have for launch

**Description:**
Create a backend service for interacting with Band Agent API.

**Acceptance Criteria:**

* `band_service.py` exists.
* Reads Band configuration from environment variables.
* Supports:

  * validating agent identity
  * creating chat room
  * listing peers
  * adding participants
  * sending agent messages
  * posting agent events
  * fetching context
* Handles Band API errors safely.
* Does not expose Band API key in logs.

**Dependencies:**
TF-001.

**AI Coding Prompt:**
Create a Band service wrapper in the FastAPI backend. It should support validating agent identity, creating chats, adding participants, sending messages, posting events, and fetching context using Band API credentials from environment variables.

---

## TF-039: Store Agent Messages Locally

**Priority:** Must-have for launch

**Description:**
Every agent handoff or event sent through Band should also be stored in the local `agent_messages` table.

**Acceptance Criteria:**

* Local message record is created for every Band message.
* Message includes:

  * run_id
  * project_id
  * from_agent_id
  * to_agent_id
  * message_type
  * task
  * summary
  * payload
  * band_message_id
  * status
* If Band fails, local status is saved as `failed`.
* Frontend can still show local logs.

**Dependencies:**
TF-010, TF-038.

**AI Coding Prompt:**
Implement local storage for ThesisForge agent messages. Whenever a Band message or event is sent, save the message to the `agent_messages` table with run ID, project ID, agents, summary, payload, Band ID, and status.

---

## TF-040: Build LangGraph Thesis Review Workflow

**Priority:** Must-have for launch

**Description:**
Create the main thesis review workflow using LangGraph or a similar graph-style workflow structure.

**Acceptance Criteria:**

* Workflow starts from an `analysis_run`.
* Workflow executes agents in order:

  1. Literature Review Agent
  2. Research Gap Agent
  3. Citation Agent
  4. Methodology Agent
  5. Results Agent, if enabled
  6. Defense Agent
  7. Report Agent
* Workflow passes structured state between agents.
* Workflow sends Band messages between major handoffs.
* Workflow saves findings after each agent.
* Workflow updates run status.
* Workflow handles partial failures.

**Dependencies:**
TF-031, TF-032, TF-033, TF-034, TF-036, TF-037, TF-038, TF-039.

**AI Coding Prompt:**
Build the main ThesisForge thesis review workflow using LangGraph. It should run the agents in sequence, pass structured state between them, send Band handoff messages, save findings, update analysis run status, and generate a final report.

---

## TF-041: Create Analysis Run API

**Priority:** Must-have for launch

**Description:**
Build backend APIs to start and inspect analysis runs.

**Acceptance Criteria:**

* Endpoints:

  * `POST /api/v1/projects/{project_id}/analysis-runs`
  * `GET /api/v1/projects/{project_id}/analysis-runs`
  * `GET /api/v1/analysis-runs/{run_id}`
  * `GET /api/v1/analysis-runs/{run_id}/status`
* Start endpoint creates analysis run.
* Run status updates:

  * queued
  * running
  * completed
  * failed
  * partial
* Ownership checks are enforced.
* Returns current agent and progress percentage if available.

**Dependencies:**
TF-040.

**AI Coding Prompt:**
Build analysis run APIs for ThesisForge. Users should be able to start a review, list runs, view run details, and poll run status. Enforce ownership checks and return status, current agent, and progress.

---

## TF-042: Add Background Worker for Analysis Runs

**Priority:** Should-have

**Description:**
Move analysis execution into a background worker so the API request does not block.

**Acceptance Criteria:**

* Celery or RQ worker is configured.
* Starting an analysis run queues a background job.
* Worker executes the thesis review workflow.
* Run status is updated in the database.
* API immediately returns queued run ID.
* Failed worker jobs update run status to failed.

**Dependencies:**
TF-041.

**AI Coding Prompt:**
Add a background worker for ThesisForge analysis runs using Celery or RQ with Redis. Starting an analysis run should queue a job, return immediately, and let the worker execute the workflow while updating run status.

---

# Epic 9: Review and Agent Timeline UI

## TF-043: Build Run Review Page

**Priority:** Must-have for launch

**Description:**
Create the frontend page where users start a thesis review.

**Acceptance Criteria:**

* Page exists at `/projects/[projectId]/review`.
* Shows project readiness checklist:

  * project details present
  * thesis content present
  * references present or optional
* User can select review type:

  * full review
  * research gap review
  * defense preparation
* Primary button starts analysis run.
* On success, redirects to run progress page.
* Handles missing content warnings.

**Dependencies:**
TF-019, TF-041.

**AI Coding Prompt:**
Build the ThesisForge run review page. Show a readiness checklist, allow the user to select review type, start an analysis run through the backend API, and redirect to the run progress page.

---

## TF-044: Build Analysis Run Progress Page

**Priority:** Must-have for launch

**Description:**
Create a page that shows the progress of a running thesis review.

**Acceptance Criteria:**

* Page exists at `/projects/[projectId]/runs/[runId]`.
* Polls run status every 3–5 seconds.
* Shows:

  * current status
  * progress percentage
  * current agent
  * started time
* Stops polling when run is completed or failed.
* Shows button to view report when completed.
* Shows clear error if run fails.

**Dependencies:**
TF-041, TF-043.

**AI Coding Prompt:**
Build the analysis run progress page for ThesisForge. Poll the backend for run status, show current agent and progress, stop polling when complete or failed, and show a View Report button when ready.

---

## TF-045: Build Agent Timeline Component

**Priority:** Must-have for launch

**Description:**
Create a reusable component that visually shows each agent’s progress during a review run.

**Acceptance Criteria:**

* Component displays all agents in workflow order.
* Each agent has status:

  * waiting
  * running
  * completed
  * failed
  * partial
* Active agent is highlighted.
* Completed agents show check icon.
* Failed agents show warning icon.
* Works on desktop and mobile.

**Dependencies:**
TF-044.

**AI Coding Prompt:**
Create an Agent Timeline component for ThesisForge. It should display all review agents in order with visual status states for waiting, running, completed, failed, and partial.

---

## TF-046: Build Agent Collaboration Log UI

**Priority:** Must-have for launch

**Description:**
Create a frontend component that shows agent-to-agent Band communication logs.

**Acceptance Criteria:**

* Fetches messages from:

  * `GET /api/v1/analysis-runs/{run_id}/agent-messages`
* Displays:

  * from agent
  * to agent
  * message type
  * summary
  * timestamp
  * status
* Failed Band messages are clearly marked.
* Log updates while run is active.
* Empty state appears if no messages exist yet.

**Dependencies:**
TF-039, TF-044.

**AI Coding Prompt:**
Build the Agent Collaboration Log UI for ThesisForge. Fetch agent messages for a run and display from-agent, to-agent, message type, summary, timestamp, and status in a clear timeline format.

---

# Epic 10: Reports and Findings

## TF-047: Create Report API

**Priority:** Must-have for launch

**Description:**
Build backend APIs for fetching reports.

**Acceptance Criteria:**

* Endpoints:

  * `GET /api/v1/projects/{project_id}/reports`
  * `GET /api/v1/reports/{report_id}`
* Users only access their own reports.
* Report response includes:

  * scores
  * executive summary
  * markdown
  * structured JSON
  * created time
* Missing report returns safe 404.

**Dependencies:**
TF-037.

**AI Coding Prompt:**
Build report APIs for ThesisForge. Users should be able to list reports for a project and fetch a specific report by ID. Enforce ownership and return scores, markdown, JSON, and metadata.

---

## TF-048: Build Final Report Page

**Priority:** Must-have for launch

**Description:**
Create the frontend page that displays the final thesis health report.

**Acceptance Criteria:**

* Page exists at `/projects/[projectId]/reports/[reportId]`.
* Shows:

  * overall score
  * score breakdown
  * executive summary
  * markdown report
  * priority fixes
  * defense questions
* Uses score color rules.
* Includes “Copy report” button.
* Includes “Run review again” button.
* Handles missing report safely.

**Dependencies:**
TF-047.

**AI Coding Prompt:**
Build the final report page for ThesisForge. Fetch the report from the backend and display overall score, score breakdown, executive summary, markdown report, priority fixes, and defense questions with a polished UI.

---

## TF-049: Build Score Card Component

**Priority:** Must-have for launch

**Description:**
Create reusable score card components for report pages.

**Acceptance Criteria:**

* Overall score card displays large score out of 100.
* Breakdown cards show:

  * gap score
  * citation score
  * methodology score
  * results score
  * defense score
* Colors change by score range.
* Handles missing scores.

**Dependencies:**
TF-048.

**AI Coding Prompt:**
Create reusable score card components for ThesisForge reports. Display overall score and score breakdown with color-coded status based on score ranges.

---

## TF-050: Build Priority Fix List Component

**Priority:** Must-have for launch

**Description:**
Create a component that displays recommended thesis improvement tasks from the report.

**Acceptance Criteria:**

* Displays task title, category, priority, and description.
* High-priority tasks appear first.
* Priority badge uses correct color.
* Empty state appears if no tasks exist.
* Optional checkbox for marking task complete if task API exists.

**Dependencies:**
TF-037, TF-048.

**AI Coding Prompt:**
Build a Priority Fix List component for ThesisForge. Display recommended improvement tasks from the report JSON, sorted by priority, with category and priority badges.

---

## TF-051: Build Defense Questions Component

**Priority:** Must-have for launch

**Description:**
Create a component that displays likely thesis defense questions generated by the Defense Agent.

**Acceptance Criteria:**

* Displays question text.
* Shows category.
* Shows risk level.
* Shows suggested answer points.
* High-risk questions appear first.
* Empty state appears if no questions exist.

**Dependencies:**
TF-036, TF-048.

**AI Coding Prompt:**
Build a Defense Questions component for ThesisForge. Display generated thesis panel questions with category, risk level, and suggested answer points, sorted by risk.

---

## TF-052: Add Report Copy and Download

**Priority:** Should-have

**Description:**
Allow users to copy the report text and download it as a markdown file.

**Acceptance Criteria:**

* “Copy report” copies markdown to clipboard.
* “Download markdown” downloads `.md` file.
* Success toast appears after copy/download.
* File name includes project title and date.

**Dependencies:**
TF-048.

**AI Coding Prompt:**
Add copy and markdown download actions to the ThesisForge report page. Let users copy the full report markdown to clipboard and download it as a `.md` file with a useful filename.

---

# Epic 11: Tasks and Supervisor Feedback

## TF-053: Create Action Task API

**Priority:** Should-have

**Description:**
Build backend APIs for viewing and updating generated action tasks.

**Acceptance Criteria:**

* Endpoints:

  * `GET /api/v1/projects/{project_id}/tasks`
  * `PATCH /api/v1/tasks/{task_id}`
  * `DELETE /api/v1/tasks/{task_id}`
* Tasks are tied to projects.
* Users only access their own tasks.
* Users can update task status:

  * open
  * in_progress
  * completed
  * dismissed
* Users can delete tasks.

**Dependencies:**
TF-037.

**AI Coding Prompt:**
Build action task APIs for ThesisForge. Allow users to list tasks for a project, update task status, and delete tasks while enforcing project ownership.

---

## TF-054: Build Tasks UI

**Priority:** Should-have

**Description:**
Create frontend UI to show and manage action tasks generated from reports.

**Acceptance Criteria:**

* Tasks appear on project overview or dedicated page.
* User can mark tasks as completed.
* User can dismiss tasks.
* Tasks are grouped by category.
* Tasks are sorted by priority.
* Empty state appears if no tasks exist.

**Dependencies:**
TF-053.

**AI Coding Prompt:**
Build the Tasks UI for ThesisForge. Fetch tasks from the backend, group them by category, sort by priority, and allow users to mark tasks complete or dismiss them.

---

## TF-055: Create Supervisor Feedback API

**Priority:** Nice-to-have

**Description:**
Build backend APIs for adding and viewing supervisor feedback.

**Acceptance Criteria:**

* Endpoints:

  * `POST /api/v1/projects/{project_id}/feedback`
  * `GET /api/v1/projects/{project_id}/feedback`
* Feedback includes:

  * feedback_text
  * source
  * feedback_date
* Users only access feedback for their own projects.
* Feedback can later be used by agents.

**Dependencies:**
TF-015.

**AI Coding Prompt:**
Build supervisor feedback APIs for ThesisForge. Allow users to add and list feedback entries for their own projects, including feedback text, source, and date.

---

## TF-056: Build Supervisor Feedback UI

**Priority:** Nice-to-have

**Description:**
Create frontend UI where users can paste supervisor feedback.

**Acceptance Criteria:**

* Feedback input exists in project page or upload page.
* User can enter feedback text.
* User can select source:

  * meeting
  * email
  * document comment
  * manual
* Feedback list displays previous entries.
* Handles empty state.

**Dependencies:**
TF-055.

**AI Coding Prompt:**
Build the Supervisor Feedback UI for ThesisForge. Let users paste feedback, choose a source, save it to the backend, and view previous feedback entries.

---

# Epic 12: Error Handling and Security

## TF-057: Add Global Backend Error Handler

**Priority:** Must-have for launch

**Description:**
Create consistent backend error responses across the API.

**Acceptance Criteria:**

* Backend returns standard error format:

  * error
  * code
  * message
  * request_id
* Stack traces are not shown to users.
* Request ID is included in logs.
* Common errors are handled:

  * 400
  * 401
  * 403/404
  * 413
  * 500
* Sensitive data is not logged.

**Dependencies:**
TF-001.

**AI Coding Prompt:**
Add a global error handling system to the FastAPI backend. Return consistent safe error responses with request IDs, hide stack traces, and log detailed errors server-side without secrets.

---

## TF-058: Add Frontend Error and Toast System

**Priority:** Must-have for launch

**Description:**
Create a consistent frontend system for showing success, warning, and error messages.

**Acceptance Criteria:**

* Toast system exists.
* API errors are converted into user-friendly messages.
* Auth errors are handled.
* Upload errors are handled.
* Analysis errors are handled.
* Permission errors use safe message:

  * “We could not find this project or you do not have access to it.”

**Dependencies:**
TF-002.

**AI Coding Prompt:**
Implement a frontend toast and error handling system for ThesisForge. Convert backend API errors into friendly user-facing messages and support success, warning, and error toasts.

---

## TF-059: Add File Upload Security Validation

**Priority:** Must-have for launch

**Description:**
Add security checks for uploaded files.

**Acceptance Criteria:**

* File size limit is enforced.
* MIME type is checked.
* File extension is checked.
* Unsupported types are rejected.
* Empty files are rejected.
* File names are sanitized.
* Upload errors are safe and clear.

**Dependencies:**
TF-023.

**AI Coding Prompt:**
Add secure file upload validation to ThesisForge. Validate file size, MIME type, extension, empty files, and sanitize filenames before saving uploads.

---

## TF-060: Add Prompt Injection Guardrails

**Priority:** Must-have for launch

**Description:**
Protect agents from following malicious instructions inside uploaded thesis content.

**Acceptance Criteria:**

* Every agent system prompt states that uploaded content is untrusted data.
* Agents are instructed not to reveal secrets.
* Agents are instructed not to follow commands inside thesis text.
* Agents only analyze provided content.
* Prompt templates separate system instructions from user content.

**Dependencies:**
TF-030.

**AI Coding Prompt:**
Add prompt injection guardrails to all ThesisForge agent prompts. Ensure uploaded thesis content is treated as untrusted data and agents are instructed not to follow commands inside the content or reveal secrets.

---

## TF-061: Add API Rate Limits

**Priority:** Should-have

**Description:**
Add basic rate limiting for sensitive backend routes.

**Acceptance Criteria:**

* Rate limits exist for:

  * login-related backend calls, if applicable
  * file upload
  * start analysis run
  * report generation
* Exceeding limit returns friendly error.
* Limits are configurable through environment variables.
* Rate limit logs include user ID or IP.

**Dependencies:**
TF-057.

**AI Coding Prompt:**
Add basic rate limiting to ThesisForge backend routes for file upload, starting analysis runs, and report generation. Make limits configurable and return friendly errors when exceeded.

---

# Epic 13: Environment, Configuration, and Deployment

## TF-062: Create Environment Configuration Layer

**Priority:** Must-have for launch

**Description:**
Create centralized backend and frontend configuration handling.

**Acceptance Criteria:**

* Backend uses a config module to read environment variables.
* Required backend variables are validated at startup.
* Frontend uses `.env.local.example`.
* Missing critical variables produce clear developer errors.
* No secrets are committed to Git.

**Dependencies:**
TF-001.

**AI Coding Prompt:**
Create centralized environment configuration for ThesisForge. Add backend config validation, frontend env examples, and clear startup errors when required variables are missing. Ensure no secrets are committed.

---

## TF-063: Add Docker Compose for Local Development

**Priority:** Should-have

**Description:**
Create Docker Compose setup for local Postgres, Redis, and backend services.

**Acceptance Criteria:**

* `docker-compose.yml` includes:

  * Postgres with pgvector
  * Redis
  * FastAPI backend
* Local database is accessible.
* Backend can connect to database and Redis.
* README includes Docker setup instructions.

**Dependencies:**
TF-001, TF-010.

**AI Coding Prompt:**
Add Docker Compose local development setup for ThesisForge with Postgres/pgvector, Redis, and FastAPI backend. Update README with instructions.

---

## TF-064: Add Vercel Deployment Config for Frontend

**Priority:** Should-have

**Description:**
Prepare frontend for Vercel deployment.

**Acceptance Criteria:**

* Next.js app builds successfully.
* Required Vercel environment variables are documented.
* Production API base URL is configurable.
* No server-only secrets are exposed.

**Dependencies:**
TF-001, TF-062.

**AI Coding Prompt:**
Prepare the ThesisForge Next.js frontend for Vercel deployment. Ensure the app builds, environment variables are documented, and production API base URL is configurable.

---

## TF-065: Add Render or Railway Deployment Config for Backend

**Priority:** Should-have

**Description:**
Prepare backend for deployment on Render or Railway.

**Acceptance Criteria:**

* Backend has production start command.
* Dockerfile or deployment config exists.
* Environment variable list is documented.
* Database migrations can run in production.
* Health check route works.

**Dependencies:**
TF-001, TF-062.

**AI Coding Prompt:**
Prepare the ThesisForge FastAPI backend for deployment on Render or Railway. Add a production start command, Dockerfile or deployment config, environment variable documentation, migration instructions, and health check support.

---

# Epic 14: Demo and Hackathon Submission

## TF-066: Add Demo Thesis Dataset

**Priority:** Must-have for launch

**Description:**
Create a sample thesis project dataset that can be used for demos and hackathon judging.

**Acceptance Criteria:**

* `examples/` folder contains:

  * sample thesis title
  * problem statement
  * research gap
  * methodology summary
  * result summary
  * sample references
* Demo data is safe and not private.
* README explains how to use demo data.
* Demo data works with the full review workflow.

**Dependencies:**
TF-040, TF-048.

**AI Coding Prompt:**
Create a safe demo dataset for ThesisForge inside an `examples/` folder. Include sample thesis metadata, research gap, methodology, results summary, and references that can be used to demonstrate the full agent review workflow.

---

## TF-067: Create Demo Mode

**Priority:** Should-have

**Description:**
Add a demo mode that fills the app with sample thesis data so judges can quickly test the workflow.

**Acceptance Criteria:**

* User can click “Load demo project.”
* Demo project is created for the logged-in user.
* Demo thesis data is inserted.
* User can run review immediately.
* Demo mode is clearly labeled.

**Dependencies:**
TF-066, TF-015.

**AI Coding Prompt:**
Add a demo mode to ThesisForge. Let logged-in users click “Load demo project” to create a prefilled project using sample thesis data so they can immediately run a review.

---

## TF-068: Create README for GitHub Submission

**Priority:** Must-have for launch

**Description:**
Create a polished README for the public GitHub repository.

**Acceptance Criteria:**

README includes:

* Product name and tagline
* Problem statement
* Solution overview
* Agent workflow
* Band integration explanation
* Tech stack
* Setup instructions
* Environment variables
* Demo data instructions
* Screenshots or placeholder image links
* Hackathon submission notes

**Dependencies:**
TF-001, TF-040, TF-048.

**AI Coding Prompt:**
Write a polished README for the ThesisForge GitHub repository. Include product overview, problem, solution, agent workflow, Band integration, tech stack, setup instructions, environment variables, demo usage, and hackathon notes.

---

## TF-069: Add Basic Analytics Events

**Priority:** Nice-to-have

**Description:**
Track important product events for MVP success metrics.

**Acceptance Criteria:**

* Track events:

  * project_created
  * document_uploaded
  * analysis_started
  * analysis_completed
  * report_viewed
  * report_copied
* Events are logged locally or through simple analytics provider.
* No thesis content is sent to analytics.

**Dependencies:**
TF-015, TF-023, TF-041, TF-048.

**AI Coding Prompt:**
Add basic analytics events to ThesisForge for project creation, document upload, analysis start, analysis completion, report view, and report copy. Do not send private thesis content to analytics.

---

# Epic 15: Polish and Quality

## TF-070: Add Loading Skeletons

**Priority:** Should-have

**Description:**
Add loading skeletons across major frontend pages.

**Acceptance Criteria:**

* Dashboard has project card skeletons.
* Project overview has section skeletons.
* Upload page has document list skeleton.
* Run progress page has timeline skeleton.
* Report page has score/report skeleton.
* No page shows a blank screen while loading.

**Dependencies:**
TF-017, TF-019, TF-028, TF-044, TF-048.

**AI Coding Prompt:**
Add loading skeleton states across ThesisForge frontend pages including dashboard, project overview, upload page, run progress page, and report page.

---

## TF-071: Add Empty States

**Priority:** Should-have

**Description:**
Add helpful empty states across the app.

**Acceptance Criteria:**

* Empty dashboard explains how to create first project.
* Empty documents page explains how to upload or paste content.
* Empty reports page explains how to run first review.
* Empty agent log explains that messages will appear after review starts.
* Empty tasks page explains that tasks are generated from reports.

**Dependencies:**
TF-017, TF-028, TF-046, TF-048, TF-054.

**AI Coding Prompt:**
Add helpful empty states across ThesisForge. Each empty state should explain what is missing and provide a clear next action.

---

## TF-072: Add Responsive Mobile Layout

**Priority:** Should-have

**Description:**
Ensure the app works properly on mobile and tablet screens.

**Acceptance Criteria:**

* Sidebar becomes mobile drawer.
* Cards stack vertically on small screens.
* Forms are usable on mobile.
* Report page is readable on mobile.
* Agent timeline becomes vertical.
* No horizontal overflow except intentional tables.

**Dependencies:**
TF-003, TF-017, TF-019, TF-028, TF-044, TF-048.

**AI Coding Prompt:**
Make the ThesisForge frontend responsive. Ensure sidebar, dashboard cards, forms, upload page, agent timeline, and report page work well on mobile and tablet screens.

---

## TF-073: Add Basic Test Coverage

**Priority:** Should-have

**Description:**
Add basic backend and frontend tests for critical flows.

**Acceptance Criteria:**

Backend tests cover:

* project creation
* ownership checks
* document text creation
* analysis run creation
* report fetch

Frontend tests or basic smoke checks cover:

* login page renders
* dashboard renders
* create project form validates
* report page renders with mock data

**Dependencies:**
Core features completed.

**AI Coding Prompt:**
Add basic test coverage for ThesisForge. Add backend tests for project creation, ownership checks, document text creation, analysis run creation, and report fetching. Add frontend smoke tests for login, dashboard, project form, and report rendering.

---

## TF-074: Add Final Hackathon Demo Polish

**Priority:** Must-have for launch

**Description:**
Polish the MVP so it is ready for a hackathon demo.

**Acceptance Criteria:**

* Demo flow works end-to-end:

  * login
  * create/load project
  * add thesis content
  * run review
  * see agent timeline
  * see Band collaboration log
  * see final report
* UI has no obvious broken states.
* README setup works.
* Demo data works.
* Error messages are friendly.
* Agent collaboration is visible and understandable.
* Project can be explained within 2–4 minutes.

**Dependencies:**
TF-017, TF-018, TF-028, TF-040, TF-044, TF-046, TF-048, TF-066, TF-068.

**AI Coding Prompt:**
Polish ThesisForge for a hackathon demo. Ensure the full flow works end-to-end from login to project creation, content input, thesis review, agent timeline, Band collaboration log, and final report. Fix broken states and improve demo clarity.

---

# Recommended MVP Build Order

## Phase 1: Foundation

1. TF-001 Initialize Monorepo
2. TF-002 Configure Design System
3. TF-003 Create Shared Layout
4. TF-062 Environment Configuration
5. TF-010 Database Schema

## Phase 2: Auth and Projects

6. TF-004 Supabase Auth Client
7. TF-005 Signup Page
8. TF-006 Login Page
9. TF-008 Protected Routes
10. TF-009 Backend JWT Verification
11. TF-014 User Profile API
12. TF-015 Project CRUD API
13. TF-017 Dashboard Page
14. TF-018 Create Project Page
15. TF-019 Project Overview Page

## Phase 3: Documents

16. TF-016 Document Metadata API
17. TF-021 Pasted Text Document API
18. TF-022 Text Chunking Service
19. TF-023 File Upload API
20. TF-024 PDF Parser
21. TF-028 Upload Page

## Phase 4: Agents and Workflow

22. TF-011 Seed Default Agents
23. TF-029 LLM Service
24. TF-030 Base Agent Class
25. TF-031 Literature Review Agent
26. TF-032 Research Gap Agent
27. TF-034 Methodology Agent
28. TF-036 Defense Agent
29. TF-037 Report Agent
30. TF-038 Band Service
31. TF-039 Store Agent Messages
32. TF-040 LangGraph Workflow
33. TF-041 Analysis Run API

## Phase 5: Review UI and Reports

34. TF-043 Run Review Page
35. TF-044 Analysis Run Progress Page
36. TF-045 Agent Timeline
37. TF-046 Agent Collaboration Log
38. TF-047 Report API
39. TF-048 Final Report Page
40. TF-049 Score Card
41. TF-050 Priority Fix List
42. TF-051 Defense Questions

## Phase 6: Security and Polish

43. TF-057 Backend Error Handler
44. TF-058 Frontend Error System
45. TF-059 File Upload Security
46. TF-060 Prompt Injection Guardrails
47. TF-066 Demo Dataset
48. TF-068 README
49. TF-074 Final Demo Polish

# Minimum Hackathon MVP Ticket Set

If time is short, build only these:

1. TF-001 Initialize Monorepo
2. TF-002 Configure Design System
3. TF-003 Shared Layout
4. TF-004 Supabase Auth Client
5. TF-006 Login Page
6. TF-008 Protected Routes
7. TF-009 Backend JWT Verification
8. TF-010 Database Schema
9. TF-011 Seed Default Agents
10. TF-014 User Profile API
11. TF-015 Project CRUD API
12. TF-017 Dashboard Page
13. TF-018 Create Project Page
14. TF-019 Project Overview Page
15. TF-021 Pasted Text Document API
16. TF-022 Text Chunking Service
17. TF-028 Upload Page
18. TF-029 LLM Service
19. TF-030 Base Agent Class
20. TF-031 Literature Review Agent
21. TF-032 Research Gap Agent
22. TF-034 Methodology Agent
23. TF-036 Defense Agent
24. TF-037 Report Agent
25. TF-038 Band Service
26. TF-039 Store Agent Messages
27. TF-040 Thesis Review Workflow
28. TF-041 Analysis Run API
29. TF-043 Run Review Page
30. TF-044 Run Progress Page
31. TF-045 Agent Timeline
32. TF-046 Agent Collaboration Log
33. TF-047 Report API
34. TF-048 Final Report Page
35. TF-057 Backend Error Handler
36. TF-058 Frontend Error System
37. TF-060 Prompt Injection Guardrails
38. TF-066 Demo Dataset
39. TF-068 README
40. TF-074 Final Demo Polish

This minimum set proves the core product:

```text
User logs in → creates thesis project → adds thesis content → starts review → agents collaborate through Band → final thesis health report is generated.
```
