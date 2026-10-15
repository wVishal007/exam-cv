import tempfile
from pathlib import Path

import fitz


def generate_pdf_preview(
    pdf_path: str,
    resume_id: int,
) -> str:
    preview_dir = (
        Path(tempfile.gettempdir())
        / "output"
        / "resume-previews"
    )

    preview_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    preview_path = (
        preview_dir
        / f"resume_{resume_id}.png"
    )

    document = fitz.open(pdf_path)

    try:
        if document.page_count == 0:
            raise ValueError(
                "Generated PDF contains no pages."
            )

        page = document[0]

        pixmap = page.get_pixmap(
            matrix=fitz.Matrix(1.5, 1.5),
            alpha=False,
        )

        pixmap.save(str(preview_path))

    finally:
        document.close()

    return str(preview_path)