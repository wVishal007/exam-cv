import json
import re
from importlib import import_module
from pathlib import Path

from database.db import text, engine

# This file lives next to template_1.py ... template_11.py
TEMPLATES_DIR = Path(__file__).resolve().parent

template_map = {}
assemble_map = {}
format_rules_map = {}


def _template_number(path: Path) -> int:
    return int(path.stem.split("_")[-1])


def _extract_info(path: Path, module) -> dict:
    """Pull name / version / description / accent color from the template file itself."""
    src = path.read_text(encoding="utf-8")
    lines = src.splitlines()

    # Line 1: "# resume_format_navy_classic.py  (v4 -- standalone, ...)"
    first = lines[0] if lines else ""
    m = re.search(r"resume_format_([A-Za-z0-9_]+)\.py", first)
    slug = m.group(1) if m else path.stem
    name = slug.replace("_", " ").title()  # "Navy Classic"

    v = re.search(r"\(v(\d+)", first)
    version = v.group(1) if v else "1"

    # Line 3: the style description comment
    description = lines[2].lstrip("# ").strip() if len(lines) > 2 else ""

    accent = re.search(
        r"\\definecolor\{accent\}\{HTML\}\{([0-9A-Fa-f]{6})\}", module.format
    )

    return {
        "name": name,
        "version": version,
        "preview_img": getattr(module, "img_preview", None),
        "style_metadata": {
            "slug": slug,
            "description": description,
            "accent_color": f"#{accent.group(1)}" if accent else None,
            "module": f"data.resume_templates.{path.stem}",
        },
    }


def add_template_to_table(template_key, name, version, preview_img, style_metadata):
    query = text("""
        INSERT INTO resume_templates (template_key, name, version, preview_img, style_metadata)
        VALUES (:template_key, :name, :version, :preview_img, CAST(:style_metadata AS JSONB))
        ON CONFLICT (template_key) DO UPDATE SET
            name = EXCLUDED.name,
            version = EXCLUDED.version,
            preview_img = EXCLUDED.preview_img,
            style_metadata = EXCLUDED.style_metadata,
            updated_at = CURRENT_TIMESTAMP
    """)
    with engine.begin() as conn:
        conn.execute(query, {
            "template_key": template_key,
            "name": name,
            "version": version,
            "preview_img": preview_img,
            "style_metadata": json.dumps(style_metadata),
        })


def ensure_template_key_unique():
    # Needed for ON CONFLICT; makes seeding safe to re-run.
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_resume_templates_key "
            "ON resume_templates (template_key)"
        ))


def seed_templates():
    ensure_template_key_unique()

    files = sorted(TEMPLATES_DIR.glob("template_*.py"), key=_template_number)
    print(f"Found {len(files)} template files in {TEMPLATES_DIR}")
    if not files:
        raise SystemExit("No template_*.py files found - check TEMPLATES_DIR")

    for path in files:
        n = _template_number(path)
        module = import_module(f"data.resume_templates.{path.stem}")

        template_map[n] = module.format
        assemble_map[n] = module.assemble
        format_rules_map[n] = module.format_rules

        info = _extract_info(path, module)
        add_template_to_table(
            f"template_{n}",
            info["name"],
            info["version"],
            info["preview_img"],
            info["style_metadata"],
        )
        print(f"seeded template_{n}: {info['name']} (v{info['version']})")


if __name__ == "__main__":
    seed_templates()