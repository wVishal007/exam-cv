from importlib import import_module
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "data" / "resume_templates"

template_map = {}
assemble_map = {}
format_rules_map = {}

for path in sorted(TEMPLATES_DIR.glob("template_*.py")):
    n = int(path.stem.split("_")[-1])
    module = import_module(f"data.resume_templates.{path.stem}")
    template_map[n] = module.format
    assemble_map[n] = module.assemble
    format_rules_map[n] = module.format_rules