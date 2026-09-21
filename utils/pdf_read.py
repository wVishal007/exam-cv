from pathlib import Path

from pypdf import PdfReader


def select_resume_pdf() -> str:
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select your resume",
        filetypes=[
            ("PDF files", "*.pdf"),
            ("All files", "*.*"),
        ],
    )

    root.destroy()

    if not file_path:
        raise SystemExit("No resume selected.")

    return file_path


def extract_resume_text(file_path: str) -> str:
    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    resume_text = "\n\n".join(pages).strip()

    if not resume_text:
        raise ValueError(
            "Could not extract text from this PDF. "
            "It may be a scanned/image-based PDF."
        )

    return resume_text