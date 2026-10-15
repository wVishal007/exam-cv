"""Best-effort candidate identity from the text of an uploaded resume PDF.

`POST /rewrite_resume` receives an extracted PDF, not a profile -- `/my/profile`
stores only `user_id`. The name / email / phone / links live at the top of that
text, so they are recovered here and handed to
`assemble(model_output, info=...)` rather than being baked into a template.

This is deliberately done in Python instead of asking the model to copy the
header across: the rewrite prompt already tells the model to fill the contact
lines from the original, and it still emits placeholders like
`\\link{[linkedin url]}{[linkedin.com/in/handle]}`. A regex cannot invent a
handle, and a missed field degrades to the bracketed placeholder.

Every field is optional. Whatever cannot be found is simply omitted, and the
template's `resolve_info` decides what to render.
"""

import re

__all__ = ["extract_candidate_info"]

# Resume text is noisy; only the header block is worth scanning.
HEAD_LINES = 40
STRICT_HEAD_LINES = 8

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

# A run of digits/separators with at least 7 digits. The leading group allows
# "(415", "+44" and bare "415". Date ranges like "2019 -- 2023" also match this
# shape, so `_looks_like_date` rejects them.
_PHONE = re.compile(r"[\(+]?\d[\d\s()./-]{6,}\d")

# "Seattle, WA" / "Austin, TX" -- a two-letter state or region code.
_LOCATION_STATE = re.compile(
    r"^\s*([A-Z][A-Za-z.'-]*(?:[ -][A-Z][A-Za-z.'-]+)*)\s*,\s*"
    r"([A-Z]{2})\b(?![A-Za-z])"
)

# "Berlin, Germany" / "Toronto, Ontario" -- a capitalised place after the comma.
_LOCATION_COUNTRY = re.compile(
    r"^\s*([A-Z][A-Za-z.'-]*(?:[ -][A-Z][A-Za-z.'-]+)*)\s*,\s*"
    r"([A-Z][A-Za-z]+(?:[ -][A-Z][A-Za-z]+)?)\s*(?:$|[|•·])"
)

# "github.com/x", "linkedin.com/in/x", "www.example.com", "https://x.dev"
_DOMAIN = re.compile(
    r"\b(?:https?://)?(?:www\.)?"
    r"([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+"
    r"(?:/[^\s|,;)\]]*)?)"
)

_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")

# Words that open a section rather than name a person.
_SECTION_WORDS = {
    "summary", "objective", "profile", "experience", "experiences",
    "education", "skills", "projects", "project", "certifications",
    "certification", "achievements", "awards", "contact", "contacts",
    "resume", "curriculum", "vitae", "cv", "employment", "internship",
    "internships", "publications", "references", "languages", "interests",
    "technical", "professional", "work", "history", "achievement",
}

# Job-title vocabulary. A line containing one of these is a role, not a person,
# however plausible its length and letter ratio look.
_TITLE_WORDS = {
    "senior", "junior", "mid", "staff", "principal", "lead", "head", "chief",
    "software", "hardware", "web", "data", "ml", "ai", "devops", "sre",
    "engineer", "developer", "programmer", "architect", "analyst", "manager",
    "consultant", "designer", "scientist", "researcher", "specialist",
    "administrator", "coordinator", "officer", "president", "founder",
    "director", "intern", "trainee", "assistant", "associate", "advisor",
    "technician", "accountant", "nurse", "teacher", "professor", "writer",
    "editor", "marketer", "executive", "administrator", "recruiter",
    "sde", "mle", "pm", "product", "business", "marketing", "sales",
}

_STRIP_CHARS = ".,;:|-–— \t"


def _head_lines(text: str, count: int) -> list[str]:
    lines = (text or "").splitlines()
    return [ln for ln in lines[:count]]


def _looks_like_date(candidate: str) -> bool:
    """True for date ranges that would otherwise pass the phone regex."""
    return bool(_YEAR.search(candidate)) or "--" in candidate or "–" in candidate


def _clean(value: str) -> str:
    return value.strip(_STRIP_CHARS).strip()


def _find_email(lines: list[str]) -> str:
    for line in lines:
        match = _EMAIL.search(line)
        if match:
            return match.group(0)
    return ""


def _find_phone(lines: list[str]) -> str:
    for line in lines:
        for match in _PHONE.finditer(line):
            digits = sum(ch.isdigit() for ch in match.group(0))
            if digits < 7 or _looks_like_date(match.group(0)):
                continue
            candidate = _clean(re.sub(r"\s+", " ", match.group(0)))
            # A leading "+" is worth keeping; trailing punctuation is not.
            if candidate:
                return candidate
    return ""


def _find_location(lines: list[str]) -> str:
    for pattern in (_LOCATION_STATE, _LOCATION_COUNTRY):
        for line in lines:
            match = pattern.match(line)
            if not match:
                continue
            city, region = match.group(1).strip(), match.group(2).strip()
            # Reject "Amazon, Inc" style false positives.
            if city.lower() in {"inc", "llc", "ltd", "corp", "co"}:
                continue
            if region.lower() in {"inc", "llc", "ltd", "corp"}:
                continue
            return f"{city}, {region}"
    return ""


def _name_is_plausible(line: str) -> bool:
    stripped = line.strip()
    if not stripped or len(stripped) > 60:
        return False
    if "@" in stripped or "http" in stripped or "www." in stripped:
        return False
    # Prose, not a name: "Experienced engineer." / "Senior Engineer with 8 yrs".
    if stripped.endswith("."):
        return False

    words = stripped.split()
    if not 1 <= len(words) <= 6:
        return False

    if stripped.lower().strip(_STRIP_CHARS) in _SECTION_WORDS:
        return False

    # A job title -- "SENIOR SOFTWARE ENGINEER", "Data Analyst".
    if any(word.strip(_STRIP_CHARS).lower() in _TITLE_WORDS for word in words):
        return False

    letters = sum(ch.isalpha() for ch in stripped)
    if letters / len(stripped) < 0.6:
        return False
    return any(ch.isalpha() for ch in stripped)


def _find_fullname(lines: list[str]) -> str:
    for line in lines:
        if _name_is_plausible(line):
            return _clean(line)
    return ""


def _find_links(lines: list[str], limit: int = 6) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    seen: set[str] = set()

    for line in lines:
        # Emails contain dots and would otherwise look like domains.
        scrubbed = _EMAIL.sub(" ", line)
        for match in _DOMAIN.finditer(scrubbed):
            domain = _clean(match.group(1))
            if not domain or "@" in domain:
                continue

            host = domain.split("/")[0]
            labels = host.split(".")
            if len(labels) < 2:
                continue
            # The last label must be a real-looking TLD, not a version number.
            if not re.fullmatch(r"[A-Za-z]{2,}", labels[-1]):
                continue
            if re.fullmatch(r"v?\d+", labels[0], flags=re.IGNORECASE):
                continue

            key = domain.lower()
            if key in seen:
                continue
            seen.add(key)

            url = domain if domain.startswith("http") else f"https://{domain}"
            found.append((domain, url))
            if len(found) >= limit:
                return found

    return found


def extract_candidate_info(resume_text: str) -> dict:
    """Pull whatever identity can be recovered from extracted resume text.

    Returns a dict with any of `fullname`, `email`, `phone`, `location` and
    `links` that were found. Missing keys are simply absent -- the caller
    decides whether to fall back to a placeholder.
    """
    text = resume_text or ""
    head = _head_lines(text, HEAD_LINES)
    strict = _head_lines(text, STRICT_HEAD_LINES)

    info: dict = {
        "fullname": _find_fullname(strict),
        "email": _find_email(strict),
        "phone": _find_phone(strict),
        "location": _find_location(strict),
        "links": _find_links(strict),
    }
    return {key: value for key, value in info.items() if value}