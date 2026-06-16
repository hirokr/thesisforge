# Frontend Specification Document

## Product: ThesisForge

### Multi-Agent Research Workflow Assistant

## 1. Product UI Summary

ThesisForge is a research workflow assistant that helps thesis students and researchers review their research gap, citations, methodology, results, and defense readiness using multiple AI agents.

The frontend should feel:

* Academic but modern
* Trustworthy
* Calm and focused
* Clear enough for non-technical students
* Professional enough for supervisors and hackathon judges

The UI should not look like a casual chatbot. It should look like a serious research quality-control dashboard.

## 2. Frontend Goals

The frontend must help the user do five things clearly:

1. Create a thesis project.
2. Add thesis material or upload files.
3. Start a multi-agent review.
4. Watch agent collaboration progress.
5. Read and act on the final thesis health report.

The most important UI principle:

```text
The user should always understand what is happening, which agent is working, and what they should do next.
```

## 3. Recommended Frontend Stack

## 3.1 Framework

### Next.js App Router

Use Next.js with the App Router.

Reason:

* Good for SaaS dashboards
* Easy deployment on Vercel
* Supports protected routes
* Works well with Supabase Auth
* Better long-term choice than Streamlit for a real product

## 3.2 Styling

### Tailwind CSS

Use Tailwind CSS for layout, spacing, colors, and responsive design.

Reason:

* Fast to build
* Easy to keep consistent
* Works well with shadcn/ui

## 3.3 Component System

### shadcn/ui

Use shadcn/ui as the base component library.

Reason:

* Clean SaaS-style components
* Easy to customize
* Accessible defaults
* Works well with Tailwind

## 3.4 State and Data Fetching

### TanStack Query

Use TanStack Query for API data fetching.

Use it for:

* Project list
* Project detail
* Analysis run status
* Agent messages
* Reports
* Tasks

Reason:

* Handles loading, error, success, caching, and refetching states cleanly.

## 3.5 Forms

### React Hook Form + Zod

Use React Hook Form for form handling and Zod for validation.

Use it for:

* Signup/login forms
* Project creation
* Thesis input form
* Feedback input
* Settings forms

## 3.6 Markdown Rendering

### react-markdown

Use react-markdown for displaying final reports.

The final report will be generated in markdown, so the frontend should render it cleanly.

## 4. Brand Direction

## 4.1 Product Personality

ThesisForge should feel like:

* A research assistant
* A thesis reviewer
* A structured academic workflow tool
* A quality-control system
* A calm professional dashboard

It should not feel like:

* A generic AI chatbot
* A casual notes app
* A flashy social app
* A heavy enterprise admin panel

## 4.2 Visual Keywords

Use these visual ideas:

* Deep navy
* Academic blue
* Soft violet
* Clean white space
* Light gray backgrounds
* Subtle borders
* Score cards
* Agent timeline
* Report panels
* Research-document style layouts

## 5. Color Palette

## 5.1 Primary Colors

| Token              | Hex       | Use                                   |
| ------------------ | --------- | ------------------------------------- |
| Primary Navy       | `#1E3A5F` | Main brand color, sidebar, headings   |
| Primary Blue       | `#2563EB` | Primary buttons, links, active states |
| Primary Blue Hover | `#1D4ED8` | Button hover                          |
| Soft Blue          | `#DBEAFE` | Light selected background             |
| Ink                | `#0F172A` | Main text                             |

## 5.2 Secondary Colors

| Token           | Hex       | Use                                |
| --------------- | --------- | ---------------------------------- |
| Research Violet | `#7C3AED` | Agent highlights, special badges   |
| Soft Violet     | `#EDE9FE` | Agent card background              |
| Teal            | `#0F766E` | Success and completed agent states |
| Soft Teal       | `#CCFBF1` | Success background                 |
| Amber           | `#D97706` | Warning states                     |
| Soft Amber      | `#FEF3C7` | Warning background                 |

## 5.3 Neutral Colors

| Token            | Hex       | Use                    |
| ---------------- | --------- | ---------------------- |
| White            | `#FFFFFF` | Main surfaces          |
| Background       | `#F8FAFC` | App background         |
| Muted Background | `#F1F5F9` | Secondary sections     |
| Border           | `#E2E8F0` | Card and input borders |
| Muted Border     | `#CBD5E1` | Stronger borders       |
| Muted Text       | `#64748B` | Helper text            |
| Body Text        | `#334155` | Paragraph text         |
| Heading Text     | `#0F172A` | Main headings          |

## 5.4 Status Colors

| Status     | Hex       | Use                           |
| ---------- | --------- | ----------------------------- |
| Success    | `#16A34A` | Completed review, good score  |
| Warning    | `#F59E0B` | Medium-risk issues            |
| Danger     | `#DC2626` | High-risk issues, failed runs |
| Info       | `#2563EB` | Informational messages        |
| Processing | `#7C3AED` | Agent currently working       |
| Disabled   | `#94A3B8` | Disabled UI states            |

## 5.5 Score Colors

| Score Range | Color     | Meaning                    |
| ----------- | --------- | -------------------------- |
| 85–100      | `#16A34A` | Strong thesis health       |
| 70–84       | `#2563EB` | Good but needs improvement |
| 50–69       | `#F59E0B` | Medium risk                |
| 0–49        | `#DC2626` | High risk                  |

## 6. Typography

## 6.1 Font Family

Use:

```css
font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
```

Reason:

* Clean
* Readable
* Professional
* Works well for dashboards and reports

## 6.2 Optional Report Font

For final reports, you may use a more academic serif font for report titles only:

```css
font-family: "Source Serif 4", Georgia, serif;
```

Use this only for report headings, not the whole app.

## 6.3 Type Scale

| Element    | Size | Weight | Line Height |
| ---------- | ---: | -----: | ----------: |
| Display    | 48px |    700 |        56px |
| H1         | 36px |    700 |        44px |
| H2         | 30px |    700 |        38px |
| H3         | 24px |    600 |        32px |
| H4         | 20px |    600 |        28px |
| Body Large | 18px |    400 |        30px |
| Body       | 16px |    400 |        26px |
| Body Small | 14px |    400 |        22px |
| Caption    | 12px |    500 |        18px |
| Button     | 14px |    600 |        20px |

## 6.4 Typography Rules

* Use H1 only once per page.
* Use sentence case, not title case, for most UI labels.
* Keep button text short.
* Use plain English for errors.
* Avoid academic jargon unless inside the report content.
* Use bold only for important emphasis.

## 7. Spacing and Layout System

## 7.1 Spacing Scale

Use a 4px spacing system.

| Token      | Value |
| ---------- | ----: |
| `space-1`  |   4px |
| `space-2`  |   8px |
| `space-3`  |  12px |
| `space-4`  |  16px |
| `space-5`  |  20px |
| `space-6`  |  24px |
| `space-8`  |  32px |
| `space-10` |  40px |
| `space-12` |  48px |
| `space-16` |  64px |

## 7.2 App Layout

Authenticated app layout:

```text
┌─────────────────────────────────────────────┐
│ Top Navigation                              │
├───────────────┬─────────────────────────────┤
│ Sidebar       │ Main Content                │
│               │                             │
│ Projects      │ Page Header                 │
│ Reports       │ Page Body                   │
│ Settings      │                             │
└───────────────┴─────────────────────────────┘
```

## 7.3 Width Rules

| Area                     |  Width |
| ------------------------ | -----: |
| Sidebar                  |  260px |
| Main content max width   | 1200px |
| Report reading max width |  860px |
| Modal small              |  420px |
| Modal medium             |  640px |
| Modal large              |  860px |

## 7.4 Responsive Breakpoints

| Breakpoint   |      Width |
| ------------ | ---------: |
| Mobile       |    0–639px |
| Tablet       | 640–1023px |
| Desktop      |    1024px+ |
| Wide Desktop |    1280px+ |

## 7.5 Mobile Rules

On mobile:

* Sidebar becomes a slide-out drawer.
* Main content uses full width.
* Cards stack vertically.
* Report page becomes single-column.
* Agent timeline becomes vertical.
* Tables become cards or horizontally scrollable.

## 8. Core Page Structure

## 8.1 Public Landing Page

Purpose:

Explain what ThesisForge does and push users to start a thesis review.

Sections:

1. Hero
2. Problem statement
3. How it works
4. Agent workflow preview
5. Example report preview
6. Call to action

Primary CTA:

```text
Start thesis review
```

Secondary CTA:

```text
View demo
```

## 8.2 Authentication Pages

Pages:

* Login
* Signup
* Forgot password
* Reset password

Design:

* Centered card layout
* Calm background
* Minimal distractions

Fields:

* Email
* Password
* Confirm password on signup

Buttons:

* Continue with email
* Continue with Google

## 8.3 Dashboard Page

Purpose:

Show all thesis projects and current review status.

Sections:

1. Welcome header
2. Create project button
3. Project cards
4. Recent reports
5. Usage summary

Empty state:

```text
No thesis projects yet. Create your first project to start reviewing your research.
```

## 8.4 New Project Page

Purpose:

Collect basic thesis metadata.

Fields:

* Thesis title
* Research area
* Thesis stage
* Problem statement
* Research gap
* Objectives
* Methodology summary
* Results summary

Primary button:

```text
Create project
```

Secondary button:

```text
Save draft
```

## 8.5 Project Detail Page

Purpose:

Show project overview and next actions.

Sections:

1. Project header
2. Thesis metadata summary
3. Uploaded documents
4. Latest analysis run
5. Latest report
6. Priority action tasks

Primary action:

```text
Run thesis review
```

Secondary actions:

```text
Upload documents
Edit project details
View reports
```

## 8.6 Upload Page

Purpose:

Let users add thesis materials.

Upload zones:

1. Thesis draft
2. References / BibTeX
3. Results CSV
4. Supervisor feedback

Supported file types:

```text
PDF, DOCX, TXT, BIB, CSV
```

Maximum MVP file size:

```text
25 MB
```

## 8.7 Review Run Page

Purpose:

Show the multi-agent workflow while it is running.

Sections:

1. Review status header
2. Agent timeline
3. Live or refreshed agent collaboration log
4. Partial findings if available
5. Cancel button, if supported

Agent states:

* Waiting
* Running
* Completed
* Failed
* Partial

## 8.8 Report Page

Purpose:

Display the final thesis health report.

Sections:

1. Overall thesis health score
2. Score breakdown
3. Executive summary
4. Major risks
5. Research gap feedback
6. Citation support feedback
7. Methodology consistency feedback
8. Results interpretation feedback
9. Defense questions
10. Priority fixes
11. Agent collaboration log

Actions:

* Copy report
* Download report
* Create tasks
* Run review again

## 9. Component Design System

## 9.1 Buttons

## Primary Button

Use for the main action on a page.

Style:

```text
Background: #2563EB
Text: #FFFFFF
Hover: #1D4ED8
Border radius: 10px
Height: 40px
Padding: 12px 16px
Font: 14px, 600
```

Examples:

```text
Create project
Run thesis review
View report
```

## Secondary Button

Use for secondary actions.

Style:

```text
Background: #FFFFFF
Text: #1E3A5F
Border: 1px solid #CBD5E1
Hover background: #F8FAFC
Border radius: 10px
Height: 40px
```

Examples:

```text
Save draft
Upload later
Edit details
```

## Destructive Button

Use only for delete actions.

Style:

```text
Background: #DC2626
Text: #FFFFFF
Hover: #B91C1C
Border radius: 10px
```

Examples:

```text
Delete project
Remove document
```

## Ghost Button

Use for low-emphasis actions.

Style:

```text
Background: transparent
Text: #334155
Hover background: #F1F5F9
Border radius: 8px
```

Examples:

```text
Cancel
Back
View details
```

## 9.2 Inputs

## Text Input

Style:

```text
Height: 40px
Background: #FFFFFF
Border: 1px solid #CBD5E1
Border radius: 10px
Text: #0F172A
Placeholder: #94A3B8
Focus border: #2563EB
Focus ring: 3px #DBEAFE
```

## Textarea

Use for thesis sections.

Style:

```text
Minimum height: 140px
Border radius: 12px
Padding: 12px
Resize: vertical
```

For long thesis content, use a larger textarea:

```text
Minimum height: 280px
```

## Select Dropdown

Use for thesis stage and review type.

Options for thesis stage:

```text
Proposal
Literature review
Methodology
Results
Final draft
Defense preparation
```

## 9.3 Cards

## Standard Card

Use for project cards and report sections.

Style:

```text
Background: #FFFFFF
Border: 1px solid #E2E8F0
Border radius: 16px
Padding: 24px
Shadow: 0 1px 2px rgba(15, 23, 42, 0.06)
```

## Hover Card

Use for clickable project cards.

Hover style:

```text
Border: #93C5FD
Shadow: 0 8px 24px rgba(15, 23, 42, 0.08)
Transform: translateY(-1px)
```

## Agent Card

Use for each agent in the workflow.

Style:

```text
Background: #FFFFFF
Border: 1px solid #E2E8F0
Border left: 4px solid status color
Border radius: 14px
Padding: 16px
```

Agent status colors:

```text
Waiting: #94A3B8
Running: #7C3AED
Completed: #16A34A
Failed: #DC2626
Partial: #F59E0B
```

## Score Card

Use for thesis health score.

Style:

```text
Background: linear-gradient(135deg, #1E3A5F, #2563EB)
Text: #FFFFFF
Border radius: 20px
Padding: 28px
```

Score number:

```text
Font size: 48px
Font weight: 700
```

## 9.4 Modals

Use modals for:

* Delete confirmation
* Run review confirmation
* Upload error details
* Report export options

Style:

```text
Background overlay: rgba(15, 23, 42, 0.45)
Modal background: #FFFFFF
Border radius: 20px
Padding: 24px
Max width: 640px
```

Modal structure:

1. Title
2. Short explanation
3. Main content
4. Action row

Button alignment:

```text
Cancel button left
Primary/destructive button right
```

## 9.5 Badges

Use badges for project status, agent status, and severity.

## Status Badges

| Status    | Background | Text      |
| --------- | ---------- | --------- |
| Draft     | `#F1F5F9`  | `#334155` |
| Reviewing | `#EDE9FE`  | `#6D28D9` |
| Completed | `#CCFBF1`  | `#0F766E` |
| Failed    | `#FEE2E2`  | `#B91C1C` |
| Archived  | `#E2E8F0`  | `#475569` |

## Severity Badges

| Severity | Background | Text      |
| -------- | ---------- | --------- |
| Low      | `#DBEAFE`  | `#1D4ED8` |
| Medium   | `#FEF3C7`  | `#B45309` |
| High     | `#FEE2E2`  | `#B91C1C` |
| Critical | `#7F1D1D`  | `#FFFFFF` |

## 9.6 Progress and Loading States

## Page Loading

Use skeleton cards, not only spinners.

## Review Running

Show an agent timeline:

```text
1. Literature Agent
2. Research Gap Agent
3. Citation Agent
4. Methodology Agent
5. Results Agent
6. Defense Agent
7. Report Agent
```

Each item should show:

* Agent name
* Status
* Short current action
* Timestamp if available

## Empty States

Every empty page should include:

1. Simple icon
2. Clear message
3. Primary action

Example:

```text
No reports yet.
Run your first thesis review to generate a report.
[Run thesis review]
```

## 10. Navigation

## 10.1 Sidebar Items

Authenticated sidebar:

```text
Dashboard
Projects
Reports
Tasks
Settings
```

For MVP, Tasks can be hidden if not fully built.

## 10.2 Project Navigation

Inside a project:

```text
Overview
Documents
Run Review
Agent Log
Reports
Tasks
Settings
```

For MVP, keep it simpler:

```text
Overview
Documents
Review
Report
```

## 11. Frontend Route Map

```text
/                         Public landing page
/login                    Login page
/register                 Signup page
/forgot-password           Forgot password page
/reset-password            Reset password page

/dashboard                 Main app dashboard
/projects                  Project list
/projects/new              Create project
/projects/:projectId       Project overview
/projects/:projectId/upload Upload documents
/projects/:projectId/review Run thesis review
/projects/:projectId/runs/:runId Analysis run progress
/projects/:projectId/reports/:reportId Final report
/settings                  User settings
```

## 12. Frontend State Management

## 12.1 Local UI State

Use React state for:

* Modal open/close
* Active tab
* Sidebar open/close
* Upload progress
* Form draft state

## 12.2 Server State

Use TanStack Query for:

* Projects
* Documents
* Analysis runs
* Agent messages
* Reports
* Tasks
* User profile

## 12.3 Auth State

Use Supabase Auth session state.

The frontend should:

* Redirect unauthenticated users away from app routes.
* Redirect authenticated users away from login/register pages.
* Refresh session automatically when supported.
* Send JWT token to FastAPI backend in the Authorization header.

Example:

```text
Authorization: Bearer <supabase_access_token>
```

## 13. Frontend-to-Backend API Spec

The frontend should call only your FastAPI backend for product data and AI workflows.

Base URL:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

## 13.1 Create Project

Endpoint:

```text
POST /projects
```

Auth:

```text
Authorization: Bearer <token>
```

Request:

```json
{
  "title": "Explainable Multimodal Deepfake Detection",
  "research_area": "Artificial Intelligence",
  "thesis_stage": "methodology",
  "problem_statement": "Modern deepfake detectors lack interpretability.",
  "research_gap": "Existing multimodal methods do not provide clear reasoning.",
  "objectives": [
    "Build a multimodal detector",
    "Add interpretable predicate reasoning"
  ],
  "methodology_summary": "The system uses visual, ocular, and audio branches.",
  "dataset_summary": "FakeAVCeleb, DFDC, and AV-Deepfake1M",
  "results_summary": "The proposed model improves AUC across datasets."
}
```

Expected response:

```json
{
  "id": "project_uuid",
  "title": "Explainable Multimodal Deepfake Detection",
  "status": "draft",
  "created_at": "2026-06-17T10:00:00Z"
}
```

Frontend behavior:

* Show success toast.
* Redirect to project overview.

## 13.2 Get Projects

Endpoint:

```text
GET /projects
```

Expected response:

```json
{
  "items": [
    {
      "id": "project_uuid",
      "title": "Explainable Multimodal Deepfake Detection",
      "research_area": "Artificial Intelligence",
      "thesis_stage": "methodology",
      "status": "draft",
      "latest_score": 76,
      "updated_at": "2026-06-17T10:00:00Z"
    }
  ]
}
```

Frontend behavior:

* Render project cards.
* If empty, show empty state.

## 13.3 Get Project Detail

Endpoint:

```text
GET /projects/{project_id}
```

Expected response:

```json
{
  "id": "project_uuid",
  "title": "Explainable Multimodal Deepfake Detection",
  "research_area": "Artificial Intelligence",
  "thesis_stage": "methodology",
  "problem_statement": "Modern deepfake detectors lack interpretability.",
  "research_gap": "Existing multimodal methods do not provide clear reasoning.",
  "objectives": [],
  "methodology_summary": "...",
  "dataset_summary": "...",
  "results_summary": "...",
  "status": "draft",
  "created_at": "2026-06-17T10:00:00Z",
  "updated_at": "2026-06-17T10:00:00Z"
}
```

## 13.4 Upload Document

Endpoint:

```text
POST /projects/{project_id}/documents
```

Request type:

```text
multipart/form-data
```

Fields:

```text
document_type: thesis_draft | reference_file | result_file | feedback | other
file: uploaded file
```

Expected response:

```json
{
  "id": "document_uuid",
  "project_id": "project_uuid",
  "document_type": "thesis_draft",
  "file_name": "thesis-draft.pdf",
  "file_mime_type": "application/pdf",
  "parse_status": "pending",
  "created_at": "2026-06-17T10:00:00Z"
}
```

Frontend behavior:

* Show upload progress.
* Show uploaded file in document list.
* Show parse status.

## 13.5 Add Pasted Text Document

Endpoint:

```text
POST /projects/{project_id}/documents/text
```

Request:

```json
{
  "document_type": "thesis_draft",
  "title": "Methodology section",
  "raw_text": "The proposed framework contains three branches..."
}
```

Expected response:

```json
{
  "id": "document_uuid",
  "parse_status": "parsed",
  "word_count": 1200
}
```

## 13.6 Start Analysis Run

Endpoint:

```text
POST /projects/{project_id}/analysis-runs
```

Request:

```json
{
  "run_type": "full_review",
  "enabled_agents": [
    "literature_review_agent",
    "research_gap_agent",
    "citation_agent",
    "methodology_agent",
    "results_agent",
    "defense_agent",
    "report_agent"
  ]
}
```

Expected response:

```json
{
  "run_id": "run_uuid",
  "project_id": "project_uuid",
  "status": "queued",
  "created_at": "2026-06-17T10:00:00Z"
}
```

Frontend behavior:

* Redirect to `/projects/{projectId}/runs/{runId}`.
* Start polling run status every 3–5 seconds.

## 13.7 Get Analysis Run Status

Endpoint:

```text
GET /analysis-runs/{run_id}/status
```

Expected response:

```json
{
  "run_id": "run_uuid",
  "status": "running",
  "current_agent": "methodology_agent",
  "progress_percent": 57,
  "started_at": "2026-06-17T10:01:00Z",
  "completed_at": null
}
```

Frontend behavior:

* Update progress bar.
* Highlight active agent.
* Continue polling until completed or failed.

## 13.8 Get Agent Messages

Endpoint:

```text
GET /analysis-runs/{run_id}/agent-messages
```

Expected response:

```json
{
  "items": [
    {
      "id": "message_uuid",
      "from_agent": "Literature Review Agent",
      "to_agent": "Research Gap Agent",
      "message_type": "handoff",
      "summary": "The current research gap is too broad.",
      "status": "sent",
      "created_at": "2026-06-17T10:02:00Z"
    }
  ]
}
```

Frontend behavior:

* Render agent collaboration timeline.
* Use different icons for handoff, critique, event, and error.

## 13.9 Get Final Report

Endpoint:

```text
GET /reports/{report_id}
```

Expected response:

```json
{
  "id": "report_uuid",
  "project_id": "project_uuid",
  "run_id": "run_uuid",
  "title": "Thesis Health Report",
  "overall_score": 76,
  "gap_score": 70,
  "citation_score": 68,
  "methodology_score": 82,
  "results_score": 74,
  "defense_score": 78,
  "executive_summary": "Your thesis has a strong direction but needs clearer citation support.",
  "report_markdown": "# Thesis Health Report\n\n...",
  "report_json": {
    "priority_fixes": [],
    "defense_questions": []
  },
  "created_at": "2026-06-17T10:10:00Z"
}
```

Frontend behavior:

* Render score cards.
* Render markdown report.
* Render priority fixes as checklist.
* Show copy/download buttons.

## 14. Third-Party Integration Spec

## 14.1 Integration Rule

The frontend should directly call only:

1. Supabase Auth
2. Your FastAPI backend

The frontend should not directly call:

1. OpenAI
2. Band
3. Gemini
4. Featherless AI
5. AI/ML API
6. Supabase service-role operations

Reason:

Those services require private keys. Private keys must stay on the backend.

## 15. Supabase Auth Integration

## 15.1 What Supabase Auth Does

Supabase Auth handles:

* User signup
* User login
* Google OAuth login
* Session management
* Password reset
* JWT access tokens

## 15.2 Frontend Signup

SDK method:

```text
supabase.auth.signUp()
```

Data sent:

```json
{
  "email": "student@example.com",
  "password": "secure-password",
  "options": {
    "data": {
      "full_name": "Student Name",
      "role": "student"
    }
  }
}
```

Expected response:

```json
{
  "data": {
    "user": {
      "id": "auth_user_uuid",
      "email": "student@example.com"
    },
    "session": null
  },
  "error": null
}
```

Frontend behavior:

* If email confirmation is enabled, show:

  ```text
  Check your email to confirm your account.
  ```
* If session is returned, redirect to dashboard.

## 15.3 Frontend Login

SDK method:

```text
supabase.auth.signInWithPassword()
```

Data sent:

```json
{
  "email": "student@example.com",
  "password": "secure-password"
}
```

Expected response:

```json
{
  "data": {
    "user": {
      "id": "auth_user_uuid",
      "email": "student@example.com"
    },
    "session": {
      "access_token": "jwt_token",
      "refresh_token": "refresh_token"
    }
  },
  "error": null
}
```

Frontend behavior:

* Store session through Supabase client.
* Redirect to dashboard.
* Use access token for backend API calls.

## 15.4 Google Login

SDK method:

```text
supabase.auth.signInWithOAuth()
```

Data sent:

```json
{
  "provider": "google",
  "options": {
    "redirectTo": "https://app-domain.com/auth/callback"
  }
}
```

Expected response:

```json
{
  "data": {
    "url": "google_oauth_redirect_url"
  },
  "error": null
}
```

Frontend behavior:

* Redirect user to Google login.
* After callback, load session.
* Redirect to dashboard.

## 15.5 Logout

SDK method:

```text
supabase.auth.signOut()
```

Expected response:

```json
{
  "error": null
}
```

Frontend behavior:

* Clear local app state.
* Redirect to `/login`.

## 15.6 Password Reset

SDK method:

```text
supabase.auth.resetPasswordForEmail()
```

Data sent:

```json
{
  "email": "student@example.com",
  "redirectTo": "https://app-domain.com/reset-password"
}
```

Expected response:

```json
{
  "data": {},
  "error": null
}
```

Frontend behavior:

* Show message:

  ```text
  Password reset link sent if this email exists.
  ```

## 16. Supabase Storage Integration

## 16.1 What Supabase Storage Does

Supabase Storage stores uploaded thesis files.

Files include:

* PDF thesis drafts
* DOCX files
* TXT files
* BibTeX files
* CSV results files

## 16.2 Recommended Upload Flow

For the safest MVP:

```text
Frontend → FastAPI backend → Supabase Storage
```

Do not upload directly from the frontend for v1 unless you implement signed upload URLs correctly.

## 16.3 Backend Upload to Supabase Storage

Storage operation:

```text
supabase.storage.from(bucket).upload(path, file)
```

Data sent:

```json
{
  "bucket": "thesisforge-documents",
  "path": "user_id/project_id/document_id/file-name.pdf",
  "file": "binary_file"
}
```

Expected response:

```json
{
  "data": {
    "path": "user_id/project_id/document_id/file-name.pdf"
  },
  "error": null
}
```

Frontend behavior:

The frontend does not see the storage path directly unless needed. It sees a document record from the backend.

## 16.4 Signed File Download

Storage operation:

```text
createSignedUrl(path, expiresIn)
```

Data sent:

```json
{
  "path": "user_id/project_id/document_id/file-name.pdf",
  "expiresIn": 600
}
```

Expected response:

```json
{
  "data": {
    "signedUrl": "temporary_download_url"
  },
  "error": null
}
```

Frontend behavior:

* Open signed URL in a new tab or trigger download.
* Do not store signed URL permanently.
* If URL expires, request a new one.

## 17. Band Integration

## 17.1 What Band Does

Band is the agent collaboration layer.

ThesisForge uses Band so agents can:

* Create a shared chat room for each analysis run
* Add specialist agents as participants
* Send handoff messages
* Record agent events
* Rehydrate context if an agent reconnects
* Show collaboration logs in the frontend

## 17.2 Frontend Rule

The frontend should not call Band directly.

The frontend gets Band activity from your backend:

```text
GET /analysis-runs/{run_id}/agent-messages
```

## 17.3 Backend Band Base URL

```text
https://app.band.ai/api/v1/agent
```

## 17.4 Validate Agent Identity

Endpoint:

```text
GET /agent/me
```

Headers:

```text
X-API-Key: <band_agent_api_key>
```

Expected response:

```json
{
  "id": "agent_id",
  "name": "Research Gap Agent",
  "handle": "research_gap_agent"
}
```

Use case:

* Validate that the Band agent key works.
* Run this when the backend starts or before a workflow begins.

## 17.5 Create Chat Room

Endpoint:

```text
POST /agent/chats
```

Headers:

```text
X-API-Key: <band_agent_api_key>
```

Request:

```json
{
  "chat": {
    "task_id": "analysis_run_uuid"
  }
}
```

Expected response:

```json
{
  "id": "band_chat_id",
  "task_id": "analysis_run_uuid"
}
```

Use case:

* One Band chat room per ThesisForge analysis run.

## 17.6 List Peers

Endpoint:

```text
GET /agent/peers
```

Expected response:

```json
{
  "items": [
    {
      "id": "peer_agent_id",
      "name": "Methodology Agent",
      "handle": "methodology_agent"
    }
  ]
}
```

Use case:

* Find available agents to add to the analysis room.

## 17.7 Add Participant to Chat

Endpoint:

```text
POST /agent/chats/{chat_id}/participants
```

Request:

```json
{
  "participant": {
    "id": "peer_agent_id"
  }
}
```

Expected response:

```json
{
  "id": "participant_id",
  "name": "Methodology Agent",
  "handle": "methodology_agent"
}
```

Use case:

* Add Literature, Gap, Citation, Methodology, Results, Defense, and Report agents to the run room.

## 17.8 Send Agent Message

Endpoint:

```text
POST /agent/chats/{chat_id}/messages
```

Request:

```json
{
  "message": {
    "content": "@research_gap_agent The literature review found that the current gap is too broad.",
    "mentions": [
      {
        "id": "peer_agent_id",
        "name": "Research Gap Agent",
        "handle": "research_gap_agent"
      }
    ]
  }
}
```

Expected response:

```json
{
  "id": "band_message_id",
  "content": "@research_gap_agent The literature review found that the current gap is too broad.",
  "created_at": "2026-06-17T10:00:00Z"
}
```

Use case:

* Agent-to-agent handoff.
* Must be saved locally in `agent_messages`.

## 17.9 Post Agent Event

Endpoint:

```text
POST /agent/chats/{chat_id}/events
```

Request:

```json
{
  "event": {
    "content": "Citation Agent started checking claim-to-reference alignment.",
    "message_type": "task",
    "metadata": {
      "agent": "citation_agent",
      "run_id": "analysis_run_uuid",
      "project_id": "project_uuid"
    }
  }
}
```

Expected response:

```json
{
  "id": "band_event_id",
  "message_type": "task",
  "created_at": "2026-06-17T10:00:00Z"
}
```

Use case:

* Show internal agent activity.
* Useful for frontend timeline.

## 17.10 Get Context for Rehydration

Endpoint:

```text
GET /agent/chats/{chat_id}/context
```

Expected response:

```json
{
  "messages": [
    {
      "id": "band_message_id",
      "content": "@methodology_agent Please check if the method supports the revised gap.",
      "created_at": "2026-06-17T10:00:00Z"
    }
  ]
}
```

Use case:

* Rebuild agent context after reconnect or failure.

## 18. OpenAI Integration

## 18.1 What OpenAI Does

OpenAI provides:

* LLM reasoning for agents
* Structured JSON outputs
* Report generation
* Embeddings for semantic search

## 18.2 Frontend Rule

The frontend must never call OpenAI directly.

Only the backend calls OpenAI.

## 18.3 Generate Agent Output

Endpoint:

```text
POST /v1/responses
```

Headers:

```text
Authorization: Bearer <OPENAI_API_KEY>
Content-Type: application/json
```

Request:

```json
{
  "model": "gpt-4.1-mini",
  "input": [
    {
      "role": "system",
      "content": "You are the Research Gap Agent. Analyze only the provided thesis content."
    },
    {
      "role": "user",
      "content": "Project context and thesis content here..."
    }
  ],
  "temperature": 0.2
}
```

Expected response:

```json
{
  "id": "response_id",
  "output_text": "{ \"score\": 72, \"findings\": [] }",
  "usage": {
    "input_tokens": 1000,
    "output_tokens": 500
  }
}
```

Backend behavior:

* Validate the output.
* Retry if JSON is invalid.
* Save findings in `agent_findings`.
* Send handoff through Band if needed.

## 18.4 Generate Embeddings

Endpoint:

```text
POST /v1/embeddings
```

Headers:

```text
Authorization: Bearer <OPENAI_API_KEY>
Content-Type: application/json
```

Request:

```json
{
  "model": "text-embedding-3-small",
  "input": "This thesis proposes an explainable multimodal deepfake detector.",
  "encoding_format": "float"
}
```

Expected response:

```json
{
  "data": [
    {
      "embedding": [0.012, -0.034, 0.056]
    }
  ],
  "model": "text-embedding-3-small",
  "usage": {
    "prompt_tokens": 20,
    "total_tokens": 20
  }
}
```

Backend behavior:

* Store embedding in `document_chunks.embedding`.
* Use vector search for relevant thesis sections.

## 19. Optional Gemini Integration

## 19.1 Status

Gemini should be optional in v1.

Use it only if:

* OpenAI credits run out
* You want a fallback LLM provider
* Hackathon resources favor Gemini-compatible models

## 19.2 Generate Content

Endpoint pattern:

```text
POST /v1beta/models/{model}:generateContent
```

Headers:

```text
x-goog-api-key: <GEMINI_API_KEY>
Content-Type: application/json
```

Request:

```json
{
  "contents": [
    {
      "parts": [
        {
          "text": "Analyze this research gap and return structured JSON."
        }
      ]
    }
  ]
}
```

Expected response:

```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "{ \"score\": 72, \"findings\": [] }"
          }
        ]
      }
    }
  ]
}
```

## 19.3 Generate Embeddings

Endpoint pattern:

```text
POST /v1beta/models/{model}:embedContent
```

Request:

```json
{
  "content": {
    "parts": [
      {
        "text": "Text to embed"
      }
    ]
  }
}
```

Expected response:

```json
{
  "embedding": {
    "values": [0.012, -0.034, 0.056]
  }
}
```

Frontend behavior:

* None.
* Backend only.

## 20. Error Handling in the Frontend

## 20.1 Auth Errors

Message:

```text
We could not sign you in. Please check your email and password.
```

Do not say:

```text
This email does not exist.
```

## 20.2 Upload Errors

Unsupported file:

```text
This file type is not supported. Please upload PDF, DOCX, TXT, BibTeX, or CSV.
```

File too large:

```text
This file is too large. Please upload a file under 25 MB.
```

Upload failed:

```text
We could not upload your file. Please try again.
```

## 20.3 Analysis Errors

Agent failed:

```text
One review agent could not complete its task. We saved the available results.
```

Band failed:

```text
The agent collaboration service had an issue. Please try running the review again.
```

LLM failed:

```text
The AI review service is temporarily unavailable. Please try again later.
```

## 20.4 Permission Errors

Message:

```text
We could not find this project or you do not have access to it.
```

Do not reveal whether the project exists.

## 21. Accessibility Requirements

## 21.1 Keyboard Support

All interactive elements must be keyboard accessible:

* Buttons
* Inputs
* Modals
* Dropdowns
* Tabs
* File upload controls

## 21.2 Contrast

Text must have strong contrast.

Do not use light gray text on white backgrounds for important information.

## 21.3 Focus States

Every clickable element must have a visible focus ring.

Recommended focus ring:

```text
3px #DBEAFE
```

## 21.4 Error Labels

Every form error should appear near the relevant field.

Example:

```text
Research gap is required before running a full review.
```

## 22. MVP Frontend Build Order

## Phase 1: Foundation

Build:

* Next.js setup
* Tailwind setup
* shadcn/ui setup
* Auth layout
* App shell
* Sidebar
* Navbar

## Phase 2: Core Product Flow

Build:

* Dashboard
* Create project page
* Project overview page
* Upload page
* Run review page
* Report page

## Phase 3: Agent Visibility

Build:

* Agent status cards
* Agent timeline
* Agent collaboration log
* Run progress polling

## Phase 4: Report UX

Build:

* Thesis score card
* Score breakdown
* Markdown report renderer
* Priority fixes list
* Defense questions list
* Copy report button

## Phase 5: Polish

Build:

* Empty states
* Error states
* Loading skeletons
* Mobile sidebar
* Responsive report page
* Toast notifications

## 23. MVP Component Checklist

Must build:

* Button
* Input
* Textarea
* Select
* Card
* Modal
* Badge
* Toast
* File upload
* Sidebar
* Navbar
* Project card
* Agent timeline
* Agent log card
* Score card
* Report section
* Priority task list
* Empty state
* Error state
* Loading skeleton

## 24. Final Frontend Recommendation

For version one, the frontend should be simple, structured, and demo-friendly.

The most important screens are:

1. Create project
2. Upload/paste thesis material
3. Run review
4. Agent collaboration timeline
5. Final thesis health report

The strongest hackathon demo screen will be the agent collaboration timeline because it proves that ThesisForge is not just a chatbot. It is a multi-agent research workflow system.
