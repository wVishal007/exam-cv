# AI Resume Analyzer

An intelligent resume analysis, job-matching, and rewriting system powered by LLMs and LangGraph. Upload a PDF resume, get a detailed ATS score with actionable feedback, a resume-vs-job-description match analysis, and optionally generate an ATS-optimized LaTeX resume in one of eleven selectable templates.

The project ships three interfaces plus one experimentation workflow:

- **React web UI** (`frontend/`) - analyze a resume, browse templates, rewrite, and preview the generated PDF
- **FastAPI web API** (`app.py`) - upload resume PDFs, register/login users, and get analysis or rewritten resumes over HTTP; also serves the built frontend from `frontend/dist`
- **Local CLI** (`main.py`) - pick a resume via a file dialog and run the same LangGraph workflow locally
- **Local workflow** (`local_workflow.py`) - single-file LangGraph harness for experimenting with nodes, routing, and state in isolation

## Features

- **PDF Text Extraction** - Extract clean text from resume PDFs using `pypdf`
- **Comprehensive Analysis** - Evaluates across 5 dimensions: ATS compatibility, JD alignment, technical strength, engineering impact, clarity/credibility
- **ATS Scoring** - Weighted score (0-100) with detailed breakdown
- **Structured Feedback** - High/Medium/Low priority issues with Problem/Why/Fix format
- **Job Description Matching** - `analysis_match_score` + dedicated resume-vs-JD feedback
- **11 Resume Templates** - Pick from `template_1` .. `template_11` when rewriting, with preview images
- **Locked LaTeX Format** - Predefined preamble, macros, header per template; only the body is rewritten; `assemble()` re-attaches the real locked top
- **PDF Compilation** - Rewritten LaTeX is compiled to PDF via `pdflatex`, served back via `GET /generated-resumes/{id}/pdf`
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

### LangGraph Workflow

Production workflow (`graphs/workflow.py`):

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

Experimentation workflow (`local_workflow.py`) mirrors the same chain in a single file for easy local testing.

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
python main.py
```

A file dialog opens - select a resume PDF, and the LangGraph workflow runs locally: extract text → analyze → print ATS score, feedback, suggestions, and job-vs-resume analysis.

### 4. Run the local experimentation workflow

```bash
# Dry-run: print the compiled graph structure + state fields (no LLM calls)
python local_workflow.py --dry-run

# Analyze a resume (scope=1, stops after analysis)
python local_workflow.py path\to\resume.pdf

# Analyze + rewrite with a template (scope=2)
python local_workflow.py path\to\resume.pdf --rewrite 3 --jd "Backend AI engineer role..."
```

`local_workflow.py` is a single-file copy of the LangGraph pipeline (state → nodes → conditional routing → compiled workflow → local invocation). It reuses the real `ResumeAgent`, template maps, and guidelines, so it behaves like production — but you can safely tweak nodes/routing to prototype changes without touching `graphs/`.

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
| `GET` | `/generated-resumes/{resume_id}/pdf` | Bearer | Streams the compiled PDF for that `resume_id` |
| `GET` | `/templates` | - | `[{template_id, preview_img, name}]` for the rewrite picker |

> The form field is **`template_id`**, not `resume_format`. `resume_format` is the
> name of the same value *inside* the LangGraph state (`agentState`), and the
> controller renames it at the HTTP boundary.

Both resume endpoints:

1. Save the upload to a temp file and extract text via `pypdf`
2. Store the resume row (`database/operations/upload_resume.py`) → `resume_id`
3. Run the LangGraph workflow via `api/controllers/resume.py`
4. Persist the analysis (`database/operations/resume_analysis.py`)
5. Rewrite additionally saves the generated LaTeX (`database/operations/generate_resume.py`) and compiles it to `output/resumes/resume_{resume_id}.pdf`

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
├── main.py                    # Local CLI entry point (file-dialog flow)
├── local_workflow.py          # Single-file LangGraph experimentation workflow
├── clean_up.py                # Deletes caches / build artifacts
├── requirements.txt
├── .env                       # Secrets (git-ignored)
├── .env.example               # Key template (tracked)
├── .gitignore
├── README.md
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
│   ├── format.py                  # Original locked LaTeX format + assemble()
│   └── resume_templates/          # 11 selectable LaTeX template modules
│       ├── template_1.py .. template_11.py
│       └── seed_templates.py      # Seeds resume_templates table (ids, names, preview imgs)
├── database/
│   ├── __init__.py
│   ├── db.py                      # SQLAlchemy engine (DATABASE_URL) + text()
│   ├── migrations/
│   │   ├── create_tables.py       # create_all_tables() - run once on a fresh DB
│   │   └── schema_tables/
│   │       └── schema_tables.py   # DDL for all 16 tables
│   └── operations/                # repositories (CRUD)
│       ├── auth.py                # create_user / login_user
│       ├── auth_sessions.py       # refresh-token session persistence
│       ├── upload_resume.py       # insert resume row (RETURNING resume_id)
│       ├── resume_analysis.py     # insert analysis + scores + feedback items
│       ├── generate_resume.py     # insert generated_resumes row
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
│   └── workflow.py                # LangGraph StateGraph compilation
├── llms/
│   ├── gemini.py                  # Gemini LLM configuration
│   ├── mistral.py                 # Mistral LLM configuration
│   └── nvidia.py                  # NVIDIA LLM configuration
├── models/
│   ├── classes.py                 # shared dataclasses / row models
│   ├── schemas/
│   │   └── auth.py                # Pydantic API schemas (Token, User, ...)
│   └── structured_outputs.py      # LLM output models (analyzer / rewrite / JD match)
├── prompts/                       # Reserved for prompt templates (currently empty)
├── services/                      # Reserved service layer (currently empty)
├── utils/
│   ├── jwt.py                     # create_access_token / create_refresh_token
│   ├── token_hash.py              # refresh-token hashing
│   ├── latex_compiler.py          # LaTeX → PDF via pdflatex
│   ├── mapping.py                 # template index → format/assemble/rules
│   └── pdf_read.py                # PDF text extraction (+ file dialog for CLI)
└── output/
    └── resumes/                   # compiled PDFs/TeX (git-ignored)
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
- `local_workflow.py` reuses the same `agentState`, `ResumeAgent`, and template maps to build an identical graph in one file — edit its nodes/routing to experiment locally without touching the production `graphs/`.

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

- **INFO dict** - name, email, phone, location, links (the only thing you edit for identity)
- **LOCKED_TOP** - preamble, macros, header rendered from INFO (never modified)
- **BODY_MARK + BODY** - the only part the model rewrites
- **format_rules** - strict rules for valid, one-page LaTeX output
- **assemble(model_output)** - discards whatever the model did to the top and re-attaches the real LOCKED_TOP

`utils/mapping.py` dynamically imports all 11 templates into `template_map`, `assemble_map`, and `format_rules_map` keyed by `1-11`.

### Database (`database/`)

`create_all_tables()` (`database/migrations/create_tables.py`) fans out to 16 DDL
functions in `database/migrations/schema_tables/schema_tables.py`:

- `users`, `auth_sessions` - accounts and refresh-token sessions
- `resume`, `candidate_profiles`, `job_descriptions` - uploaded source material
- `resume_templates`, `llm_models` - reference data for the UI picker and LLM bookkeeping
- `resume_analysis`, `resume_analysis_scores`, `analysis_feedback_items` - per-run scores and structured feedback
- `analysis_runs`, `workflow_steps`, `llm_requests` - per-run tracing
- `prompt_versions`, `resume_version`, `generated_resumes` - versioning and rewrite output

Repository functions live in `database/operations/` and are used by the API controllers.

## Customization

### Centralized Configuration
Edit `config/settings.py` to add/rename config values. All modules access them as `settings.<FIELD>`; API keys are also mirrored into the process environment so LangChain providers (chat models) pick them up like before.

### Modify Analysis Guidelines
Edit `data/guidelines.py` - 30 sections covering ATS, keywords, experience, projects, AI/ML, leadership, etc.

### Modify LaTeX Templates
Edit `data/resume_templates/template_N.py`:
- **Identity**: Change the `INFO` dict (fullname, email, phone, location, links)
- **Sections**: Modify `BODY` sections; **Rules**: update `format_rules`

### Add a Template
1. Create `data/resume_templates/template_12.py` (copy an existing one)
2. Seed a row in `resume_templates` (see `data/resume_templates/seed_templates.py`) so the frontend picker can list it
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
- `services/` and `prompts/` are reserved but currently empty (service layer & prompt templates to be added)
- `main.py` (CLI) is a thin local harness; the API + controllers are the primary interface
- `local_workflow.py` is the sandbox for iterating on nodes/routing; promote stable changes back into `graphs/nodes.py` and `graphs/workflow.py`
- Frontend `npm run lint` reports 2 pre-existing `react-refresh/only-export-components` errors (a `useAuth`/`useTheme` hook exported from the same file as its provider); fix by splitting the hooks into their own modules
- `pdfjs-dist` is still listed in `frontend/package.json` but nothing imports it

## License

ISC License - see the root `package.json` for details.

---

**Built with**: Python, FastAPI, LangGraph, LangChain, Google Gemini, Pydantic, SQLAlchemy, pypdf, pdflatex, PyJWT, pwdlib, React 19, TypeScript, Vite, Tailwind CSS v4, TanStack Query, Axios