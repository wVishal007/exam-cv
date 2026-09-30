# resume_format_paper_ink.py  (v5 -- standalone, no hardcoded contact info)
#
# Paper & Ink: pure black & white. The sidebar is NOT filled -- it is set off
# from the body by a single hairline rule, with a letter-spaced small-caps name.
# Maximum ATS-safety (zero color), with a distinctive editorial two-column look.
#
# LOCKED_TOP  = preamble + macros + header (sidebar). The model must never change it.
# BODY        = the only part the model rewrites.
# format      = LOCKED_TOP + BODY   (paste into the prompt as "Required Format")
# assemble()  = takes the model's output, DISCARDS whatever it did to the top,
#               and re-attaches the real LOCKED_TOP (built from INFO below).
#
# To change name / contact details, edit ONLY the INFO dict below.
# Nothing else in this file needs to change.

import re
img_preview = 'https://res.cloudinary.com/cxkcte6e/image/upload/v1790602621/Screenshot_2026-09-28_190207.png'

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
# Links/email are plain black here (that is the whole point of this template).
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

    line1 = []
    if info.get("email"):
        e = info["email"].strip()
        line1.append(rf"\href{{mailto:{e}}}{{{_esc(e)}}}")
    if info.get("phone"):
        line1.append(_esc(info["phone"]))
    if info.get("location"):
        line1.append(_esc(info["location"]))
    line1 = r"\sep ".join(line1)

    line2 = [rf"\link{{{url}}}{{{_esc(label)}}}" for label, url in info.get("links", []) or []]
    line2 = r"\sep ".join(line2)

    if line1 and line2:
        header_content = line1 + r"\newline" + "\n  " + line2
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
\usepackage[top=0.5in,bottom=0.5in,left=0.5in,right=0.5in]{geometry}
\usepackage{enumitem}
\usepackage{array}
\usepackage{titlesec}
\usepackage{xcolor}

\ifPDFTeX
  \usepackage[utf8]{inputenc}
  \usepackage[T1]{fontenc}
  \usepackage{helvet}
  \renewcommand{\familydefault}{\sfdefault}
  \usepackage{microtype}
  \microtypesetup{expansion=false}
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

% Pure black & white -- "accent"/"muted" still exist so the shared macros
% work unmodified, they just both resolve to near-black here.
\definecolor{accent}{HTML}{000000}
\definecolor{muted}{HTML}{404040}

\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}
\setlength{\emergencystretch}{3em}
\raggedbottom
\hyphenpenalty=10000 \exhyphenpenalty=10000 \raggedright
\renewcommand{\normalsize}{\fontsize{9.8}{12.2}\selectfont}
\AtBeginDocument{\normalsize}

% Heading: small-caps with a short centered hairline underneath.
\newif\iffirstentry
\newcommand{\boundary}[1]{%
  \global\firstentrytrue
  {\fontsize{10.4}{12}\selectfont\bfseries\scshape#1}\par
  \vspace{1pt}{\hfill\rule{0.45\linewidth}{0.3pt}\hfill}\par\vspace{1pt}}
\titleformat{\section}
  {\global\firstentrytrue}
  {}{0em}
  {\boundary}
\titlespacing*{\section}{0pt}{8pt}{3pt}

% ================= MACROS: the model may only USE these ====================
\newenvironment{bullets}
  {\begin{itemize}[nosep,leftmargin=1.1em,labelsep=0.5em,label=\textbullet,
     itemsep=1pt,topsep=1.5pt]}
  {\end{itemize}}

% One bullet. Braced, so text starting with [ is never read as an \item label.
\newcommand{\bul}[1]{\item {#1}}

\newcommand{\gap}{\iffirstentry\global\firstentryfalse\else\vspace{3pt}\fi}
\newcommand{\sep}{\ \textbar\ }
\newcommand{\link}[2]{\href{#1}{\textcolor{accent}{#2}}}

% \entry{Organization}{Location}{Role or Degree}{Dates}   ({} = empty)
\newcommand{\entry}[4]{%
  \gap\noindent\textbf{#1}\hfill #2\par
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

\setlength{\tabcolsep}{0pt}
\noindent
\begin{tabular}[t]{@{}p{0.33\textwidth}@{\hspace{0.03\textwidth}\vrule width 0.5pt\hspace{0.04\textwidth}}>{\raggedright\arraybackslash}p{\dimexpr0.60\textwidth\relax}@{}}
  {\fontsize{18}{21}\selectfont\bfseries\fullname}
  \vspace{3pt}

  {\small
  \renewcommand{\link}[2]{\href{#1}{#2}}
  @@HEADER_CONTENT@@}
  &
'''

LOCKED_TOP = _fill(LOCKED_TOP_TEMPLATE, _render_header(INFO))

BODY_MARK = '%%%%%%%%%% BODY: rewrite everything below this line %%%%%%%%%%'

BODY = r'''
\section{Summary}
[2-3 sentence factual summary. Delete this section if it adds nothing.]

\section{Technical Skills}
\skill{Languages}{[items]}
\skill{Frontend}{[items]}
\skill{Backend}{[items]}
\skill{Databases}{[items]}
\skill{Tools \& DevOps}{[items]}
\skill{Fundamentals}{[items]}

\section{Projects}
\project{[Project Name]}{[Tech, Stack]}{\link{[url]}{Live Demo}\sep\link{[url]}{GitHub}}
\begin{bullets}
\bul{[Bullet]}
\bul{[Bullet]}
\end{bullets}

\section{Experience}
\entry{[Company]}{[City, Country or Remote]}{[Role]}{[Mon YYYY] -- [Mon YYYY or Present]}
\begin{bullets}
\bul{[Bullet]}
\bul{[Bullet]}
\end{bullets}

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
   preamble, macros, header, or the sidebar. Only rewrite what is below that line.
2. Use ONLY these macros in the body:
     \section{}                      standard names only: Summary, Technical Skills,
                                     Projects, Experience, Education, Achievements,
                                     Certifications
     \skill{Label}{items}            one skills row (NOT inside a bullets environment)
     \entry{Org}{Location}{Role}{Dates}
                                     jobs and education; put {} for unknown location
     \project{Name}{Tech}{Links}     projects; Tech = comma-separated stack taken ONLY
                                     from the original resume
     \begin{bullets} \bul{} \end{bullets}
     \link{url}{text}   \sep
   Never use raw \item, \begin{itemize}, \\, \vspace, \textbf for headings, or
   new packages.
3. Every macro argument must be present. Write {} for an empty one.
4. Escape these in all text: & -> \&   % -> \%   $ -> \$   # -> \#   _ -> \_
   Never write a bare { or } inside text.
5. Use only "--" for date ranges and "---" as a separator. No emoji, arrows, smart
   quotes, or unicode bullets. No markdown (**bold**, `code`, - lists).
6. Dates: one consistent format everywhere, "Mon YYYY -- Mon YYYY" (or "Present").
7. Output raw LaTeX only. No ``` fences and no commentary. End with \end{document}.
   Do NOT write \end{tabular} yourself -- the pipeline closes the table.
8. Keep it to ONE page: bullets under ~28 words, at most 3 bullets per role or
   project, at most 4 certifications.
9. Never invent metrics, employers, locations, dates, technologies, or
   responsibilities. If a fact is not in the original resume, leave it out.
'''


def assemble(model_output: str) -> str:
    """Re-attach the real LOCKED_TOP (rendered from INFO above) to whatever
    body the model produced. Anything the model did to the preamble/header
    is discarded -- so INFO is the *only* place contact details can come
    from, never something the model guessed or hallucinated.
    The sidebar table is closed here so the model never needs to emit it.
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

    body = re.sub(r"\\end\{tabular\}\\end\{document\}\s*$", "", body.strip()).strip()
    body = re.sub(r"\\end\{document\}\s*$", "", body.strip()).strip()
    return LOCKED_TOP + BODY_MARK + "\n\n" + body + "\n\n\\end{tabular}\n\\end{document}\n"