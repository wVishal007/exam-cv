# resume_format_signal_block.py  (standalone, no hardcoded contact info)
#
# Teal accent, left-aligned name with a right-aligned contact block,
# section labels marked with a small filled color chip instead of a rule.
# Reads more "product/startup" than the other rule-underline templates.
# The chip is a real colorbox with real text next to it -- pdftotext still
# extracts the section label as plain text (see the self-test at the
# bottom: `python3 resume_format_signal_block.py`).
#
# Same fixed contract as every other file in this set:
#   LOCKED_TOP  = preamble + macros + header. The model must never change it.
#   BODY        = the only part the model rewrites.
#   format      = LOCKED_TOP + BODY   (paste into the prompt as "Required Format")
#   assemble()  = takes the model's output, DISCARDS whatever it did to the top,
#                 and re-attaches the real LOCKED_TOP.
#
# To change name / contact details, edit ONLY the INFO dict below.
# Nothing else in this file needs to change -- no separate identity module,
# no validate_identity, just one dict and assemble(model_output).

import re
img_preview = 'https://res.cloudinary.com/cxkcte6e/image/upload/v1790602622/Screenshot_2026-09-28_190246.png'

# ============================================================================
# EDIT THIS -- and only this -- to change whose resume it is.
# ============================================================================
INFO = {
    "fullname": "Jordan Avery",
    "email": "jordan.avery.dev@gmail.com",
    "phone": "+1 555-201-4477",
    "location": "",                      # optional -- e.g. "Austin, TX"
    "links": [
        ("github.com/jordanavery", "https://github.com/jordanavery"),
        ("linkedin.com/in/jordan-avery-dev", "https://linkedin.com/in/jordan-avery-dev"),
        ("jordanavery.dev", "https://jordanavery.dev"),
    ],
}

# ---- header rendering: turns INFO into LaTeX. Nothing about a person is
# ---- ever written directly into LOCKED_TOP_TEMPLATE below. ----------------
_ESCAPE_MAP = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
    "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}


def _esc(text):
    if not text:
        return ""
    return "".join(_ESCAPE_MAP.get(ch, ch) for ch in str(text))


def _render_header(info):
    fullname = info.get("fullname", "").strip()
    if not fullname:
        raise ValueError("INFO['fullname'] is required")

    # Right-hand contact block: email / phone / location on one line,
    # links on the next -- same escaping rule as everywhere else in this
    # file: raw value inside the \href target, escaped value as the
    # visible text, so an "_" or "&" in an address/handle can't break
    # compilation.
    line1 = []
    if info.get("email"):
        e = info["email"].strip()
        line1.append(rf"\href{{mailto:{e}}}{{\textcolor{{accent}}{{{_esc(e)}}}}}")
    if info.get("phone"):
        line1.append(_esc(info["phone"]))
    if info.get("location"):
        line1.append(_esc(info["location"]))
    line1 = r"\sep ".join(line1)

    line2 = [rf"\link{{{url}}}{{{_esc(label)}}}" for label, url in info.get("links", []) or []]
    line2 = r"\sep ".join(line2)

    if line1 and line2:
        header_content = line1 + r"\\[3pt]" + "\n  " + line2
    else:
        header_content = line1 or line2

    return {"FULLNAME": _esc(fullname), "HEADER_CONTENT": header_content}


def _fill(template, tokens):
    out = template
    for key, val in tokens.items():
        out = out.replace(f"@@{key}@@", val)
    return out


LOCKED_TOP_TEMPLATE = r'''\documentclass[a4paper,10pt]{article}

\usepackage{iftex}
\usepackage{etoolbox}
\usepackage{parskip}
\usepackage[top=0.45in,bottom=0.45in,left=0.55in,right=0.55in]{geometry}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{xcolor}
\usepackage{tikz}

\ifPDFTeX
  \usepackage[utf8]{inputenc}
  \usepackage[T1]{fontenc}
  \usepackage{helvet}
  \renewcommand{\familydefault}{\sfdefault}
  \usepackage{microtype}
  \DisableLigatures[f]{encoding = *, family = *}
  \input{glyphtounicode}
  \pdfgentounicode=1
\else
  \usepackage{fontspec}
  \defaultfontfeatures{Ligatures={NoCommon,TeX}}
  \IfFontExistsTF{Liberation Sans}
    {\setmainfont{Liberation Sans}}
    {\IfFontExistsTF{TeX Gyre Heros}{\setmainfont{TeX Gyre Heros}}{}}
\fi

\usepackage[hidelinks,unicode]{hyperref}

\newcommand{\fullname}{@@FULLNAME@@}
\hypersetup{pdftitle={\fullname{} - Resume},pdfauthor={\fullname}}

\definecolor{accent}{HTML}{0F5C4C}    % deep teal (swap for any single hue)
\definecolor{accentbg}{HTML}{E8F2EF} % pale tint for the section tag fill
\definecolor{muted}{HTML}{4D4D4D}

\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}
\setlength{\emergencystretch}{3em}
\raggedbottom
\hyphenpenalty=10000 \exhyphenpenalty=10000 \raggedright
% FIT KNOB: drop to {9}{10.8} if a longer resume spills onto page 2.
\renewcommand{\normalsize}{\fontsize{9.5}{11.4}\selectfont}
\AtBeginDocument{\normalsize}

% Section label: a small filled accent chip + bold caps + thin accent rule.
\newif\iffirstentry
\titleformat{\section}
  {\fontsize{9.5}{9.5}\selectfont\bfseries\color{accent}\global\firstentrytrue}
  {\raisebox{-1.2pt}{\tikz[baseline]\fill[accent] (0,0) rectangle (6pt,9pt);}}
  {5pt}
  {\MakeUppercase}
  [\vspace{-3pt}{\color{accentbg}\titlerule[1.6pt]}]
\titlespacing*{\section}{0pt}{8pt}{4pt}

% ================= MACROS: the model may only USE these ====================
\newenvironment{bullets}
  {\begin{itemize}[nosep,leftmargin=1.1em,labelsep=0.5em,label=\textcolor{accent}{\textbullet},
     itemsep=1pt,topsep=1.5pt]}
  {\end{itemize}}

\newcommand{\bul}[1]{\item {#1}}
\newcommand{\gap}{\iffirstentry\global\firstentryfalse\else\vspace{3pt}\fi}
\newcommand{\sep}{\ \textbar\ }
\newcommand{\link}[2]{\href{#1}{\textcolor{accent}{#2}}}

% \entry{Organization}{Location}{Role or Degree}{Dates}   ({} = empty)
\newcommand{\entry}[4]{%
  \gap\noindent\textbf{#1}\hfill\textcolor{muted}{#2}\par
  \noindent\textit{#3}\hfill\textcolor{muted}{#4}\par\vspace{1pt}}

% \project{Name}{Tech, Stack}{Links}                     ({} = empty)
\newcommand{\project}[3]{%
  \gap\noindent\textbf{#1}\ifblank{#2}{}{\sep\textit{#2}}\hfill #3\par\vspace{1pt}}

% \skill{Label}{comma, separated, items}
\newlength{\skilllabel}\setlength{\skilllabel}{1.3in}
\newcommand{\skill}[2]{%
  \noindent\hangindent=\skilllabel\hangafter=1
  \makebox[\skilllabel][l]{\textbf{\textcolor{accent}{#1}}}#2\par\vspace{1.5pt}}

\begin{document}

% ---------------- HEADER: name left, contact block right ----------
\noindent
\begin{minipage}[t]{0.55\textwidth}
  {\fontsize{22}{26}\selectfont\bfseries\fullname}
\end{minipage}%
\begin{minipage}[t]{0.45\textwidth}
  \raggedleft\small
  @@HEADER_CONTENT@@
\end{minipage}
\vspace{2pt}

'''

LOCKED_TOP = _fill(LOCKED_TOP_TEMPLATE, _render_header(INFO))

BODY_MARK = "%%%%%%%%%% BODY: rewrite everything below this line %%%%%%%%%%"

BODY = r'''
\section{Summary}
[2-3 sentence factual summary. Delete this section if it adds nothing.]

\section{Experience}
\entry{[Company]}{[City, Country or Remote]}{[Role]}{[Mon YYYY] -- [Mon YYYY or Present]}
\begin{bullets}
\bul{[Bullet]}
\bul{[Bullet]}
\end{bullets}

\section{Projects}
\project{[Project Name]}{[Tech, Stack]}{\link{[url]}{Live Demo}\sep\link{[url]}{GitHub}}
\begin{bullets}
\bul{[Bullet]}
\bul{[Bullet]}
\end{bullets}

\section{Technical Skills}
\skill{Languages}{[items]}
\skill{Frameworks}{[items]}
\skill{Tools}{[items]}

\section{Education}
\entry{[Institution]}{[City, Country]}{[Degree]}{[YYYY] -- [YYYY]}

\section{Achievements}
\begin{bullets}
\bul{[Award] --- [Event]}
\end{bullets}

\section{Certifications}
\begin{bullets}
\bul{[Certification] --- [Issuer]}
\end{bullets}
'''

# What you paste into the prompt as "Required Format".
format = LOCKED_TOP + BODY_MARK + "\n" + BODY

# Append to the rewrite prompt.
format_rules = r'''
LATEX OUTPUT RULES (breaking any of these breaks compilation):
1. Return the full document. Copy everything ABOVE the line
   "%%%%%%%%%% BODY ..." EXACTLY, character for character. Do not edit the
   preamble, macros, or header. Only rewrite what is below that line.
2. Use ONLY these macros in the body:
     \section{}                      standard names only: Summary, Experience,
                                     Projects, Technical Skills, Education,
                                     Achievements, Certifications
     \entry{Org}{Location}{Role}{Dates}   jobs and education; {} for unknown location/role
     \project{Name}{Tech}{Links}          Tech = stack taken ONLY from the original resume
     \skill{Label}{items}                 one skills row, NOT inside bullets
     \begin{bullets} \bul{} \end{bullets}
     \link{url}{text}   \sep
   Never use raw \item, \begin{itemize}, \\, \vspace, \textbf for headings, or
   new packages.
3. Every macro argument must be present. Write {} for an empty one.
4. Escape: & -> \&   % -> \%   $ -> \$   # -> \#   _ -> \_. Never write a bare
   { or } inside text.
5. Use only "--" for date ranges and "---" as a separator. No emoji, arrows,
   smart quotes, unicode bullets, or markdown.
6. Dates: one consistent format everywhere, "Mon YYYY -- Mon YYYY" (or "Present").
7. Output raw LaTeX only. No ``` fences, no commentary. End with \end{document}.
8. Keep it to ONE page: bullets under ~28 words, at most 3 per role/project,
   at most 4 certifications.
9. Never invent metrics, employers, locations, dates, technologies, or
   responsibilities. If a fact is not in the original resume, leave it out.
'''


def assemble(model_output: str) -> str:
    """Re-attach the real LOCKED_TOP (rendered from INFO above) to whatever
    body the model produced. Anything the model did to the preamble/header
    is discarded -- so INFO is the *only* place contact details can come
    from, never something the model guessed or hallucinated.
    """
    s = (model_output or "").strip()
    s = re.sub(r"^```[a-zA-Z]*[ \t]*\n?", "", s)   # opening fence
    s = re.sub(r"\n?```[ \t]*$", "", s)             # closing fence

    if BODY_MARK in s:
        body = s.split(BODY_MARK, 1)[1]
    else:
        m = re.search(r"\\section\s*\{", s)         # marker dropped: first section
        if not m:
            raise ValueError("Model output contains no body (no marker, no \\section).")
        body = s[m.start():]

    body = re.sub(r"\\end\{document\}\s*$", "", body.strip()).strip()
    return LOCKED_TOP + BODY_MARK + "\n\n" + body + "\n\n\\end{document}\n"


if __name__ == "__main__":
    import shutil, subprocess, sys, tempfile

    sample_body_output = BODY_MARK + r'''
\section{Summary}
Backend engineer who previously worked at Smith \& Co on 50\% of their
payments platform.
\section{Experience}
\entry{Smith \& Co}{Remote}{Engineer}{Jan 2023 -- Present}
\begin{bullets}
\bul{Shipped a payments API used by 50\% of the company's clients.}
\end{bullets}
\section{Projects}
\section{Technical Skills}
\skill{Languages}{Python, Go}
\section{Education}
\entry{State University}{City}{B.S. CS}{2019 -- 2023}
\section{Achievements}
\begin{bullets}
\bul{Employee of the Quarter}
\end{bullets}
\section{Certifications}
\begin{bullets}
\bul{Example Cert --- Example Org}
\end{bullets}
'''
    if not shutil.which("pdflatex"):
        print("pdflatex not found on PATH -- skipping compile check.")
        sys.exit(0)
    final_tex = assemble(sample_body_output)
    with tempfile.TemporaryDirectory() as td:
        with open(f"{td}/test.tex", "w") as f:
            f.write(final_tex)
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "test.tex"],
            cwd=td, capture_output=True, text=True,
        )
        if result.returncode != 0:
            print("COMPILE FAILED")
            print(result.stdout[-3000:])
            sys.exit(1)
        print("Compile OK.")
        if shutil.which("pdftotext"):
            extracted = subprocess.run(["pdftotext", f"{td}/test.pdf", "-"], capture_output=True, text=True).stdout
            assert "EXPERIENCE" in extracted
            print("pdftotext extraction OK: chip label extracted as plain text.")
