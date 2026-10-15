"""Compile-and-render tests for every resume template.

These are regression guards for two real bugs:

1. `INFO` was baked into `LOCKED_TOP` at import time, so every generated resume
   was stamped with the template author's name.
2. Templates 2/3/4/5 laid out the two-column sidebar with `tabular`, which cannot
   break across pages. Any resume taller than one page pushed the whole
   unbreakable box to page 2, leaving page 1 completely blank.

Compilation is deliberately a SINGLE pdflatex pass, matching production
(`utils/latex_compiler.py`). Anything that needs a second pass to place content
correctly -- e.g. a TikZ `remember picture` page anchor -- will fail here.
"""

import inspect
import re
import shutil
import subprocess
import tempfile
from importlib import import_module
from pathlib import Path

import pytest
from pypdf import PdfReader

from fixtures import (
    INJECTED_INFO,
    LEGACY_BAKED_IN_NAME,
    long_model_output,
    short_model_output,
)
from utils.mapping import assemble_map, template_map

TEMPLATE_IDS = sorted(template_map)

pdflatex = shutil.which("pdflatex")
requires_pdflatex = pytest.mark.skipif(
    pdflatex is None, reason="pdflatex not on PATH"
)

# Compiling 11 templates x several fixtures is slow; cache per run.
_COMPILE_CACHE: dict[tuple, Path] = {}


def _module(tid: int):
    return import_module(f"data.resume_templates.template_{tid}")


def _compile(tex: str, key: tuple) -> Path:
    """Run pdflatex once on `tex` and return the resulting PDF path."""
    if key in _COMPILE_CACHE:
        return _COMPILE_CACHE[key]

    tmp = Path(tempfile.mkdtemp(prefix="texcheck_"))
    try:
        (tmp / "doc.tex").write_text(tex, encoding="utf-8")
        proc = subprocess.run(
            [pdflatex, "-interaction=nonstopmode", "-halt-on-error", "doc.tex"],
            cwd=tmp,
            capture_output=True,
            text=True,
            timeout=180,
        )
        pdf = tmp / "doc.pdf"
        if proc.returncode != 0 or not pdf.exists():
            pytest.fail(
                "pdflatex failed on a single pass:\n"
                f"returncode={proc.returncode}\n"
                f"{proc.stdout[-4000:]}\n{proc.stderr[-2000:]}"
            )
        _COMPILE_CACHE[key] = pdf
        return pdf
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise


def _pages(pdf: Path) -> list[str]:
    """Extracted text per page. A blank page yields '' or whitespace."""
    return [(p.extract_text() or "") for p in PdfReader(str(pdf)).pages]


def _compile_pages(template_id: int, model_output: str, info, tag: str) -> list[str]:
    tex = assemble_map[template_id](model_output, info=info)
    return _pages(_compile(tex, (template_id, tag, repr(info))))


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    for pdf in _COMPILE_CACHE.values():
        shutil.rmtree(pdf.parent, ignore_errors=True)
    _COMPILE_CACHE.clear()


# --------------------------------------------------------------------------
# mapping
# --------------------------------------------------------------------------

def test_mapping_covers_every_template():
    assert TEMPLATE_IDS == list(range(1, 12))


def test_assemble_accepts_per_call_info():
    """`assemble` must take the candidate's info at call time."""
    for tid in TEMPLATE_IDS:
        params = inspect.signature(assemble_map[tid]).parameters
        assert "info" in params, f"template {tid}: assemble() has no info parameter"
        assert params["info"].default is None, (
            f"template {tid}: info must be optional so old single-arg callers work"
        )


# --------------------------------------------------------------------------
# identity
# --------------------------------------------------------------------------

def _flat(pages) -> str:
    """Page text with all whitespace collapsed to single spaces.

    Needed because layout is not text-flow: in a narrow sidebar column a name
    wraps across two lines, so a raw substring check would pass or fail purely
    as a function of how wide the column is.
    """
    return " ".join(" ".join(pages).split())


@requires_pdflatex
@pytest.mark.parametrize("tid", TEMPLATE_IDS)
def test_injected_identity_reaches_the_pdf(tid):
    """The name/email passed to assemble() must appear on the rendered page."""
    pages = _compile_pages(tid, short_model_output(_module(tid)), INJECTED_INFO, "ident")
    text = _flat(pages)
    assert " ".join(INJECTED_INFO["fullname"].split()) in text
    assert INJECTED_INFO["email"] in text


@requires_pdflatex
@pytest.mark.parametrize("tid", TEMPLATE_IDS)
def test_baked_in_identity_never_leaks(tid):
    """The template author's own name must never reach a generated resume."""
    pages = _compile_pages(tid, short_model_output(_module(tid)), INJECTED_INFO, "ident")
    text = _flat(pages)
    assert LEGACY_BAKED_IN_NAME not in text, (
        f"template {tid} still renders the import-time INFO name"
    )


@requires_pdflatex
@pytest.mark.parametrize("tid", TEMPLATE_IDS)
def test_missing_info_renders_a_clear_placeholder(tid):
    """No info supplied -> an obviously-fake placeholder, not someone's real name."""
    pages = _compile_pages(tid, short_model_output(_module(tid)), None, "placeholder")
    text = _flat(pages)
    assert "[CANDIDATE NAME]" in text
    assert LEGACY_BAKED_IN_NAME not in text


def test_candidate_info_extraction():
    """utils.candidate_info should lift identity out of extracted PDF text."""
    from utils.candidate_info import extract_candidate_info

    resume_text = (
        "Priya Raghunathan\n"
        "Seattle, WA | +1 415-555-0139 | priya.raghunathan@example.org\n"
        "github.com/priyaraghu  linkedin.com/in/priya-raghunathan\n"
        "\n"
        "SUMMARY\n"
        "Backend engineer with eight years building distributed systems.\n"
        "\n"
        "EXPERIENCE\n"
        "Northwind Systems -- Senior Engineer -- 2021 to Present\n"
    )
    info = extract_candidate_info(resume_text)

    assert info["fullname"] == "Priya Raghunathan"
    assert info["email"] == "priya.raghunathan@example.org"
    assert info["phone"] == "+1 415-555-0139"
    assert info["location"] == "Seattle, WA"
    urls = [u for _, u in info["links"]]
    assert "https://github.com/priyaraghu" in urls
    assert "https://linkedin.com/in/priya-raghunathan" in urls


# --------------------------------------------------------------------------
# pagination  (the blank-page regression)
# --------------------------------------------------------------------------

@requires_pdflatex
@pytest.mark.parametrize("tid", TEMPLATE_IDS)
def test_short_resume_is_one_page(tid):
    pages = _compile_pages(tid, short_model_output(_module(tid)), INJECTED_INFO, "short")
    assert len(pages) == 1, f"template {tid}: short resume rendered {len(pages)} pages"


@requires_pdflatex
@pytest.mark.parametrize("tid", TEMPLATE_IDS)
def test_long_resume_has_no_blank_pages(tid):
    """Every page must carry text.

    This is the direct guard for the sidebar bug: a `tabular`-wrapped body that
    overflowed produced a page 1 with zero extractable text.
    """
    pages = _compile_pages(tid, long_model_output(_module(tid)), INJECTED_INFO, "long")

    assert len(pages) >= 2, (
        f"template {tid}: long fixture only rendered {len(pages)} page(s); "
        "the fixture is not long enough to exercise pagination"
    )
    blank = [i + 1 for i, p in enumerate(pages) if len(p.strip()) == 0]
    assert not blank, (
        f"template {tid}: blank page(s) {blank} of {len(pages)}. "
        "The body is almost certainly inside an unbreakable box."
    )


@requires_pdflatex
@pytest.mark.parametrize("tid", [2, 3, 4, 5])
def test_sidebar_appears_on_every_page(tid):
    """The sidebar furniture is drawn per page, not as one tall table row."""
    pdf = _compile(
        assemble_map[tid](long_model_output(_module(tid)), info=INJECTED_INFO),
        (tid, "long", repr(INJECTED_INFO)),
    )
    reader = PdfReader(str(pdf))

    # A filled sidebar band (2/3/5) paints a rectangle in the page's left
    # margin; template 4 paints a hairline. Either way there must be vector
    # content in the left margin on EVERY page, including page 2+.
    missing = [
        index
        for index, page in enumerate(reader.pages, start=1)
        if not _left_margin_has_graphics(page)
    ]
    assert not missing, (
        f"template {tid}: no sidebar in the left margin on page(s) {missing} -- "
        "the band is not being repeated on continuation pages"
    )


# The sidebar reaches the page two different ways, and which one depends on how
# pdfTeX chooses to emit the rule:
#
#   * templates 2/3/5 paint a filled band -> a rectangle, "x y w h re";
#   * template 4 paints a 0.5pt hairline, which pdfTeX optimises into a stroked
#     line inside a translated coordinate system -> "1 0 0 1 tx ty cm ... 0 0 m
#     0 H l S".
#
# Both must be recognised, and both must span the full page height -- that height
# requirement is what makes this a real regression guard, since it is exactly
# what a page-1-only sidebar would lack and what ordinary body decoration
# (heading underlines) never has.
_RE_BAND = re.compile(r"([-\d.]+)\s+[-\d.]+\s+[-\d.]+\s+([-\d.]+)\s+re")
_RE_RULE = re.compile(
    r"1\s+0\s+0\s+1\s+([-\d.]+)\s+[-\d.]+\s+cm"
    r"[\s\S]{0,200}?"
    r"([-\d.]+)\s+([-\d.]+)\s+m\s+([-\d.]+)\s+([-\d.]+)\s+l\s+S"
)


def _left_margin_has_graphics(page) -> bool:
    """True if the page draws the sidebar furniture in its left margin.

    The horizontal bound is 40% of the page width rather than 15% because
    template 4 sets its hairline 2.5in in, which is ~30% of an A4 page.
    """
    try:
        contents = page.get_contents()
        if contents is None:
            return False
        data = contents.get_data().decode("latin-1", "replace")
    except Exception:
        return False

    width = float(page.mediabox.width)
    height = float(page.mediabox.height)
    x_limit = width * 0.40
    h_min = height * 0.90

    for m in _RE_BAND.finditer(data):
        if float(m.group(1)) < x_limit and float(m.group(2)) > h_min:
            return True
    for m in _RE_RULE.finditer(data):
        start_y, end_y = float(m.group(3)), float(m.group(5))
        if float(m.group(1)) < x_limit and abs(end_y - start_y) > h_min:
            return True
    return False