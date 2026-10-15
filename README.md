# AI Resume Analyzer

An intelligent resume analysis, job-matching, and rewriting system powered by LLMs and LangGraph. Upload a PDF resume, get a detailed ATS score with actionable feedback, a resume-vs-job-description match analysis, and optionally generate an ATS-optimized LaTeX resume in one of eleven selectable templates.

The project ships three interfaces plus one experimentation workflow:

- **React web UI** (`frontend/`) - analyze a resume, browse templates, rewrite, and preview the generated PDF
- **FastAPI web API** (`app.py`) - upload resume PDFs, register/login users, and get analysis or rewritten resumes over HTTP; also serves the built frontend from `frontend/dist`
- **Local CLI** (`extras/main.py`) - pick a resume via a file dialog and run the same LangGraph workflow locally
- **Local workflow** (`extras/local_workflow.py`) - single-file LangGraph harness for experimenting with nodes, routing, and state in isolation

> Formerly-root-level scripts and dead modules were relocated to `extras/` during
> a cleanup. See [`extras/README.md`](extras/README.md). The `app.py` import chain
> is unaffected.

## Features

- **PDF Text Extraction** - Extract clean text from resume PDFs using `pypdf`
- **Comprehensive Analysis** - Evaluates across 5 dimensions: ATS compatibility, JD alignment, technical strength, engineering impact, clarity/credibility
- **ATS Scoring** - Weighted score (0-100) with detailed breakdown
- **Structured Feedback** - High/Medium/Low priority issues with Problem/Why/Fix format
- **Job Description Matching** - `analysis_match_score` + dedicated resume-vs-JD feedback
- **11 Resume Templates** - Pick from `template_1` .. `template_11` when rewriting, with preview images
- **Locked LaTeX Format** - Predefined preamble, macros, header per template; only the body is rewritten; `assemble()` re-attaches the real locked top
- **PDF Compilation & Storage** - Rewritten LaTeX is compiled to PDF via `pdflatex`; the bytes are persisted in PostgreSQL (`generated_resumes.pdf_data`) and served via `GET /generated-resumes/{id}/pdf`
- **User Auth** - Register / login with hashed passwords (argon2 via pwdlib) + JWT access/refresh tokens
- **Database Persistence** - SQLAlchemy engine over 16 tables (users, resumes, analyses, feedback items, generated resumes, auth sessions, ...)

## Architecture

```
   ┌────────────────────────────┐        ┌──────────────────────────────────────────┐
   │  React UI (frontend/)      │        │        FastAPI (app.py)                  │
   │  pages → hooks → api       │ ─────▶ │  /add/user  /login/user  /my/profile    │
   │  axios + Bearer token      │  HTTP  │  /analyze_resume  /rewrite_resume       │
   └────────────────────────────┘        │  /templates  /generated-resumes/{id}/pdf │
                                         │  + StaticFiles(frontend/dist) at "/"     │
                                         └───────────┬─────────────────────────────┘
                                                     │
                                         ┌───────────▼─────────┐       ┌───────────▼─────────────┐
                                         │ api/routes          │       │ api/controllers           │
                                         │   (HTTP → handlers) │       │   (business logic)        │
                                         └───────────┬─────────┘       └───────────┬─────────────┘
                                                     │                             │
                                            ┌────────────────────┼───────────────────┐
                                            ▼                    ▼                   ▼
                                       graphs/workflow   database/operations   utils/ (jwt)
                                       (LangGraph)       (repositories)          ├ pdf_read
                                            └──► agents/ (analyzer + rewrite)    ├ latex_compiler
                                                    └──► llms/ (gemini)          └ mapping
                                            └────────────────────────────────────────────────────┘
```

### Generated PDF storage

The rewrite flow keeps the **PDF bytes** in the database so they survive restarts
and ephemeral hosts; the page-1 thumbnail goes to Cloudinary:

```
rewrite → pdflatex (temp dir) ─┬─▶ generated_resumes.pdf_data   (PostgreSQL BYTEA)
                               └─▶ page-1 PNG → Cloudinary       (preview_img_url)

GET /generated-resumes/{id}/pdf  →  Response(bytes)  ·  owner-checked, 404 if none
```

Intermediates (`.tex` / `.pdf` / `.png`) live in the OS temp directory — not the
working directory — so nothing on local disk has to outlive a single request.

### LangGraph Workflow

Production workflow (`graphs/resume_workflow.py`):

```
START → "analyze" (Analyzer Agent)
         │
         │  scope == 1 ──────────► END (analysis only)
         ▼
      "rewrite" (Rewrite Agent, templates 1-11)
         │
         ▼
      END  (outputs: ats_score, latex_code)
```

Experimentation workflow (`extras/local_workflow.py`) mirrors the same chain in a single file for easy local testing.

## Tech Stack

**Backend**

- Python 3.10+
- FastAPI / Uvicorn (REST API)
- LangGraph + LangChain (agent orchestration)
- Google Gemini (primary LLM), Mistral / NVIDIA (alternatives)
- Pydantic v2 (schemas + structured LLM output)
- SQLAlchemy + SQLAlchemy `text()` (database)
- PyJWT + pwdlib (auth & password hashing)
- pypdf (PDF text extraction), pdflatex / PDFLaTeX (PDF compilation)

**Frontend**

- React 19 + TypeScript + Vite
- Tailwind CSS v4 (CSS-first `@theme` tokens, no `tailwind.config.js`)
- TanStack Query (server state), React Router v7, Axios
- Editorial "report" aesthetic: serif headings, mono for scores, hairline borders, no shadows/gradients

## Prerequisites

- **Python 3.10+**
- **Node.js 20+** (to build the frontend)
- **API Keys** (set in `.env`):
  - `GOOGLE_API_KEY` - Google Gemini (required)
  - `MISTRAL_API_KEY` - Mistral (optional, alternative LLM)
  - `NVIDIA_API_KEY` - NVIDIA (optional, alternative LLM)
- **Auth / Database** (required for the API):
  - `JWT_SECRET_KEY` - secret used to sign access/refresh tokens
  - `DATABASE_URL` - SQLAlchemy connection string (e.g. `sqlite:///resume_agent.db` or a PostgreSQL URL)
- **pdflatex binary** (for PDF compilation) - e.g. MiKTeX or TeX Live on `PATH`

## Installation

```bash
cd project
pip install -r requirements.txt

cd frontend
npm install
```

Create the tables once against a fresh database:

```bash
python -c "from database.migrations.create_tables import create_all_tables; create_all_tables()"
```

`create_all_tables()` also runs an idempotent `ALTER TABLE` for the compiled-PDF
column, so run it once against **existing** databases too (it is safe to repeat):

```sql
ALTER TABLE generated_resumes
ADD COLUMN IF NOT EXISTS pdf_data BYTEA;
```

Verify `pdflatex` is available if you plan to compile PDFs:

```bash
pdflatex --version
```

## Configuration

1. Copy the example file (`.env` itself is git-ignored):

```bash
cd project
cp .env.example .env
```

2. Fill in your values:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
MISTRAL_API_KEY=your_mistral_api_key_here
NVIDIA_API_KEY=your_nvidia_api_key_here

# Required for the API:
JWT_SECRET_KEY=your_jwt_secret_here
DATABASE_URL=sqlite:///resume_agent.db
```

> **Security**: Never commit `.env` to version control - it's in `.gitignore`. Use a strong, random `JWT_SECRET_KEY` in production.

All configuration is centralized in `config/settings.py` (Pydantic Settings v2). It reads `.env` automatically and exposes typed values (`settings.GOOGLE_API_KEY`, `settings.DATABASE_URL`, `settings.JWT_SECRET_KEY`, etc.) used by the DB engine, JWT utils, auth controllers, and LLM providers — replacing the old scattered `load_dotenv()` / `os.getenv()` calls.

## Usage

### 1. Run the web API (serves the built frontend)

```bash
# From the backend, with frontend/dist already built (see step 2)
uvicorn app:app --reload
```

Then open `http://127.0.0.1:8000`. The FastAPI docs are at `/docs`.

> ⚠️ **`app.py` mounts `frontend/dist` at `/`.** The browser is served the
> **production build**, not the Vite dev server. `npm run dev` on port 5173 is a
> *separate* origin that talks to the same API via `VITE_API_BASE_URL`.
>
> This matters: after changing frontend code you must `npm run build`, or the
> page you're testing in the browser is the previous bundle. Likewise, the API
> must be running with `--reload` for backend edits to take effect.

Database tables are created by `database/migrations/create_tables.py`
(`create_all_tables()`), which fans out to the 16 table functions in
`database/migrations/schema_tables/schema_tables.py`. Run it once against a
fresh database before first use.

### 2. Build or develop the frontend

```bash
cd project/frontend
npm install
cp .env.example .env        # set VITE_API_BASE_URL to your FastAPI server
npm run build               # output goes to frontend/dist (served by app.py)
```

For iterative work, run the dev server instead:

```bash
npm run dev                 # http://localhost:5173, proxies to VITE_API_BASE_URL
```

| Script | Does |
|--------|------|
| `npm run dev` | Vite dev server with HMR |
| `npm run build` | `tsc -b && vite build` — type-checks, then bundles to `dist/` |
| `npm run lint` | `eslint .` |
| `npm run preview` | Serves the built `dist/` locally |

> There is no standalone `typecheck` script and no test runner; type checking
> runs as the first half of `npm run build`.

### Frontend architecture

```
src/
├── api/          # the only place URLs and request shapes are defined
│   ├── auth.ts        register / login / profile
│   └── resume.ts      analyze / rewrite / getGeneratedResumePdf / templates / history
├── hooks/        # all React Query hooks (useResume.ts) — components never call api/ directly
├── lib/          # axios instance + error helper, QueryClient
├── context/      # Auth (tokens, current user) and Theme (light/dark, persisted)
├── components/   # ui/ primitives + layout/ + AnalysisReport
├── pages/        # Dashboard (analyze), Templates (rewrite), History, Login, Register
└── types/        # hand-written mirrors of the API response shapes
```

The layering is strict: **pages → hooks → api**. `src/types/index.ts` must stay
in sync with the response shapes documented above — it is the only guard against
a contract drift like the one that produced
`GET /generated-resumes/undefined/pdf`.

Auth tokens live in `localStorage` (`access_token`, `refresh_token`) and are
attached by the axios request interceptor; a 401 clears them automatically.

### 3. Run the local CLI

```bash
python extras/main.py
```

A file dialog opens - select a resume PDF, and the LangGraph workflow runs locally: extract text → analyze → print ATS score, feedback, suggestions, and job-vs-resume analysis.

### 4. Run the local experimentation workflow

```bash
# Dry-run: print the compiled graph structure + state fields (no LLM calls)
python extras/local_workflow.py --dry-run

# Analyze a resume (scope=1, stops after analysis)
python extras/local_workflow.py path\to\resume.pdf

# Analyze + rewrite with a template (scope=2)
python extras/local_workflow.py path\to\resume.pdf --rewrite 3 --jd "Backend AI engineer role..."
```

`extras/local_workflow.py` is a single-file copy of the LangGraph pipeline (state → nodes → conditional routing → compiled workflow → local invocation). It reuses the real `ResumeAgent`, template maps, and guidelines, so it behaves like production — but you can safely tweak nodes/routing to prototype changes without touching `graphs/`. Both scripts prepend the project root to `sys.path`, so run them from the `project/` directory.

### 5. Run the template tests

```bash
python -m pytest tests/ -q
```

Requires `pdflatex` and `pypdf` on PATH (they are test-time only, not runtime
dependencies). The suite compiles all 11 templates on a **single** `pdflatex`
pass — matching `utils/latex_compiler.py` — and asserts:

- every template renders, and every one exposes `assemble(..., info=...)`;
- injected identity reaches the PDF, and the template author's own name never does;
- missing identity renders visible placeholders;
- a long resume paginates with text on *every* page (the blank-page-1 regression);
- templates 2-5 repeat their sidebar furniture on every page;
- `utils/candidate_info.py` lifts identity out of extracted resume text.

Tests that need `pdflatex` skip themselves when it is not installed.

## API Reference

All resume endpoints require a Bearer token obtained via login.

### Auth

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/add/user` | - | Register `{name, email, password}`; password hashed with argon2 |
| `POST` | `/login/user` | - | Login `{email, password}` → `{access_token, refresh_token}` |
| `GET` | `/my/profile` | Bearer | Returns `{ "user_id": <int> }` — **nothing else**, no name or email |

### Resume

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/analyze_resume` | Bearer | Multipart: `file` (PDF) + `job_description` (form) → analysis |
| `POST` | `/rewrite_resume` | Bearer | Multipart: `file`, `job_description`, `template_id` → analysis + compiled PDF |
| `GET` | `/generated-resumes/{resume_id}/pdf` | Bearer | Serves the compiled PDF bytes from `generated_resumes.pdf_data` (owner-checked) |
| `GET` | `/templates` | - | `[{template_id, preview_img, name}]` for the rewrite picker |

> The form field is **`template_id`**, not `resume_format`. `resume_format` is the
> name of the same value *inside* the LangGraph state (`agentState`), and the
> controller renames it at the HTTP boundary.

Both resume endpoints:

1. Save the upload to a temp file and extract text via `pypdf`
2. Store the resume row (`database/operations/upload_resume.py`) → `resume_id`
3. Run the LangGraph workflow via `api/controllers/resume.py`
4. Persist the analysis (`database/operations/resume_analysis.py`)
5. Rewrite additionally saves the generated LaTeX and the compiled PDF bytes (`database/operations/generate_resume.py`) — compiling to a temp dir first, then persisting the bytes in `generated_resumes.pdf_data`

> If `job_description` is empty, the route substitutes a default prompt to tailor the resume to the job market.

### Response shapes

`/analyze_resume` and `/rewrite_resume` share a response body; rewrite adds one field.

```jsonc
{
  "resume_id": 12,                    // the uploaded resume; also the PDF path segment
  "ats_score": 88,
  "feedback": "...",
  "suggestions": "...",
  "job_vs_resume_analysis": "...",    // a STRING of prose — NOT an object
  "analysis_match_score": 69,         // top-level sibling, NOT nested
  "pdf_url": "/generated-resumes/12/pdf"   // rewrite only
}
```

> ⚠️ **`job_vs_resume_analysis` is a string, and `analysis_match_score` is a
> top-level field.** The analyzer's structured output nests both
> (`{analysis_match_score, job_analysis_feed_back}` in
> `models/structured_outputs.py`), but `graphs/nodes.py` flattens that model
> before it reaches HTTP. Consumers that treat the analysis as an object get
> `undefined` for both the score and the feedback text.

`/rewrite_resume` also returns `pdf_url`, the server's own pointer to the
compiled file. Prefer it over rebuilding the path from `resume_id` — if
`resume_id` is ever renamed or omitted, a frontend that reconstructs the URL
silently requests `/generated-resumes/undefined/pdf` and gets a 422.

### Known gap

`GET /resumes` (resume history for the dashboard) is **not implemented** — the
History page surfaces this as an explicit "not available yet" state rather than
an empty list.

### Auth flow

```
Register  →  POST /add/user
Login     →  POST /login/user           → access_token + refresh_token
Use API   →  Authorization: Bearer <access_token>   (sub = user_id, type = "access")
```

Tokens are signed with HS256 using `JWT_SECRET_KEY`. Access tokens last 300 minutes, refresh tokens 7 days (`utils/jwt.py`).

## Project Structure

```
project/
├── app.py                     # FastAPI app (routes + StaticFiles(frontend/dist) at "/")
├── requirements.txt
├── .env                       # Secrets (git-ignored)
├── .env.example               # Key template (tracked)
├── .gitignore
├── README.md
├── docs/
│   └── architecture.md        # In-depth architecture reference
├── extras/                    # Relocated scripts + dead code (NOT imported by app.py)
│   ├── README.md
│   ├── main.py                # Local CLI entry point (file-dialog flow)
│   ├── local_workflow.py      # Single-file LangGraph experimentation workflow
│   ├── clean_up.py            # Deletes caches / build artifacts
│   ├── data/format.py         # Legacy locked LaTeX format (dead)
│   ├── data/resume_templates/seed_templates.py   # Seeds resume_templates table
│   ├── database/operations/candidate_profile.py  # Empty stub (dead)
│   ├── database/migrations/schema_tables/v2/     # Commented-out future schema (dead)
│   ├── models/schemas/auth.py                    # Unused Pydantic auth schemas (dead)
│   └── llms/mistral.py  llms/nvidia.py           # Alternate LLM configs (unused)
├── config/
│   ├── __init__.py
│   └── settings.py            # Centralized Pydantic Settings (reads .env)
├── agents/
│   ├── analyzer_agent.py          # Analyzer model w/ structured output (Gemini)
│   └── resume_rewrite_agent.py    # Rewriter model w/ structured output (Gemini)
├── api/
│   ├── __init__.py
│   ├── controllers/
│   │   ├── auth.py                # register / login / get_current_user (JWT)
│   │   └── resume.py              # analyze_resume / rewrite_resume (workflow calls)
│   └── routes/
│       ├── auth.py                # POST /add/user, /login/user, GET /my/profile
│       └── resume.py              # POST /analyze_resume, /rewrite_resume,
│                                 # GET /templates, GET /generated-resumes/{id}/pdf
├── data/
│   ├── __init__.py
│   ├── guidelines.py              # Strict analysis / ATS optimization guidelines
│   └── resume_templates/          # 11 selectable LaTeX template modules
│       ├── _common.py             # Shared escaping / header rendering
│       └── template_1.py .. template_11.py
├── database/
│   ├── __init__.py
│   ├── db.py                      # SQLAlchemy engine (DATABASE_URL) + text()
│   ├── migrations/
│   │   ├── create_tables.py       # create_all_tables() + pdf_data ALTER - run once per DB
│   │   └── schema_tables/
│   │       └── schema_tables.py   # DDL for all 16 tables + pdf_data ALTER
│   └── operations/                # repositories (CRUD)
│       ├── auth.py                # create_user / login_user
│       ├── auth_sessions.py       # refresh-token session persistence
│       ├── upload_resume.py       # insert resume row (RETURNING resume_id)
│       ├── resume_analysis.py     # insert analysis + scores + feedback items
│       ├── generate_resume.py     # insert generated_resumes row (+ pdf bytes) / read PDF
│       ├── llm_models.py          # llm_models lookup
│       └── resume_templates.py    # get_templates() for the frontend picker
├── frontend/                     # React 19 + TypeScript + Vite + Tailwind v4 SPA
│   ├── src/api/ hooks/ lib/ context/ components/ pages/ types/
│   ├── dist/                      # built bundle served by app.py
│   ├── FRONTEND_NOTES.md          # frontend integration notes
│   ├── vite.config.ts  eslint.config.js
│   └── package.json
├── graphs/
│   ├── agent_states.py            # TypedDict workflow state
│   ├── nodes.py                   # analyze / rewrite / conditional nodes
│   └── resume_workflow.py         # LangGraph StateGraph compilation
├── llms/
│   └── gemini.py                  # Gemini LLM configuration
├── models/
│   ├── classes.py                 # BaseLLM registration wrapper
│   └── structured_outputs.py      # LLM output models (analyzer / rewrite / JD match)
├── utils/
│   ├── jwt.py                     # create_access_token / create_refresh_token
│   ├── token_hash.py              # refresh-token hashing
│   ├── latex_compiler.py          # LaTeX → PDF via pdflatex
│   ├── pdf_preview.py             # PDF → PNG preview via PyMuPDF
│   ├── cloudinary_upload.py       # preview upload
│   ├── candidate_info.py          # identity extraction from resume text
│   ├── mapping.py                 # template index → format/assemble/rules
│   └── pdf_read.py                # PDF text extraction
├── tests/                         # Template compilation + identity tests
└── output/
    └── resumes/                   # legacy local scratch (intermediates now use the OS temp dir)
```

## How It Works

### LangGraph Workflow (`graphs/`)

```python
StateGraph(agentState)
  → START → "analyze" (Analyzer Agent)
  → Conditional Edge (scope):
      scope == 1  → END
      scope != 1  → "rewrite" (Rewrite Agent) → END
```

The `agentState` carries: `data`, `guidelines`, `job_description`, `scope`, `resume_format`, `ats_score`, `feedback`, `suggestions`, `job_vs_resume_analysis`, `analysis_match_score`, `latex_code`.

- `api/controllers/resume.py` invokes the workflow with `scope=1` for analysis-only, or `scope=2` + `resume_format` for the full rewrite path.
- The rewrite node picks `format` / `format_rules` / `assemble()` via `utils/mapping.py`, then returns the assembled `latex_code` and the higher of the two ATS scores.
- `extras/local_workflow.py` reuses the same `agentState`, `ResumeAgent`, and template maps to build an identical graph in one file — edit its nodes/routing to experiment locally without touching the production `graphs/`.

### Agents & Structured Outputs (`agents/`, `models/structured_outputs.py`)

Both agents use `gemini_llm.with_structured_output(...)`:

```python
class job_vs_resume_analysis_class(BaseModel):
    analysis_match_score: int (1-100)   # 69 if no JD provided
    job_analysis_feed_back: str         # "no job description provided" if none

class analyzer_output(BaseModel):
    ats_score: int (1-100)
    feedback: str
    suggestions: str
    job_vs_resume_analysis: job_vs_resume_analysis_class

class rewrite_output(BaseModel):
    ats_score: int (1-100)
    latex_code: str
```

> The LLM output nests the JD match as an object, but `graphs/nodes.py` **flattens
> it before it leaves the graph**:
>
> ```python
> "job_vs_resume_analysis": response.job_vs_resume_analysis.job_analysis_feed_back,  # str
> "analysis_match_score": response.job_vs_resume_analysis.analysis_match_score        # int
> ```
>
> So the HTTP payload has a string plus a sibling integer — never the nested
> object. See the [Response shapes](#response-shapes) table.

### Templates (`data/resume_templates/`, `utils/mapping.py`)

Each `template_N.py` exposes `format`, `format_rules`, and `assemble()`:

- **`format`** - `LOCKED_TOP` + `BODY_MARK` + `BODY`: the skeleton sent to the model.
- **`LOCKED_TOP`** - preamble, macros, and a *placeholder* header. The model must never change it.
- **`BODY_MARK` + `BODY`** - the only part the model rewrites.
- **`format_rules`** - strict rules for valid LaTeX output.
- **`assemble(model_output, info=None)`** - discards whatever the model did to the top and re-attaches the real header, rendered from `info`.

**Identity is supplied per call, not baked into the template.** A template renders a
different header for every candidate, so the 11 templates are safe to share across
users. `graphs/nodes.py` and `extras/local_workflow.py` call
`extract_candidate_info(state["data"])` on the uploaded resume's extracted text and
pass the result as `info`. Missing fields fall back to obvious placeholders
(`[CANDIDATE NAME]`, …) rather than leaking the template author's details.

Escaping, placeholder tokens, and header rendering live once in
`data/resume_templates/_common.py`, so all 11 templates stay in sync.

`utils/mapping.py` dynamically imports all 11 templates into `template_map`,
`assemble_map`, and `format_rules_map` keyed by `1-11`.

#### Pagination and the sidebar templates

Templates 2, 3, 4, and 5 use a two-column sidebar. This used to be a `tabular`,
which cannot break across pages: once the body outgrew one page, TeX pushed the
entire box to page 2 and left page 1 blank.

The sidebar is now page furniture drawn with `eso-pic`:

- `\AddToShipoutPictureBG` paints the band (or hairline) on **every** page;
- `\AddToShipoutPictureFG*` paints the name and contact block on page 1 only;
- the body returns to normal flow with a widened left margin.

`\AtPageLowerLeft` / `\AtPageUpperLeft` position against absolute page
coordinates, so this is correct on the **first** `pdflatex` pass — which matters,
because `utils/latex_compiler.py` compiles exactly once. A TikZ `remember
picture` / `current page` anchor would need a second pass and would render blank
the first time.

Templates 1 and 6-11 have no sidebar and paginate normally.

### Database (`database/`)

`create_all_tables()` (`database/migrations/create_tables.py`) fans out to 16 DDL
functions in `database/migrations/schema_tables/schema_tables.py`, then runs the
idempotent `alter_generated_resumes_add_pdf_data()` (`ALTER TABLE ... ADD COLUMN
IF NOT EXISTS pdf_data BYTEA`):

- `users`, `auth_sessions` - accounts and refresh-token sessions
- `resume`, `candidate_profiles`, `job_descriptions` - uploaded source material
- `resume_templates`, `llm_models` - reference data for the UI picker and LLM bookkeeping
- `resume_analysis`, `resume_analysis_scores`, `analysis_feedback_items` - per-run scores and structured feedback
- `analysis_runs`, `workflow_steps`, `llm_requests` - per-run tracing
- `prompt_versions`, `resume_version`, `generated_resumes` - versioning and rewrite output (LaTeX, Cloudinary preview URL, compiled PDF bytes in `pdf_data`)

Repository functions live in `database/operations/` and are used by the API controllers.

## Customization

### Centralized Configuration
Edit `config/settings.py` to add/rename config values. All modules access them as `settings.<FIELD>`; API keys are also mirrored into the process environment so LangChain providers (chat models) pick them up like before.

### Modify Analysis Guidelines
Edit `data/guidelines.py` - 30 sections covering ATS, keywords, experience, projects, AI/ML, leadership, etc.

### Modify LaTeX Templates
Edit `data/resume_templates/template_N.py`:
- **Identity**: nothing to edit — identity arrives per call via `assemble(..., info=...)`
- **Header**: change `_header_tokens()` in the template, or `render_header()` in `_common.py` to change all of them at once
- **Sections**: Modify `BODY` sections; **Rules**: update `format_rules`

### Add a Template
1. Create `data/resume_templates/template_12.py` (copy an existing one)
2. Seed a row in `resume_templates` (see `extras/data/resume_templates/seed_templates.py`) so the frontend picker can list it
3. `utils/mapping.py` auto-discovers every `template_*.py` for the LaTeX side

> `utils/mapping.py` builds `template_map` / `assemble_map` / `format_rules_map` keyed by index, so the LaTeX template index and the `resume_templates.template_id` row must be kept in agreement.

### Switch LLMs
Modify `llms/gemini.py`, `llms/mistral.py`, `llms/nvidia.py`, then update the imports in `agents/` (e.g. uncomment the NVIDIA line in `resume_rewrite_agent.py`).

### Structured Outputs
Modify `models/structured_outputs.py` to change analyzer/rewrite output schema.

> If you change the analyzer's output shape, update **both** `graphs/nodes.py`
> (which flattens it) and `frontend/src/types/index.ts` + the response-shape
> table above. The nested `job_vs_resume_analysis` object is flattened into a
> string plus a sibling `analysis_match_score`; consumers expecting the nested
> object silently read `undefined`.

## Roadmap / Known Issues

- `GET /resumes` (resume history) is not implemented; the History page says so explicitly
- `services/` and `prompts/` are reserved but currently empty (service layer & prompt templates to be added); their empty `__init__.py` files now live in `extras/`
- `extras/main.py` (CLI) is a thin local harness; the API + controllers are the primary interface
- `extras/local_workflow.py` is the sandbox for iterating on nodes/routing; promote stable changes back into `graphs/nodes.py` and `graphs/resume_workflow.py`
- Frontend `npm run lint` reports 2 pre-existing `react-refresh/only-export-components` errors (a `useAuth`/`useTheme` hook exported from the same file as its provider); fix by splitting the hooks into their own modules
- `pdfjs-dist` is still listed in `frontend/package.json` but nothing imports it

## License

ISC License - see the root `package.json` for details.

---

**Built with**: Python, FastAPI, LangGraph, LangChain, Google Gemini, Pydantic, SQLAlchemy, pypdf, pdflatex, PyJWT, pwdlib, React 19, TypeScript, Vite, Tailwind CSS v4, TanStack Query, Axios