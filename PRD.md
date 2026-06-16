# Product Requirements Document

## Product Name: ThesisForge

### Multi-Agent Research Workflow Assistant Powered by Band

## 1. Product Summary

**ThesisForge** is a multi-agent research workflow assistant that helps students and early-stage researchers improve the quality, consistency, and defense readiness of their thesis or research project.

The app allows users to upload or paste thesis-related materials such as a research title, problem statement, research gap, methodology, references, result summary, and supervisor feedback. A team of specialized AI agents then collaborates to review the work, identify weaknesses, validate claims, check citation alignment, find methodology inconsistencies, and generate actionable improvement tasks.

The product is not designed to write the entire thesis for the user. Instead, it acts as a research quality-control system that helps users understand what is weak, missing, unsupported, or inconsistent in their work.

## 2. Product Vision

To become the operating system for academic research workflows, where students and researchers can manage literature review, research gaps, methodology, citations, experiments, supervisor feedback, and defense preparation in one structured multi-agent workspace.

## 3. Problem Statement

Thesis and research work is highly fragmented. Students usually manage their workflow across many disconnected tools:

* Google Scholar for papers
* Zotero or Mendeley for references
* Word, Google Docs, or LaTeX for writing
* Excel or CSV files for results
* GitHub or Google Drive for code and files
* Email, WhatsApp, or meeting notes for supervisor feedback

Because these tools do not communicate with each other, students often face serious research workflow problems:

1. The research gap becomes outdated after reading more papers.
2. Citations are added but may not strongly support the written claims.
3. The methodology described in the thesis may not match the actual experiment.
4. Supervisor feedback is scattered and hard to track.
5. Results are reported but not properly interpreted.
6. Students struggle to prepare for thesis defense questions.
7. Final quality checks are done manually and often too late.

This leads to weak research arguments, inconsistent chapters, poor citation support, and stressful final submissions.

## 4. Target Users

### Primary Users

#### 1. Undergraduate Thesis Students

Students working on final-year thesis or capstone research projects who need help organizing and improving their research quality.

#### 2. Master’s Students

Students writing a dissertation who need support with literature review, methodology alignment, citation quality, and defense preparation.

#### 3. Early-Stage Researchers

Beginner researchers preparing conference papers, journal drafts, or research proposals.

### Secondary Users

#### 1. Supervisors and Faculty Members

Supervisors who want a quick structured review of a student’s thesis progress before meetings.

#### 2. Research Teams

Small academic teams working collaboratively on papers, thesis projects, or grant proposals.

#### 3. University Research Labs

Labs that want a repeatable process for reviewing student research quality.

## 5. User Personas

### Persona 1: Final-Year Thesis Student

**Name:** Rahul
**Goal:** Complete thesis with strong research gap, methodology, citations, and defense preparation.
**Pain Points:** Too many files, unclear research gap, weak citation management, unsure what panel may ask.
**Success Outcome:** Gets a clear improvement report and knows exactly what to fix before submission.

### Persona 2: Research Supervisor

**Name:** Dr. Ahmed
**Goal:** Review student progress quickly and identify major weaknesses.
**Pain Points:** Students submit incomplete drafts, unclear methodology, weak literature support.
**Success Outcome:** Gets a concise thesis health report before the meeting.

### Persona 3: Research Team Lead

**Name:** Sara
**Goal:** Coordinate literature, experiments, writing, and feedback among team members.
**Pain Points:** Team members work separately, claims and results become inconsistent.
**Success Outcome:** Uses the app to detect misalignment and generate team tasks.

## 6. Core Value Proposition

ThesisForge helps thesis students and researchers answer four critical questions:

1. **Is my research gap clear and valid?**
2. **Are my claims supported by citations?**
3. **Does my methodology actually solve my stated problem?**
4. **Am I ready to defend this work in front of a panel?**

The app turns scattered thesis materials into a structured, agent-reviewed improvement report.

## 7. Product Goals

### Business Goals

* Demonstrate a strong multi-agent workflow suitable for the Band of Agents Hackathon.
* Build a practical product that solves a real academic workflow problem.
* Show clear enterprise or institutional value for universities, labs, and research teams.
* Create a product that can later evolve into a SaaS tool for academic research management.

### User Goals

* Save time reviewing thesis quality.
* Identify weak sections before supervisor or panel review.
* Improve research gap, methodology, citation, and result alignment.
* Track supervisor feedback as actionable tasks.
* Prepare better for thesis defense.

### Technical Goals

* Use at least 3 specialized AI agents.
* Use Band as the agent collaboration and context-sharing layer.
* Provide a simple user interface for uploading or entering thesis materials.
* Generate a structured final research review report.
* Show transparent agent-to-agent communication logs.

## 8. Product Scope

### In Scope for Version 1

Version 1 focuses on thesis review and quality control.

The user can provide thesis-related content, run a multi-agent review, and receive a structured improvement report.

The app should support:

* Thesis project creation
* Text input or file upload
* Multi-agent analysis
* Research gap review
* Citation and claim support review
* Methodology consistency review
* Result interpretation review
* Defense question generation
* Final report generation
* Agent communication log

### Out of Scope for Version 1

Version 1 will not support full thesis writing, plagiarism detection, full reference manager syncing, supervisor collaboration accounts, or production-level university deployment.

## 9. Core Features

## 9.1 Must-Have Features

### Feature 1: Thesis Project Setup

**Description:**
The user creates a new thesis review project by entering basic information.

**Inputs:**

* Thesis title
* Research domain
* Problem statement
* Research gap
* Research objectives
* Methodology summary
* Dataset or experiment summary
* Results summary
* References or BibTeX text

**User Value:**
Creates a structured starting point for agent analysis.

**Priority:** Must-have

---

### Feature 2: Thesis Content Upload or Paste

**Description:**
The user can either paste thesis sections manually or upload basic files.

**Supported MVP Inputs:**

* Plain text
* PDF
* DOCX
* BibTeX
* CSV result summary

**User Value:**
Makes the app useful for real thesis workflows instead of only demo text.

**Priority:** Must-have

---

### Feature 3: Multi-Agent Workflow Using Band

**Description:**
The system uses multiple specialized agents that communicate through Band.

**Minimum Agents:**

1. Literature Review Agent
2. Research Gap Agent
3. Methodology Consistency Agent
4. Defense Preparation Agent

**User Value:**
Shows that the app is not a single chatbot. It is a coordinated research workflow system.

**Priority:** Must-have

---

### Feature 4: Literature Review Agent

**Description:**
This agent reviews provided references and extracts key claims, methods, datasets, and limitations.

**Responsibilities:**

* Identify major themes from provided references
* Extract what each paper supports
* Detect weak or missing citation support
* Highlight outdated or irrelevant references
* Send findings to the Research Gap Agent

**Output:**

* Paper summary table
* Claim-support mapping
* Weak citation warnings
* Suggested literature gaps

**Priority:** Must-have

---

### Feature 5: Research Gap Agent

**Description:**
This agent checks whether the research gap is clear, specific, and supported by the literature.

**Responsibilities:**

* Evaluate if the gap is too broad
* Check whether the gap is already solved by cited work
* Suggest a more specific research gap
* Align the gap with problem statement and objectives

**Output:**

* Gap quality score
* Problems in current gap
* Suggested improved gap
* Missing literature areas

**Priority:** Must-have

---

### Feature 6: Methodology Consistency Agent

**Description:**
This agent checks whether the methodology matches the research problem, gap, objectives, datasets, and reported results.

**Responsibilities:**

* Detect mismatch between objectives and methods
* Check whether experiments support the proposed claims
* Identify missing baselines, ablations, or evaluation metrics
* Flag unsupported result interpretations

**Output:**

* Methodology consistency score
* Missing experiment list
* Result interpretation warnings
* Suggested methodology fixes

**Priority:** Must-have

---

### Feature 7: Defense Preparation Agent

**Description:**
This agent generates possible thesis panel questions based on weaknesses found by other agents.

**Responsibilities:**

* Generate likely defense questions
* Categorize questions by topic
* Suggest short answer directions
* Highlight high-risk questions

**Output:**

* Panel question list
* Risk level per question
* Suggested answer points

**Priority:** Must-have

---

### Feature 8: Final Thesis Health Report

**Description:**
The app combines all agent outputs into a final structured report.

**Report Sections:**

1. Overall thesis health score
2. Research gap review
3. Citation support review
4. Methodology consistency review
5. Results and experiment review
6. Defense readiness questions
7. Priority fixes
8. Suggested next steps

**User Value:**
Gives the user a clear action plan instead of scattered AI responses.

**Priority:** Must-have

---

### Feature 9: Agent Collaboration Log

**Description:**
The user can see how agents passed information to each other.

**Example Log:**

```text
Literature Agent → Research Gap Agent:
Found that the current research gap is too broad and lacks support from recent multimodal research papers.

Research Gap Agent → Methodology Agent:
Updated research gap focuses on interpretable multimodal reasoning. Please check if the methodology addresses this.

Methodology Agent → Defense Agent:
Methodology lacks ablation study for the symbolic reasoning layer. Generate possible panel questions.
```

**User Value:**
Makes the multi-agent workflow visible and strengthens the hackathon demo.

**Priority:** Must-have

---

## 9.2 Nice-to-Have Features

### Feature 10: Supervisor Feedback Tracker

**Description:**
The user can paste supervisor feedback and the app converts it into structured tasks.

**Output:**

* Task title
* Priority
* Related thesis section
* Suggested fix

**Priority:** Nice-to-have

---

### Feature 11: LaTeX Consistency Checker

**Description:**
The app checks common LaTeX thesis issues.

**Checks:**

* Missing figure references
* Missing table references
* Citation key errors
* Equation numbering issues
* Section hierarchy issues

**Priority:** Nice-to-have

---

### Feature 12: Research Timeline Planner

**Description:**
The app creates a simple thesis improvement timeline.

**Output:**

* Tasks for this week
* High-priority fixes
* Defense preparation schedule

**Priority:** Nice-to-have

---

### Feature 13: Export to PDF or DOCX

**Description:**
The user can export the final thesis review report.

**Priority:** Nice-to-have

---

### Feature 14: Reference Manager Integration

**Description:**
Future integration with Zotero, Mendeley, or Google Scholar.

**Priority:** Nice-to-have, not MVP

---

### Feature 15: Team Collaboration

**Description:**
Multiple students can collaborate on the same thesis project.

**Priority:** Nice-to-have, not MVP

## 10. User Flow

## 10.1 First-Time User Flow

### Step 1: User Opens App

The user lands on the homepage and sees:

* Product name
* Short explanation
* “Start Thesis Review” button

### Step 2: User Creates a Thesis Project

The user enters:

* Thesis title
* Research area
* Current thesis stage
* Target output

Example target outputs:

* Research gap review
* Full thesis health check
* Defense preparation
* Methodology consistency check

### Step 3: User Provides Thesis Materials

The user can:

* Paste text manually
* Upload thesis draft
* Upload references
* Upload result summary
* Paste supervisor feedback

### Step 4: User Starts Multi-Agent Review

The user clicks:

**Run ThesisForge Review**

The system starts the agent workflow.

### Step 5: Agents Analyze the Thesis

The workflow runs in this order:

1. Literature Review Agent extracts claims and citation support.
2. Research Gap Agent validates the gap.
3. Methodology Consistency Agent checks alignment.
4. Defense Preparation Agent generates questions.
5. Report Agent compiles the final output.

### Step 6: User Views Agent Collaboration Log

The user sees how the agents communicated.

This proves the app is using a real multi-agent workflow.

### Step 7: User Receives Final Report

The user gets:

* Thesis health score
* Major weaknesses
* Priority fixes
* Improved research gap suggestion
* Methodology improvement suggestions
* Citation warnings
* Defense questions

### Step 8: User Takes Action

The user can:

* Copy the report
* Download the report
* Use the task list to improve the thesis
* Run another review after editing

## 11. MVP Definition

The MVP should prove that ThesisForge can review a thesis workflow using multiple AI agents that collaborate through Band.

## 11.1 MVP Must Include

### 1. Simple Frontend

A simple Streamlit or basic web interface where the user can:

* Enter thesis title
* Paste thesis sections
* Upload references or BibTeX
* Click a button to run analysis
* View final report

### 2. Backend Agent Workflow

A backend using FastAPI or Python that manages:

* Input processing
* Agent execution
* Band communication
* Final report generation

### 3. At Least 4 Agents

Minimum agent set:

1. Literature Review Agent
2. Research Gap Agent
3. Methodology Consistency Agent
4. Defense Preparation Agent

### 4. Band Integration

Band must be used for real agent communication.

Band should handle:

* Agent messages
* Shared context
* Handoffs
* Collaboration history

### 5. Final Report

The final report should include:

* Overall thesis score
* Research gap feedback
* Citation feedback
* Methodology feedback
* Defense questions
* Priority improvements

### 6. Demo Dataset

Include sample thesis data for demo purposes.

Example:

* Sample thesis title
* Sample research gap
* Sample methodology
* Sample references
* Sample results

## 11.2 MVP User Experience

The MVP does not need to be beautiful. It needs to be clear.

The user should be able to complete this journey:

```text
Open app → Enter thesis data → Run review → Watch agents collaborate → Get final report
```

## 12. Recommended MVP Tech Stack

### Frontend

**Recommended:** Streamlit
Reason: Fast to build, good for hackathon demos, supports file upload easily.

Alternative: Next.js
Use only if there is enough time.

### Backend

**Recommended:** FastAPI
Reason: Clean API structure and easy integration with Python agents.

### Agent Orchestration

**Recommended:** LangGraph
Reason: Good for multi-step agent workflows.

### Agent Collaboration Layer

**Required for Hackathon:** Band
Reason: The hackathon focuses on agent collaboration through Band.

### LLM Provider

Possible options:

* OpenAI
* Gemini
* AI/ML API
* Featherless AI

### File Processing

* PyMuPDF for PDF
* python-docx for DOCX
* bibtexparser for BibTeX
* pandas for CSV result files

### Storage

For MVP:

* Local JSON files
* SQLite

For future:

* PostgreSQL
* Vector database

## 13. Functional Requirements

## 13.1 Project Creation

The system must allow users to create a thesis project with basic metadata.

**Required Fields:**

* Project title
* Research area
* Thesis stage
* Main objective

## 13.2 Content Input

The system must allow the user to provide thesis material through text input or upload.

**Required Content Types:**

* Problem statement
* Research gap
* Methodology
* References
* Results summary

## 13.3 Agent Execution

The system must run agents in a structured workflow.

**Required Behavior:**

* Agents must have separate responsibilities.
* Agents must exchange structured context.
* Agent outputs must be saved.
* Final response must combine all agent outputs.

## 13.4 Band Communication

The system must send and receive agent messages through Band.

**Required Message Fields:**

```json
{
  "from_agent": "LiteratureAgent",
  "to_agent": "ResearchGapAgent",
  "task": "validate_research_gap",
  "context": {},
  "findings": [],
  "next_action": ""
}
```

## 13.5 Report Generation

The system must generate a final report using all agent outputs.

**Required Report Sections:**

* Executive summary
* Thesis health score
* Key risks
* Agent findings
* Recommended fixes
* Defense questions

## 14. Non-Functional Requirements

### Performance

* Analysis should complete within a reasonable demo time.
* MVP target: under 2 minutes for a short thesis sample.

### Reliability

* If one agent fails, the system should show a meaningful error.
* The app should not crash on missing optional fields.

### Usability

* The interface should be simple enough for a thesis student to use without training.
* Outputs should be structured, readable, and actionable.

### Transparency

* The system should show which agent produced which output.
* The system should display agent handoffs.

### Security

* For MVP, avoid storing sensitive thesis files permanently unless necessary.
* Add a simple disclaimer that uploaded content is used for analysis.

## 15. Success Metrics

## 15.1 Product Success Metrics

### Activation

* Percentage of users who create a project and run their first thesis review.
* Target MVP success: 70%+ of demo users complete the first review flow.

### Completion

* Percentage of users who reach the final report screen.
* Target MVP success: 80%+ completion in demo environment.

### Output Usefulness

* User rating of final report usefulness.
* Target MVP success: average rating of 4 out of 5.

### Time Saved

* Self-reported time saved compared to manual thesis review.
* Target MVP success: users feel it saves at least 1–2 hours of manual review.

### Actionability

* Number of clear improvement tasks generated per review.
* Target MVP success: at least 5 useful action items per thesis review.

## 15.2 Hackathon Success Metrics

* Clear use of at least 3 agents.
* Band is visibly used for agent collaboration.
* Demo shows agent-to-agent handoff.
* Final report solves a real thesis workflow problem.
* Judges can understand the value within 2 minutes.
* GitHub repo is clean and reproducible.
* Video demo clearly explains the problem, solution, workflow, and impact.

## 16. Version 1 Non-Goals

These are deliberately not being built in version one.

### 1. Full Thesis Generation

The app will not write the entire thesis automatically.

Reason: This creates academic integrity concerns and weakens the product’s positioning. The app should improve research quality, not replace the student.

### 2. Plagiarism Detection

The app will not perform plagiarism checking.

Reason: This requires specialized databases and institutional integrations.

### 3. Full Google Scholar Search

The app will not automatically crawl Google Scholar.

Reason: It is technically fragile and may violate platform restrictions.

### 4. Zotero or Mendeley Sync

The app will not sync with reference managers in version one.

Reason: Useful later, but not needed to prove MVP value.

### 5. Multi-User Collaboration

The app will not support team accounts, comments, or supervisor dashboards in version one.

Reason: MVP should focus on single-user thesis review first.

### 6. Full LaTeX Compilation

The app will not compile or fully validate LaTeX projects.

Reason: This is a separate technical scope.

### 7. University LMS Integration

The app will not integrate with Moodle, Blackboard, Canvas, or university portals.

Reason: Too large for version one.

### 8. Payment System

The app will not include subscriptions, billing, or premium plans.

Reason: Not required for hackathon MVP.

### 9. Long-Term Research Project Management

The app will not include full project management features like Kanban boards, calendars, or team assignments.

Reason: The MVP only needs review, feedback, and improvement planning.

## 17. Risks and Mitigations

### Risk 1: The App Looks Like a Simple Chatbot

**Mitigation:**
Show separate agents, clear agent responsibilities, and visible Band communication logs.

### Risk 2: Output Is Too Generic

**Mitigation:**
Force agents to cite specific user-provided sections, references, claims, and methodology points.

### Risk 3: Users Expect the App to Write the Thesis

**Mitigation:**
Position the product as a quality-control and research workflow assistant, not a thesis writer.

### Risk 4: Band Integration Is Not Clear

**Mitigation:**
Add a dedicated “Agent Collaboration Log” section in the frontend and demo video.

### Risk 5: File Parsing Takes Too Much Time

**Mitigation:**
For MVP, support pasted text first. Add file upload only if time allows.

## 18. MVP Demo Scenario

### Example Demo Input

**Thesis Title:**
Explainable Multimodal Deepfake Detection Using Neuro-Symbolic Reasoning

**Problem Statement:**
Modern deepfake detection systems often achieve high accuracy but lack interpretability and cross-modal reasoning.

**Research Gap:**
Existing systems do not properly combine facial behavior, gaze movement, and audio emotion for explainable detection.

**Methodology:**
The system uses visual, ocular, and audio branches. The outputs are fused and passed into a neuro-symbolic predicate layer.

**Results:**
The proposed system improves AUC across three benchmark datasets.

**References:**
The user uploads or pastes several related paper citations.

### Expected Demo Output

The app produces:

1. A warning that the research gap is too broad.
2. A suggestion to make the gap more specific around interpretable multimodal reasoning.
3. A citation warning for unsupported claims.
4. A methodology warning about missing ablation studies.
5. A list of likely defense questions.
6. A final priority task list.

## 19. Example Final Output Structure

```text
Thesis Health Score: 76/100

Main Strength:
Your thesis has a clear direction and strong multimodal motivation.

Main Weakness:
The research gap is currently too broad and needs stronger citation support.

Priority Fixes:
1. Narrow the research gap to interpretable multimodal reasoning.
2. Add citations for audio-visual inconsistency detection.
3. Add ablation study for the neuro-symbolic predicate layer.
4. Clarify why each dataset was selected.
5. Prepare defense answers for model complexity and generalization.

High-Risk Defense Questions:
1. Why is your method better than existing multimodal deepfake detectors?
2. How do you prove the symbolic predicate layer improves interpretability?
3. Why did you choose these datasets?
4. What happens if one modality is missing or noisy?
```

## 20. Launch Plan for Hackathon

### Phase 1: Build Core Workflow

* Create basic backend
* Define agent prompts
* Implement LangGraph workflow
* Connect Band for agent handoff
* Generate final report

### Phase 2: Build Simple Frontend

* Add text input fields
* Add file upload if possible
* Add run button
* Display agent outputs
* Display final report

### Phase 3: Prepare Demo

* Create sample thesis input
* Record agent collaboration flow
* Show Band communication log
* Explain business and academic value

### Phase 4: Submit

Prepare:

* GitHub repository
* README
* Demo video
* Slide deck
* Cover image
* App URL
* Project description

## 21. Final MVP Positioning

ThesisForge is not an AI thesis writer.

It is a multi-agent research workflow assistant that helps students and researchers validate their thesis quality before submission or defense.

The key product promise is:

**“Upload your thesis draft. Let a team of AI research agents review your gap, citations, methodology, results, and defense readiness.”**
