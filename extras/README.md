# extras/

Files relocated here during cleanup. **Nothing in this folder is imported by the
running API** (`app.py` and everything it imports). They are kept for reference,
experimentation, and manual operations — not deleted.

Moving them out of the package tree does not break the server. The four runnable
scripts carry a small `sys.path` bootstrap so they still work from here.

## Inventory

### Standalone scripts (runnable)

| File | Was | Run |
|---|---|---|
| `main.py` | `project/main.py` | `python extras/main.py` — CLI: file dialog → analyze (and optional rewrite) |
| `local_workflow.py` | `project/local_workflow.py` | `python extras/local_workflow.py [--dry-run]` — single-file LangGraph + Tk GUI sandbox |
| `clean_up.py` | `project/clean_up.py` | `python extras/clean_up.py` — deletes caches/build artifacts under CWD |
| `data/resume_templates/seed_templates.py` | `project/data/resume_templates/seed_templates.py` | `python extras/data/resume_templates/seed_templates.py` — seeds the `resume_templates` table |

These scripts insert the project root on `sys.path` themselves, so the absolute
imports they rely on (`data.*`, `utils.*`, `graphs.*`) resolve. `seed_templates.py`
was also repointed at the real templates in `project/data/resume_templates/`.

> `local_workflow.py` and `main.py` require `ttkbootstrap` (see the Optional
> section of `../requirements.txt`). `seed_templates.py` requires a reachable
> `DATABASE_URL` (Postgres).

### Dead code (not imported anywhere)

| File | Why it was moved |
|---|---|
| `data/format.py` | Legacy locked-LaTeX template with baked-in identity; superseded by `data/resume_templates/` |
| `database/operations/candidate_profile.py` | Empty stub (`check_candidate_profile` has a blank query) |
| `database/migrations/schema_tables/v2/schema_tables.py` | Fully commented-out future schema; not referenced by `create_tables.py` |
| `models/schemas/auth.py` | `Token` / `TokenData` / `User` / `UserInDB`; the routes define their own request models |
| `llms/mistral.py`, `llms/nvidia.py` | Alternate provider clients; the agents import Gemini (`llms/gemini.py`) only |
| `services/__init__.py`, `prompts/__init__.py` | Reserved-but-empty packages; re-add if/when they get content |

## Notes

- `config/cloudinary.py` was **not** moved: it is currently unused, but it is the
  only place that calls `cloudinary.config(...)`, so it should be wired into
  startup rather than shelved.
- The `tests/` suite stays in the package tree because `tests/conftest.py`
  derives the project root from its own location.
- To restore any file, move it back to the path in the "Was" column.
