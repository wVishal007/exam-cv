# AI Resume Analyzer

An intelligent resume analysis, job-matching, and rewriting system powered by LLMs and LangGraph. Extract text from a PDF resume, get a detailed ATS score with actionable feedback, compare the resume against a pasted job description, and optionally generate an ATS-optimized LaTeX resume in one of six selectable templates — compiled straight to PDF.

## Features

- **PDF Text Extraction** - Select a resume via file dialog, extract clean text using `pypdf`
- **Comprehensive Analysis** - Evaluates across 5 dimensions: ATS compatibility, JD alignment, technical strength, engineering impact, clarity/credibility
- **ATS Scoring** - Weighted score (0-100) with detailed breakdown
- **Structured Feedback** - High/Medium/Low priority issues with Problem/Why/Fix format
- **Job Description Matching** - Paste any JD; get a resume-vs-JD match score and dedicated feedback
- **Keyword Analysis** - Matching, missing, weakly demonstrated keywords
- **FAANG-Level Standards** - Evaluates against senior engineering benchmarks
- **6 Resume Templates** - Pick from `template_1` .. `template_6` when rewriting
- **Locked LaTeX Format** - Predefined preamble, macros, header per template; only the body is rewritten; `assemble()` re-attaches the real locked top
- **PDF Compilation** - Rewritten LaTeX is compiled to PDF via `pdflatex` and saved to `output/resumes/`
- **SQLite Persistence** - Schema for users, resumes, resume versions, and analyses (`resume_agent.db`)

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌────────────────┐
│  PDF Resume │────▶│  Extract     │────▶│  start_db()     │────▶│  LangGraph     │
│  (User      │     │  Text        │     │  (SQLite init)  │     │  Workflow      │
│   Selects)  │     │  (pypdf)     │     │                 │     │                │
└─────────────┘     └──────────────┘     └─────────────────┘     └───────┬────────┘
                                                                          │
                    ┌─────────────────────────────────────────────────────┼──────────────────────┐
                    ▼                                                     ▼                      ▼
           ┌─────────────────┐                                   ┌──────────────────┐  ┌─────────────────┐
           │  Analyzer Agent │                                   │  Conditional     │  │  Rewrite Agent  │
           │  (Gemini)       │                                   │  Node            │  │  (Gemini)       │
           │                 │                                   │                  │  │                 │
           │ • ATS Score     │                                   │ 1 = End          │  │ • Template 1-6  │
           │ • Feedback      │                                   │ 2 = Rewrite      │  │ • ATS Score     │
           │ • Suggestions   │                                   │                  │  │ • LaTeX Output  │
           │ • JD Match Score│                                   │                  │  │                 │
           └─────────────────┘                                   └──────────────────┘  └────────┬────────┘
                                                                                                 ▼
                                                                                        ┌─────────────────┐
                                                                                        │  assemble() +   │
                                                                                        │  pdflatex       │
                                                                                        │  → PDF          │
                                                                                        │  (output/resumes)│
                                                                                        └─────────────────┘
```

## Prerequisites

- **Python 3.10+**
- **API Keys** (set in `.env`):
  - `GOOGLE_API_KEY` - Google Gemini (required)
  - `MISTRAL_API_KEY` - Mistral (optional, for alternative LLMs)
  - `NVIDIA_API_KEY` - NVIDIA (optional, for alternative LLMs)
- **pdflatex binary** (for PDF compilation) - e.g. MiKTeX or TeX Live, available on `PATH`
- **Optional (auth skeleton)**: FastAPI / uvicorn / PyJWT / pwdlib

## Installation

```bash
cd project
pip install -r requirements.txt
```

Make sure `pdflatex` is installed and on your `PATH`:

```bash
# verify
pdflatex --version
```

## Configuration

1. Copy the example file (`.env` itself is git-ignored):

```bash
cd project
cp .env.example .env
```

2. Fill in your API keys:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
MISTRAL_API_KEY=your_mistral_api_key_here
NVIDIA_API_KEY=your_nvidia_api_key_here
```

> **Security**: Never commit `.env` to version control. It's already in `.gitignore`.
> If you use the auth skeleton, change the hardcoded `SECRET_KEY` in `operations/auth/auth.py`.

## Usage

```bash
cd project
python main.py
```

1. File dialog opens - select your resume PDF
2. **Paste a job description** (optional) - type `END` on a new line when finished
3. **Analyzer** outputs:
   - ATS Score (X/100)
   - Detailed feedback (High/Medium/Low priority)
   - Suggestions
   - Job-vs-resume analysis (match score + feedback)
4. Choose to **end** (`1`) or **rewrite** (`2`) the resume
5. If rewrite: choose a **template** (`1`-`6`), and the **Rewrite Agent** generates optimized LaTeX
6. The LaTeX is compiled to PDF and saved to `output/resumes/<source_name>.pdf`

To run the auth skeleton separately:

```bash
uvicorn operations.auth.auth:app --reload
```

## Project Structure

```
project/
├── main.py                     # Entry point: DB init → extract → analyze → rewrite → PDF
├── clean_up.py                 # Deletes caches / build artifacts
├── requirements.txt            # Python dependencies
├── .env                        # API keys (not tracked)
├── .env.example                # Template for .env (tracked)
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
├── agents/
│   ├── __init__.py
│   ├── analyzer_agent.py           # Analyzer model with structured output (Gemini)
│   └── resume_rewrite_agent.py     # Rewriter model with structured output (Gemini)
├── data/
│   ├── __init__.py
│   ├── guidelines.py               # Strict analysis / ATS optimization guidelines
│   ├── format.py                   # Original locked LaTeX format + assemble()
│   └── resume_templates/           # 6 selectable LaTeX template modules
│       ├── template_1.py .. template_6.py
├── database/
│   ├── __init__.py
│   ├── db.py                       # SQLite connection to resume_agent.db
│   ├── init_db.py                  # Creates all tables
│   └── tables/
│       ├── user_table.py           # users
│       ├── resume_table.py         # resume
│       ├── resume_analysis_table.py# resume_analysis
│       └── resume_version_table.py # resume_version
├── graphs/
│   ├── __init__.py
│   ├── agent_states.py             # TypedDict for workflow state
│   ├── nodes.py                    # analyze / rewrite / conditional nodes
│   └── workflow.py                 # LangGraph StateGraph compilation
├── llms/
│   ├── __init__.py
│   ├── gemini.py                   # Gemini LLM configuration
│   ├── mistral.py                  # Mistral LLM configuration
│   └── nvidia.py                   # NVIDIA LLM configuration
├── models/
│   ├── __init__.py
│   └── structured_outputs.py       # Pydantic models for analyzer/rewrite output
├── operations/
│   ├── auth/
│   │   └── auth.py                 # FastAPI + JWT auth skeleton
├── prompts/
│   └── __init__.py                 # Prompt templates (currently empty)
└── utils/
    ├── __init__.py
    ├── pdf_read.py                 # File dialog + PDF text extraction
    ├── latex_compiler.py           # LaTeX → PDF via pdflatex
    └── mapping.py                  # Dynamic template map (template index → format/assemble/rules)
```

## How It Works

### LangGraph Workflow (`graphs/workflow.py`)

```python
StateGraph(agentState)
  → START → "analyze" (Analyzer Agent)
  → Conditional Edge:
      "end"  → END
      "rewrite" → "rewrite" (Rewrite Agent) → END
```

### Analyze Node (`graphs/nodes.py`)

Prompts you to paste a job description (type `END` on a new line to finish), then calls the analyzer with the resume + JD + guidelines.

### Agents & Models (`agents/`, `models/structured_outputs.py`)

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

`utils/mapping.py` dynamically imports all 6 templates and builds `template_map`, `assemble_map`, `format_rules_map` keyed by 1-6. The rewrite node asks which template to use, then runs `assemble_map[i](response.latex_code)`.

### PDF Compilation (`utils/latex_compiler.py`)

`generate_pdf_from_latex(latex_code, source_file_name)` writes the LaTeX to a temp dir, runs `pdflatex -interaction=nonstopmode -halt-on-error`, then moves the `.pdf` and `.tex` into `output/resumes/`. If the source name already exists, it prompts for a new file name.

### Database (`database/`)

`main.py` calls `start_db()` on launch, which creates four tables in `resume_agent.db`:

- `users` (user_id, name, email, password)
- `resume` (resume_id, user_id, raw_text, latex_code, file_name, created_at)
- `resume_analysis` (analysis_id, resume_id, ats_score, feedback, suggestions, created_at)
- `resume_version` (version, resume_id, ats_score, created_at)

## Sample Output

```
==============================
AI RESUME ANALYZER
select your resume
getting resume-data
db started
Enter job description.
Paste the complete job description.
When finished, type END on a new line.
> ... (paste) ...
> END
==============================
78
------------------------------
OVERALL ASSESSMENT
...
ATS SCORE
Score: 78/100
...
HIGH PRIORITY ISSUES
Problem: Missing metrics in experience bullets
Why: ATS and recruiters need quantified impact
Fix: Add users, latency, throughput, cost savings where verifiable
...
KEYWORD ANALYSIS
MATCHING KEYWORDS: Python, FastAPI, PostgreSQL, Docker
MISSING KEYWORDS: Kubernetes, CI/CD, GraphQL
...
==============================
Job-vs-resume analysis
MATCH SCORE: 85/100
...job analysis feedback...
------------------------------
enter your choice [1] analyze or rewrite [2] : 2
enter the format you want to use out of 1,2,3,4,5,6 : 3
...
PDF generated: output/resumes/my_resume.pdf
------------------------------
resume rewrite done
```

## Customization

### Modify Analysis Guidelines
Edit `data/guidelines.py` - 30 sections covering ATS, keywords, experience, projects, AI/ML, leadership, etc.

### Modify LaTeX Templates
Edit `data/resume_templates/template_N.py`:
- **Identity**: Change the `INFO` dict (fullname, email, phone, location, links)
- **Sections**: Modify `BODY` template sections
- **Macros**: Add/change `\entry`, `\project`, `\skill`, `\bullets`
- **Rules**: Update `format_rules` for new constraints

### Add a Template
1. Create `data/resume_templates/template_7.py` (copy an existing one)
2. Bump `n` in `utils/mapping.py` from `6` to `7`

### Switch LLMs
Modify `llms/gemini.py`, `llms/mistral.py`, `llms/nvidia.py`, then update the agent imports in `agents/`.

### Structured Outputs
Modify `models/structured_outputs.py` to change analyzer/rewrite output schema.

### Auth Skeleton
`operations/auth/auth.py` is a FastAPI JWT example (OAuth2-Password-Bearer with `/token` and `/users/me/`). Replace the hardcoded `SECRET_KEY` and `fake_users_db` before any real use.

## License

ISC License - see root `package.json` for details.

---

**Built with**: Python, LangGraph, LangChain, Google Gemini, Pydantic, pypdf, pdflatex, FastAPI, SQLite