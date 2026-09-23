from pathlib import Path
import shutil


ROOT = Path.cwd()

DIRS_TO_DELETE = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".coverage",
    "htmlcov",
    "node_modules",
    ".next",
    ".nuxt",
    "dist",
    "build",
    ".turbo",
    ".cache",
}

FILES_TO_DELETE = {
    ".pyc",
    ".pyo",
    ".log",
}


def clean_project(root: Path):
    deleted_dirs = 0
    deleted_files = 0

    for current_root, dirs, files in os.walk(root):
        current_root = Path(current_root)

        # Don't descend into node_modules/.git etc. unnecessarily
        dirs[:] = [
            d for d in dirs
            if d != ".git"
        ]

        for directory in dirs:
            if directory in DIRS_TO_DELETE:
                path = current_root / directory

                try:
                    shutil.rmtree(path)
                    print(f"Deleted directory: {path}")
                    deleted_dirs += 1
                except Exception as e:
                    print(f"Failed: {path} -> {e}")

        for file in files:
            path = current_root / file

            if path.suffix.lower() in FILES_TO_DELETE:
                try:
                    path.unlink()
                    print(f"Deleted file: {path}")
                    deleted_files += 1
                except Exception as e:
                    print(f"Failed: {path} -> {e}")

    print("\n" + "=" * 50)
    print("CLEANUP COMPLETE")
    print("=" * 50)
    print(f"Directories deleted: {deleted_dirs}")
    print(f"Files deleted:       {deleted_files}")


if __name__ == "__main__":
    import os
    clean_project(ROOT)