## Career Co-Pilot – AI Resume & Outreach Architect

### 1. Project Overview

Career Co-Pilot is a web application that automates key parts of the job application workflow:

- **Ingest** a user’s base resume (`.docx`).
- **Scrape & analyze** LinkedIn job postings.
- **Align** the resume to each role (skills, experience ordering, international logic).
- **Generate** tailored cover letters and outreach templates (email + LinkedIn DM).
- **Export** finalized artifacts as downloadable `.docx` files.

The goal is a **lean, modern UI** on top of a **modular, LLM‑orchestrated backend** that can later scale to different databases and cloud environments.

---

### 2. Architecture Overview (High-Level)

- **Frontend (React + Tailwind CSS)**
  - Single-page app (SPA) dashboard.
  - Handles resume upload, LinkedIn URL input, review of “before vs after” resume, and outreach copy.
  - Communicates with the backend via JSON REST APIs and file upload/download endpoints.

- **Backend (FastAPI)**
  - REST API layer.
  - Orchestrates scraping, parsing, LLM workflows, and document generation.
  - Implements a **Repository Pattern** over SQLite for persistence of resumes, jobs, and alignment runs.

- **Orchestration (LangChain / LangGraph)**
  - Chains for:
    - Job description analysis.
    - Resume alignment (bullets + ordering + international logic).
    - Outreach generation (cover letter + email + LinkedIn DM).
  - Encapsulated in dedicated services to keep FastAPI endpoints thin.

- **LLM (Google Gemini via Google Generative AI SDK)**
  - Used as the core model for text understanding and generation.
  - Access wrapped by a service that reads `GOOGLE_API_KEY` from environment variables.

- **Storage & Files**
  - **Database**: SQLite (initial), accessed via repositories and SQLAlchemy models.
  - **Files**: `.docx` base resumes and generated resumes stored in a `storage/` directory, never committed (ignored via `.gitignore`).
  - **File parsing & generation**: `python-docx` (or equivalent) used to read/write `.docx`.

High-level request flow:

1. User uploads base resume (`.docx`) → frontend → FastAPI → stored to disk + DB metadata.
2. User submits LinkedIn job URL → FastAPI calls scraper → JD text extracted.
3. FastAPI orchestrates LLM chain:
   - Analyze JD → key skills & must-haves.
   - Compare JD vs base resume (including “hidden matches”).
   - Generate aligned resume text + international-tailored elements if applicable.
4. FastAPI converts aligned resume text to a `.docx` and exposes it for download.
5. LLM generates cover letter + email + LinkedIn DM templates.
6. Frontend shows “Before vs After” diff and provides copy/download actions.

---

### 3. Detailed Architecture & Directory Structure (Low-Level)

#### 3.1 Project Layout

At repo root (`Career-Co-Pilot/`):

- `backend/`
  - `app/`
    - `main.py` – FastAPI app entrypoint, CORS, routing.
    - `config.py` – settings (env variables, API keys, DB URL).
    - `database.py` – SQLAlchemy engine/session creation.
    - `models.py` – SQLAlchemy ORM models (Resume, JobPosting, AlignmentRun).
    - `schemas.py` – Pydantic request/response models.
    - `repositories/`
      - `resume_repository.py`
      - `job_repository.py`
      - `alignment_repository.py`
    - `services/`
      - `scraper_service.py` – LinkedIn JD scraper.
      - `resume_service.py` – parse base resume `.docx`, prepare text.
      - `alignment_service.py` – LangChain/LangGraph pipeline for alignment workflow.
      - `outreach_service.py` – cover letter, email, LinkedIn DM generation.
      - `docx_service.py` – `.docx` generation utilities.
      - `llm_client.py` – wrapper around Google Gemini SDK + LangChain.
    - `routers/`
      - `resume_router.py` – upload/manage base resume.
      - `job_router.py` – accept LinkedIn URL, return parsed JD and skills.
      - `alignment_router.py` – run the alignment workflow, provide downloadable resume.
      - `outreach_router.py` – generate cover letter and outreach copy.
  - `requirements.txt`

- `frontend/`
  - `index.html`
  - `src/`
    - `main.tsx` – React root.
    - `App.tsx` – main dashboard layout.
    - `components/`
      - `BaseResumeCard.tsx`
      - `JobUrlForm.tsx`
      - `AlignmentReview.tsx`
      - `OutreachPanel.tsx`
    - `lib/api.ts` – small API client wrappers.
    - `types/` – shared TypeScript types aligned with backend responses.
  - `tailwind.config.js`
  - `postcss.config.js`
  - `tsconfig.json`
  - `package.json` – React, Tailwind, tooling.

- `storage/` – local filesystem storage for `.docx` and SQLite DB.
  - `resumes/`
  - `generated/`
  - `db.sqlite3`

- `.env` – environment variables; **not committed**.
- `.gitignore` – ignores `.env`, `storage/`, `*.docx`, `*.db`, `__pycache__/`, `node_modules/`, etc.
- `Instructions.md` – original high-level brief.

---

### 4. Backend Low-Level Design

#### 4.1 Data Models (SQLAlchemy)

- **Resume**
  - `id: int`
  - `user_id: str | None` (future multi-user support; can be a UUID or email hash).
  - `file_path: str` – file system path to `.docx` base resume.
  - `text_content: str` – extracted plain text (for fast LLM input).
  - `created_at: datetime`
  - `updated_at: datetime`

- **JobPosting**
  - `id: int`
  - `url: str`
  - `raw_html: str | None`
  - `jd_text: str` – cleaned job description text.
  - `is_international: bool` – derived flag based on location (outside India).
  - `location: str | None`
  - `company_name: str | None`
  - `poster_name: str | None` – used for LinkedIn DM personalization.
  - `contact_email: str | None` – if parsed from JD.
  - `created_at: datetime`

- **AlignmentRun**
  - `id: int`
  - `resume_id: int (FK → Resume.id)`
  - `job_posting_id: int (FK → JobPosting.id)`
  - `aligned_resume_text: str` – final aligned resume body (for re-generation).
  - `aligned_resume_file_path: str | None` – path to generated `.docx`.
  - `cover_letter: str`
  - `email_template: str`
  - `linkedin_dm: str`
  - `hidden_matches_summary: str` – narrative explanation of “hidden matches”.
  - `created_at: datetime`

Repositories encapsulate access to these models and prevent direct ORM usage in routers.

#### 4.2 Repository Pattern

Each repository exposes a small interface (Python class) such as:

- `ResumeRepository`
  - `get_latest_for_user(user_id: str | None) -> Resume`
  - `create_or_replace_resume(...) -> Resume`

- `JobRepository`
  - `create_from_scrape(url: str, jd_text: str, meta: dict) -> JobPosting`
  - `get(id: int) -> JobPosting`

- `AlignmentRepository`
  - `create_alignment(...) -> AlignmentRun`
  - `get(id: int) -> AlignmentRun`

The FastAPI routers depend on these repositories via dependency injection (e.g. `Depends(get_resume_repository)`), allowing the underlying DB (SQLite → PostgreSQL/DynamoDB later) to change without touching endpoint logic.

#### 4.3 FastAPI Routers & Endpoints

- **`/api/resume`**
  - `POST /api/resume/base`
    - Request: multipart form with `file: UploadFile` (`.docx`).
    - Flow:
      - Validate file type.
      - Store original file under `storage/resumes/`.
      - Parse `.docx` → structured text via `resume_service`.
      - Persist `Resume` via `ResumeRepository`.
    - Response: JSON with `resume_id`, summary of detected sections (e.g., skills, experience count).

  - `GET /api/resume/base/latest`
    - Response: latest base resume metadata and short preview text.

- **`/api/job`**
  - `POST /api/job/analyze`
    - Body: `{ "url": string }`
    - Flow:
      - `scraper_service` fetches HTML from LinkedIn URL (requests + fallback to Playwright if blocked).
      - Extract JD text, location, company, HR/poster name, contact email.
      - Use LLM (optional) to refine JD text if noisy.
      - Persist to `JobPosting`.
      - Detect `is_international` based on location (simple: location does not contain "India").
    - Response: JD text, key metadata, and `job_id`.

- **`/api/alignment`**
  - `POST /api/alignment/run`
    - Body: `{ "resume_id": int, "job_id": int }`
    - Flow:
      - Load `Resume` and `JobPosting`.
      - Determine `is_international` from `JobPosting`.
      - Call `alignment_service.align_resume(resume, job)`:
        - Extract key skills & must-haves (LLM).
        - Compare vs resume (LLM prompt with JD + resume text).
        - Identify hidden matches and rewrite relevant bullets.
        - Reorder sections if international (bring onsite/international experience up, add relocation/visa statement).
      - Generate aligned `.docx` via `docx_service`.
      - Persist `AlignmentRun`.
    - Response: alignment summary (skills, hidden matches, key changes), `alignment_id`, and a URL for download.

  - `GET /api/alignment/{alignment_id}/download`
    - Returns: aligned resume `.docx` as file download.

- **`/api/outreach`**
  - `POST /api/outreach/generate`
    - Body: `{ "alignment_id": int }`
    - Flow:
      - Load `AlignmentRun` + `JobPosting`.
      - `outreach_service` calls LLM to generate:
        - Cover letter: using aligned resume + JD + international context.
        - Email: uses any detected HR email + mailto-ready subject & body.
        - LinkedIn DM: concise InMail style message using poster name if available.
      - Update `AlignmentRun` with generated texts.
    - Response: `{ cover_letter, email_template, linkedin_dm }`.

---

### 5. Orchestration & LLM Workflow (Low-Level)

#### 5.1 LLM Client Abstraction

`services/llm_client.py`:

- Initializes the Google Generative AI SDK with `GOOGLE_API_KEY` from `.env`.
- Exposes a small, framework-agnostic interface, e.g.:
  - `generate_text(prompt: str, temperature: float = 0.4) -> str`
  - `structured_call(prompt: str, schema: dict) -> dict` (optional for JSON outputs).

LangChain / LangGraph integration:

- The client is wrapped in LangChain `LLM` or used as a tool in LangGraph.
- Prompt templates and chains live in `alignment_service` and `outreach_service`, keeping all Gemini-specific details encapsulated.

#### 5.2 Alignment Chain

Inputs:

- `JD_Text` – cleaned job description.
- `Base_Resume_Text` – plain text from `.docx`.
- `Is_International` – boolean.

Steps (could be a LangGraph state machine):

1. **JD Analysis Node**
   - Prompt: “Extract must-have skills, nice-to-have skills, responsibilities, and any explicit visa/relocation hints.”
   - Output: structured JSON with skills and requirements.

2. **Resume Gap & Hidden Match Analysis Node**
   - Prompt: “Given JD analysis and resume text, list:
     - (a) Direct matches.
     - (b) Hidden matches (skills present but phrased differently).
     - (c) Gaps.”

3. **Resume Rewriting Node**
   - Prompt: “Rewrite the resume bullets to:
     - Emphasize must-have skills.
     - Surface hidden matches clearly.
     - Respect brevity and ATS friendliness.”
   - If `Is_International = true`:
     - Bring any international/onsite experience higher.
     - Add a concise relocation & visa willingness statement.

4. **Formatting Node**
   - Ensures output is structured by sections (Summary, Experience, Skills, etc.) to be mapped cleanly into `.docx` generation templates.

Outputs:

- `aligned_resume_sections: dict` (per-section text).
- `hidden_matches_summary: str`.

#### 5.3 Outreach Chain

Inputs:

- `Aligned_Resume_Text`
- `JD_Text`
- `Job_Metadata` (company, role, poster name, email).

Outputs:

- `cover_letter: str`
- `email_template: { subject: str, body: str }`
- `linkedin_dm: str`

Prompts emphasize:

- Personalized yet reusable structure.
- Clear mention of relevant skills from alignment step.
- International relocation & visa context where relevant.

---

### 6. Frontend Low-Level Design

#### 6.1 Screens & Components

- **Dashboard (root)**
  - **`BaseResumeCard`**
    - Shows current base resume status (uploaded / not uploaded).
    - Button to upload/replace `.docx`.
  - **`JobUrlForm`**
    - Input for LinkedIn job URL.
    - On submit: calls `/api/job/analyze`, shows loading & error states.
  - **`AlignmentReview`**
    - Once JD + base resume exist:
      - Trigger `/api/alignment/run`.
      - Display:
        - High-level alignment summary (skills, hidden matches, international logic applied).
        - Side-by-side “Before vs After” text snippet view.
      - Button: “Download aligned resume (.docx)” (hits `/api/alignment/{id}/download`).
  - **`OutreachPanel`**
    - Button: “Generate outreach templates”.
    - Shows:
      - Tailored cover letter (copy button).
      - Email template with “Copy” and optionally “Open mail client” (mailto link).
      - LinkedIn DM text (copy button).

#### 6.2 API Client Layer

`frontend/src/lib/api.ts`:

- `uploadBaseResume(file: File): Promise<BaseResume>`
- `analyzeJob(url: string): Promise<JobAnalysis>`
- `runAlignment(resumeId: number, jobId: number): Promise<AlignmentRun>`
- `downloadAlignedResume(alignmentId: number): void` (triggers browser download).
- `generateOutreach(alignmentId: number): Promise<OutreachBundle>`

This keeps components UI-focused and avoids repeating `fetch` logic.

#### 6.3 State Management

- Local React state (and optionally React Query/SWR) handles:
  - Current `BaseResume`.
  - Current `JobPosting`.
  - Last `AlignmentRun`.
  - `OutreachBundle`.
- Loading and error states for each async interaction.

---

### 7. Security, Safety & Standards

- **Environment Variables**
  - `.env` holds:
    - `GOOGLE_API_KEY`
    - `DATABASE_URL` (default `sqlite:///./storage/db.sqlite3`)
    - Any scraping-related configuration (user agent, proxy, etc.).

- **Git Ignore**
  - `.env`
  - `storage/` (all `.docx` files, DB file, generated documents).
  - `__pycache__/`
  - `*.db`
  - `node_modules/`

- **Scraping Safety**
  - Respect LinkedIn’s terms and robots; for production, consider official APIs or user-provided JD text instead of automated scraping.
  - In this implementation, the scraper module is designed to fail gracefully and can be swapped for a manual “paste JD text” workflow.

- **Error Handling**
  - Clear error messages for:
    - Invalid or private LinkedIn URLs.
    - Invalid file types for resumes.
    - Missing `GOOGLE_API_KEY`.
  - FastAPI exception handlers translate backend issues into clean JSON errors consumed by the frontend.

---

### 8. Implementation Notes & Next Steps

- **Minimal Vertical Slice (MVP)**
  - Implement base resume upload, JD analysis (with a stub scraper if needed), and alignment workflow with mocked LLM responses.
  - Wire up the frontend dashboard to exercise the full flow end-to-end.

- **LLM & Scraper Hardening**
  - Plug in the real Google Gemini SDK and LangChain/LangGraph flows once keys are configured.
  - Replace simple HTTP scraping with Playwright/Selenium if LinkedIn blocking is encountered.

- **Database Swap Readiness**
  - Because the backend uses repository interfaces, swapping SQLite for PostgreSQL or DynamoDB is primarily a configuration and driver change, not an application rewrite.

