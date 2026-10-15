"""Make the project and the local test helpers importable.

`utils.mapping` and `data.resume_templates.*` need the project root on sys.path;
`fixtures` needs this directory on sys.path.
"""

import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent

for _path in (PROJECT_ROOT, TESTS_DIR):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))