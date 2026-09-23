from pdflatex import PDFLaTeX
from pathlib import Path
import subprocess
import tempfile
import shutil

def generate_pdf_from_latex(latex_code,source_file_name):
    temp_dir = tempfile.mkdtemp()


    current_dir = Path.cwd()
    output_dir = current_dir / "output" / "resumes"
    output_dir.mkdir(parents=True, exist_ok=True)
    current_dir_destination = output_dir / f"{source_file_name}.pdf"


    if Path(current_dir_destination).exists():
        user_file_name = input(f"{source_file_name}.pdf already exists enter the resume file name : ")
        current_dir_destination = output_dir / f"{user_file_name}.pdf"
        file_name = user_file_name
    else:
        file_name = source_file_name


    print(f"Temporary directory: {temp_dir}")

    tex_file = Path(temp_dir) / f"{file_name}.tex"
    tex_file.write_text(latex_code, encoding="utf-8")

    print(f"TeX file: {tex_file}")
    print(f"TeX file exists: {tex_file.exists()}")

    result = subprocess.run(
        [
            "pdflatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"{file_name}.tex",
        ],
        cwd=temp_dir,
        capture_output=True,
        text=True,
    )

    files = [f"{file_name}.pdf",f"{file_name}.tex"]
    for i in files:
        temp_resume_dir = Path(temp_dir) / i
        current_dir_destination_temp = output_dir / i 
        shutil.move(temp_resume_dir,current_dir_destination_temp)
    print(temp_dir)
    shutil.rmtree(temp_dir)


    print(f"\nPDF path: {current_dir_destination}")
    print(f"PDF exists: {current_dir_destination.exists()}")

    if not current_dir_destination.exists():
        raise RuntimeError(f"pdflatex did not generate {file_name}.pdf")
    return current_dir_destination