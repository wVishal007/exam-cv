# AI Resume Analyzer

An intelligent resume analysis, job-matching, and rewriting system powered by LLMs and LangGraph. Upload a PDF resume, get a detailed ATS score with actionable feedback, a resume-vs-job-description match analysis, and optionally generate an ATS-optimized LaTeX resume in one of six selectable templates.

The project ships two interfaces plus one experimentation workflow:

- **FastAPI web API** (`app.py`) - upload resume PDFs, register/login users, and get analysis or rewritten resumes over HTTP
- **Local CLI** (`main.py`) - pick a resume via a file dialog and run the same LangGraph workflow locally
- **Local workflow** (`local_workflow.py`) - single-file LangGraph harness for experimenting with nodes, routing, and state in isolation

## Features

- **PDF Text Extraction** - Extract clean text from resume PDFs using `pypdf`
- **Comprehensive Analysis** - Evaluates across 5 dimensions: ATS compatibility, JD alignment, technical strength, engineering impact, clarity/credibility
- **ATS Scoring** - Weighted score (0-100) with detailed breakdown
- **Structured Feedback** - High/Medium/Low priority issues with Problem/Why/Fix format
- **Job Description Matching** - `analysis_match_score` + dedicated resume-vs-JD feedback
- **6 Resume Templates** - Pick from `template_1` .. `template_6` when rewriting
- **Locked LaTeX Format** - Predefined preamble, macros, header per template; only the body is rewritten; `assemble()` re-attaches the real locked top
- **PDF Compilation** - Rewritten LaTeX is compiled to PDF via `pdflatex` (CLI flow)
- **User Auth** - Register / login with hashed passwords (argon2 via pwdlib) + JWT access/refresh tokens
- **Database Persistence** - SQLAlchemy engine with tables for users, resumes, analyses, versions, and generated resumes

## Architecture

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                      FastAPI (app.py)                   │
                    │   /add/user  /login/user  /my/profile                  │
                    │   /analyze_resume  /rewrite_resume                     │
                    └───────────┬─────────────────────────────┬───────────────┘
                                │                             │
                    ┌───────────▼─────────┐       ┌───────────▼─────────────┐
                    │ api/routes          │       │ api/controllers           │
                    │   (HTTP → handlers) │       │   (business logic)        │
                    └───────────┬─────────┘       └───────────┬─────────────┘
                                │                             │
                                │        ┌────────────────────┼───────────────────┐
                                │        ▼                    ▼                   ▼
                                │   graphs/workflow   database/operations   utils/ (jwt)
                                │   (LangGraph)       (repositories)          ├ pdf_read
                                │        └──► agents/ (analyzer + rewrite)    ├ latex_compiler
                                │                    └──► llms/ (gemini)      └ mapping
                                └────────────────────────────────────────────────────┘
```

### LangGraph Workflow

Production workflow (`graphs/workflow.py`):

```
START → "analyze" (Analyzer Agent)
         │
         │  scope == 1 ──────────► END (analysis only)
         ▼
      "rewrite" (Rewrite Agent, templates 1-6)
         │
         ▼
      END  (outputs: ats_score, latex_code)
```

Experimentation workflow (`local_workflow.py`) mirrors the same chain in a single file for easy local testing.

## Tech Stack

- Python 3.10+
- FastAPI / Uvicorn (REST API)
- LangGraph + LangChain (agent orchestration)
- Google Gemini (primary LLM), Mistral / NVIDIA (alternatives)
- Pydantic v2 (schemas + structured LLM output)
- SQLAlchemy + SQLAlchemy `text()` (database)
- PyJWT + pwdlib (auth & password hashing)
- pypdf (PDF text extraction), pdflatex / PDFLaTeX (PDF compilation)

## Prerequisites

- **Python 3.10+**
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

### 1. Run the web API

```bash
uvicorn app:app --reload
```

The FastAPI docs are available at `http://127.0.0.1:8000/docs`.

On startup, the lifespan handler calls `start_db()` to create all tables.

### 2. Run the local CLI

```bash
python main.py
```

A file dialog opens - select a resume PDF, and the LangGraph workflow runs locally: extract text → analyze → print ATS score, feedback, suggestions, and job-vs-resume analysis.

### 3. Run the local experimentation workflow

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
| `GET` | `/my/profile` | Bearer | Returns the authenticated `user_id` |

### Resume

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/analyze_resume` | Bearer | Multipart: `file` (PDF) + `job_description` (form) → full analysis |
| `POST` | `/rewrite_resume` | Bearer | Multipart: `file`, `job_description`, `resume_format` (1-6) → analysis + `latex_code` |

Both resume endpoints:

1. Save the upload to a temp file and extract text via `pypdf`
2. Store the resume row (`database/operations/upload_resume.py`) → `resume_id`
3. Run the LangGraph workflow via `api/controllers/resume.py`
4. Persist the analysis (`database/operations/resume_analysis.py`)
5. Rewrite additionally saves the generated LaTeX (`database/operations/generate_resume.py`)

> If `job_description` is empty, the controller substitutes a default prompt to tailor the resume to the job market.

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
├── app.py                     # FastAPI app (lifespan runs start_db(), routes mounted)
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
│       └── resume.py              # POST /analyze_resume, /rewrite_resume
├── data/
│   ├── __init__.py
│   ├── guidelines.py              # Strict analysis / ATS optimization guidelines
│   ├── format.py                  # Original locked LaTeX format + assemble()
│   └── resume_templates/          # 6 selectable LaTeX template modules
│       └── template_1.py .. template_6.py
├── database/
│   ├── __init__.py
│   ├── db.py                      # SQLAlchemy engine (DATABASE_URL)
│   ├── init_db.py                 # start_db() - creates all tables
│   ├── operations/                # repositories (CRUD)
│   │   ├── auth.py                # create_user / login_user
│   │   ├── upload_resume.py       # insert resume row
│   │   ├── resume_analysis.py     # insert resume_analysis row
│   │   └── generate_resume.py     # insert generated_resumes row
│   └── tables/                    # table DDL
│       ├── user_table.py          # users
│       ├── resume_table.py        # resume
│       ├── resume_analysis_table.py
│       ├── resume_version_table.py
│       └── generated_resume_table.py
├── graphs/
│   ├── agent_states.py            # TypedDict workflow state
│   ├── nodes.py                   # analyze / rewrite / conditional nodes
│   └── workflow.py                # LangGraph StateGraph compilation
├── llms/
│   ├── gemini.py                  # Gemini LLM configuration
│   ├── mistral.py                 # Mistral LLM configuration
│   └── nvidia.py                  # NVIDIA LLM configuration
├── models/
│   ├── schemas/
│   │   └── auth.py                # Pydantic API schemas (Token, User, ...)
│   └── structured_outputs.py      # LLM output models (analyzer / rewrite / JD match)
├── operations/                    # Legacy auth skeleton (superseded by api/)
├── prompts/                       # Reserved for prompt templates (currently empty)
├── services/                      # Reserved service layer (currently empty)
├── utils/
│   ├── jwt.py                     # create_access_token / create_refresh_token
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

### Templates (`data/resume_templates/`, `utils/mapping.py`)

Each `template_N.py` exposes `format`, `format_rules`, and `assemble()`:

- **INFO dict** - name, email, phone, location, links (the only thing you edit for identity)
- **LOCKED_TOP** - preamble, macros, header rendered from INFO (never modified)
- **BODY_MARK + BODY** - the only part the model rewrites
- **format_rules** - strict rules for valid, one-page LaTeX output
- **assemble(model_output)** - discards whatever the model did to the top and re-attaches the real LOCKED_TOP

`utils/mapping.py` dynamically imports all 6 templates into `template_map`, `assemble_map`, and `format_rules_map` keyed by `1-6`.

### Database (`database/`)

`start_db()` (`database/init_db.py`) creates the tables via raw SQL (`SQLAlchemy text()`):

- `users` - user_id, name, email, password (hashed)
- `resume` - resume_id, user_id (FK), raw_text, file_name, ...
- `resume_analysis` - analysis_id, resume_id (FK), ats_score, feedback, suggestions
- `resume_version` - version, resume_id (FK), ats_score
- `generated_resumes` - new_resume_id, resume_id (FK), latex_code

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
1. Create `data/resume_templates/template_7.py` (copy an existing one)
2. Bump `n` in `utils/mapping.py` from `6` to `7`

### Switch LLMs
Modify `llms/gemini.py`, `llms/mistral.py`, `llms/nvidia.py`, then update the imports in `agents/` (e.g. uncomment the NVIDIA line in `resume_rewrite_agent.py`).

### Structured Outputs
Modify `models/structured_outputs.py` to change analyzer/rewrite output schema.

## Roadmap / Known Issues

- `services/` and `prompts/` are reserved but currently empty (service layer & prompt templates to be added)
- `main.py` (CLI) is a thin local harness; the API + controllers are the primary interface
- The legacy `operations/` auth skeleton is superseded by `api/controllers/auth.py` and can be removed
- `local_workflow.py` is the sandbox for iterating on nodes/routing; promote stable changes back into `graphs/nodes.py` and `graphs/workflow.py`

## License

ISC License - see the root `package.json` for details.

---

**Built with**: Python, FastAPI, LangGraph, LangChain, Google Gemini, Pydantic, SQLAlchemy, pypdf, pdflatex, PyJWT, pwdlib