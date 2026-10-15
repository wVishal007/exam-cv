"""Shared helpers for the resume templates.

Before this module every `template_N.py` carried its own byte-identical copy of
`_ESCAPE_MAP`, `_esc` and `_fill`, plus one of four near-identical copies of
`_render_header`. The identity that a template renders is supplied *per call* to
`assemble(model_output, info=...)`, so that logic lives here once instead of
being duplicated eleven times.

Nothing in this module reads a module-level `INFO`; the candidate's details are
always an argument. If none are supplied, `PLACEHOLDER_INFO` is used so the
result is obviously a placeholder rather than somebody's real details.
"""

ESCAPE_MAP = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
    "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}

# Rendered when the caller supplies no identity. Deliberately bracketed so it can
# never be mistaken for real contact details.
PLACEHOLDER_INFO = {
    "fullname": "[CANDIDATE NAME]",
    "email": "[email@example.com]",
    "phone": "[phone number]",
    "location": "",
    "links": [],
}


def esc(text) -> str:
    """Escape LaTeX special characters. An empty value renders as nothing."""
    if not text:
        return ""
    return "".join(ESCAPE_MAP.get(ch, ch) for ch in str(text))


def fill(template: str, tokens: dict) -> str:
    """Substitute `@@KEY@@` placeholders in `template`."""
    out = template
    for key, val in tokens.items():
        out = out.replace(f"@@{key}@@", val)
    return out


def _with_scheme(url: str) -> str:
    """`github.com/x` -> `https://github.com/x`.

    A bare host in `\\href` becomes a document-relative link, which silently
    resolves against whatever page happens to embed the PDF.
    """
    url = str(url).strip()
    if not url:
        return url
    if url.startswith(("http://", "https://", "mailto:", "tel:")):
        return url
    if "@" in url and "/" not in url.split("@")[0]:
        return f"mailto:{url}"
    return f"https://{url}"


def _normalise_link(item):
    """Accept a url string, a (label, url) pair, or a mapping; return a pair."""
    if isinstance(item, str):
        url = item.strip()
        return (url, url) if url else None
    if isinstance(item, dict):
        url = str(item.get("url") or item.get("href") or "").strip()
        label = str(item.get("label") or item.get("text") or url).strip()
        return (label, url) if url else None
    try:
        label, url = item
    except (TypeError, ValueError):
        return None
    label = str(label or "").strip()
    url = str(url or "").strip()
    if not url:
        return None
    return (label or url, url)


def resolve_info(info) -> dict:
    """Normalise a candidate dict, falling back to `PLACEHOLDER_INFO`.

    Empty strings and unusable link entries are dropped so a half-filled profile
    degrades gracefully instead of rendering stray separators.
    """
    info = info or {}
    if not isinstance(info, dict):
        return dict(PLACEHOLDER_INFO)

    resolved = {}
    for key in ("fullname", "email", "phone", "location"):
        value = info.get(key)
        resolved[key] = str(value).strip() if value else ""

    if not resolved["fullname"]:
        resolved["fullname"] = PLACEHOLDER_INFO["fullname"]

    links = []
    for item in info.get("links") or []:
        pair = _normalise_link(item)
        if pair:
            label, url = pair
            links.append((label, _with_scheme(url)))
    resolved["links"] = links

    return resolved


def render_header(
    info,
    *,
    link_color: str | None = "accent",
    line_break: str = r"\\[1.5pt]",
) -> dict:
    """Build the `@@FULLNAME@@` / `@@HEADER_CONTENT@@` tokens.

    `link_color` is applied to the header's own links and email only. The body's
    `\\link` macro keeps its template-defined colour, because the sidebar
    templates need light-on-dark here and normal-on-paper there.

    `line_break` differs per template: a `[1.5pt]` vertical gap, a `\\newline`
    (sidebar), or `[3pt]` (template 6's two-column header).
    """
    info = resolve_info(info)
    fullname = info["fullname"]

    def tint(text: str) -> str:
        return rf"\textcolor{{{link_color}}}{{{text}}}" if link_color else text

    # Raw value inside the \href target, escaped value as the visible text, so an
    # "_" or "&" in an address or handle cannot break compilation.
    line1 = []
    if info["email"]:
        email = info["email"]
        line1.append(rf"\href{{mailto:{email}}}{{{tint(esc(email))}}}")
    if info["phone"]:
        line1.append(esc(info["phone"]))
    if info["location"]:
        line1.append(esc(info["location"]))
    line1 = r"\sep ".join(line1)

    line2 = [rf"\link{{{url}}}{{{tint(esc(label))}}}" for label, url in info["links"]]
    line2 = r"\sep ".join(line2)

    if line1 and line2:
        header_content = line1 + line_break + "\n  " + line2
    else:
        header_content = line1 or line2

    return {"FULLNAME": esc(fullname), "HEADER_CONTENT": header_content}