from pathlib import Path
import subprocess
import tempfile
import shutil


def generate_pdf_from_latex(
    latex_code: str,
    source_file_name: str,
    resume_id: int
):
    temp_dir = Path(tempfile.mkdtemp())

    output_dir = Path(tempfile.gettempdir()) / "output" / "resumes"
    output_dir.mkdir(parents=True, exist_ok=True)

    # output_dir = Path("/tmp/output/resumes")
    # output_dir.mkdir(parents=True, exist_ok=True)

    file_name = Path(source_file_name).stem
    tex_file = temp_dir / f"{file_name}.tex"
    pdf_file = temp_dir / f"{file_name}.pdf"

    try:
        tex_file.write_text(latex_code, encoding="utf-8")

        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                tex_file.name,
            ],
            cwd=temp_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0 or not pdf_file.exists():
            raise RuntimeError(
                f"LaTeX compilation failed:\n{result.stdout}\n{result.stderr}"
            )
        destination_pdf = output_dir / f"resume_{resume_id}.pdf"
        destination_tex = output_dir / f"resume_{resume_id}.tex"

        shutil.copy2(pdf_file, destination_pdf)
        shutil.copy2(tex_file, destination_tex)

        return destination_pdf

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)