# AI Resume Analyzer

An intelligent resume analysis and rewriting system powered by LLMs and LangGraph. Extract text from PDF resumes, get detailed ATS scoring with actionable feedback, and optionally generate an ATS-optimized LaTeX resume.

## Features

- **PDF Text Extraction** - Select resume via file dialog, extract clean text using `pypdf`
- **Comprehensive Analysis** - Evaluates across 5 dimensions: ATS compatibility, JD alignment, technical strength, engineering impact, clarity/credibility
- **ATS Scoring** - Weighted score (0-100) with detailed breakdown
- **Structured Feedback** - High/Medium/Low priority issues with Problem/Why/Fix format
- **Keyword Analysis** - Matching, missing, weakly demonstrated keywords
- **FAANG-Level Standards** - Evaluates against senior engineering benchmarks
- **Automated Rewriting** - Generates ATS-friendly LaTeX resume preserving factual accuracy
- **Locked LaTeX Format** - Predefined preamble, macros, header; only body is rewritten

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  PDF Resume │────▶│  Extract     │────▶│  LangGraph      │
│  (User      │     │  Text        │     │  Workflow       │
│   Selects)  │     │  (pypdf)     │     │                 │
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                   │
                    ┌──────────────────────────────┼──────────────────────────────┐
                    ▼                              ▼                              ▼
           ┌─────────────────┐            ┌─────────────────┐            ┌─────────────────┐
           │  Analyzer Agent │            │  Conditional    │            │  Rewrite Agent  │
           │  (Gemini)       │            │  Node           │            │  (Gemini)       │
           │                 │            │  (User Choice)  │            │                 │
           │ • ATS Score     │            │                 │            │ • LaTeX Output  │
           │ • Feedback      │            │ 1 = End         │            │ • ATS Score     │
           │ • Suggestions   │            │ 2 = Rewrite     │            │                 │
           └─────────────────┘            └─────────────────┘            └─────────────────┘
```

## Prerequisites

- **Python 3.10+**
- **API Keys** (set in `.env`):
  - `GOOGLE_API_KEY` - Google Gemini (required)
  - `MISTRAL_API_KEY` - Mistral (optional, for alternative LLMs)
  - `NVIDIA_API_KEY` - NVIDIA (optional, for alternative LLMs)

## Installation

```bash
cd project
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the `project/` directory:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
MISTRAL_API_KEY=your_mistral_api_key_here  # optional
NVIDIA_API_KEY=your_nvidia_api_key_here    # optional
```

> **Security**: Never commit `.env` to version control. It's already in `.gitignore`.

## Usage

```bash
cd project
python main.py
```

1. File dialog opens - select your resume PDF
2. Text is extracted and analyzed
3. **Analyzer** outputs:
   - ATS Score (X/100)
   - Detailed feedback (High/Medium/Low priority)
   - Keyword analysis
   - Experience/Project/Skills feedback
   - FAANG-level improvements
   - Actionable suggestions
4. Choose to **end** or **rewrite** resume
5. If rewrite: **Rewrite Agent** generates optimized LaTeX resume

## Project Structure

```
project/
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── .env                    # API keys (not tracked)
├── .gitignore              # Git ignore rules
├── README.md               # This file
├── agents/
│   ├── __init__.py
│   ├── analyzer_agent.py   # Analyzer model with structured output
│   └── resume_rewrite_agent.py  # Rewriter model with structured output
├── data/
│   ├── __init__.py
│   ├── guidelines.py       # 1000+ line analysis guidelines
│   └── format.py           # Locked LaTeX format + assembly logic
├── graphs/
│   ├── __init__.py
│   ├── agent_states.py     # TypedDict for workflow state
│   ├── nodes.py            # Analyze/Rewrite/Conditional nodes
│   └── workflow.py         # LangGraph StateGraph compilation
├── llms/
│   ├── __init__.py
│   ├── gemini.py           # Gemini LLM configuration
│   ├── mistral.py          # Mistral LLM configuration
│   └── nvidia.py           # NVIDIA LLM configuration
├── models/
│   ├── __init__.py
│   └── structured_outputs.py  # Pydantic models for outputs
├── prompts/
│   └── __init__.py         # Prompt templates (currently empty)
└── utils/
    ├── __init__.py
    └── pdf_read.py         # PDF extraction + file dialog
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

### Analyzer Agent (`agents/analyzer_agent.py`)

Uses `gemini_llm.with_structured_output(analyzer_output)` where:

```python
class analyzer_output(BaseModel):
    ats_score: int (1-100)
    feedback: str
    suggestions: str
```

### Rewrite Agent (`agents/resume_rewrite_agent.py`)

Uses structured output with:

```python
class rewrite_output(BaseModel):
    ats_score: int (1-100)
    latex_code: str
```

### LaTeX Format (`data/format.py`)

- **LOCKED_TOP**: Preamble, macros, header (never modified)
- **BODY**: Template sections (Summary, Skills, Experience, Projects, Education, Achievements, Certifications)
- **format_rules**: 9 strict rules for valid LaTeX output
- **assemble()**: Re-attaches LOCKED_TOP to model's body output

## Sample Output

```
==============================
AI RESUME ANALYZER
select your resume
getting resume-data
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
FINAL RECOMMENDATIONS
1. Quantify top 3 experience bullets
2. Add Kubernetes to Skills if experienced
3. Rewrite Summary to target specific role
...
==============================
analyzation done
```

If rewrite chosen, outputs full LaTeX document ready for compilation.

## Customization

### Modify Analysis Guidelines
Edit `data/guidelines.py` - 30 sections covering ATS, keywords, experience, projects, AI/ML, leadership, etc.

### Modify LaTeX Format
Edit `data/format.py`:
- **Identity**: Change `\fullname`, email, phone, links in LOCKED_TOP
- **Sections**: Modify BODY template sections
- **Macros**: Add/change `\entry`, `\project`, `\skill`, `\bullets`
- **Rules**: Update `format_rules` for new constraints

### Switch LLMs
Modify `llms/gemini.py`, `llms/mistral.py`, `llms/nvidia.py` then update agent imports.

### Structured Outputs
Modify `models/structured_outputs.py` to change analyzer/rewrite output schema.

## License

ISC License - see root `package.json` for details.

---

**Built with**: Python, LangGraph, LangChain, Google Gemini, Pydantic, pypdf