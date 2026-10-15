# resume_format_burgundy_elegant.py  (standalone, no hardcoded contact info)
#
# LOCKED_TOP  = preamble + macros + header. The model must never change it.
# BODY        = the only part the model rewrites.
# format      = LOCKED_TOP + BODY   (paste into the prompt as "Required Format")
# assemble()  = takes the model's output, DISCARDS whatever it did to the top,
#               and re-attaches a header rendered from the `info` argument.
#               There is no module-level identity: the candidate's details are
#               supplied per call, and omitted ones render as a placeholder.
import re

from ._common import PLACEHOLDER_INFO, fill, render_header

img_preview = 'https://res.cloudinary.com/cxkcte6e/image/upload/v1790602622/Screenshot_2026-09-28_190257.png'

# ============================================================================
# Identity is supplied PER CALL by the caller -- see assemble() below.
# The module-level INFO dict that used to live here was baked into LOCKED_TOP at
# import time, so every generated resume was stamped with the template author's
# name.
# ============================================================================

def _header_tokens(info):
    """This template's flavour of the shared header renderer.

    `link_color` applies to the header only -- the body's \\link macro keeps its
    own colour, because the sidebar templates need light-on-dark up here and
    normal-on-paper down there.
    """
    return render_header(info, link_color="accent", line_break=r"\\[1.5pt]")


LOCKED_TOP_TEMPLATE = r'''\documentclass[a4paper,10pt]{article}

\usepackage{iftex}
\usepackage{etoolbox}
\usepackage{parskip}
\usepackage[top=0.45in,bottom=0.45in,left=0.55in,right=0.55in]{geometry}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{xcolor}

% Serif body throughout -- default Latin Modern Roman under pdflatex is
% embedded & ATS-safe; xelatex/lualatex upgrade to a nicer serif if present.
\ifPDFTeX
  \usepackage[utf8]{inputenc}
  \usepackage[T1]{fontenc}
  \usepackage{microtype}
  \DisableLigatures[f]{encoding = *, family = *}
  \input{glyphtounicode}
  \pdfgentounicode=1
\else
  \usepackage{fontspec}
  \defaultfontfeatures{Ligatures={NoCommon,TeX}}
  \IfFontExistsTF{TeX Gyre Pagella}
    {\setmainfont{TeX Gyre Pagella}}
    {\IfFontExistsTF{Liberation Serif}{\setmainfont{Liberation Serif}}{}}
\fi

\usepackage[hidelinks,unicode]{hyperref}

\newcommand{\fullname}{@@FULLNAME@@}
\hypersetup{pdftitle={\fullname{} - Resume},pdfauthor={\fullname}}

\definecolor{accent}{HTML}{6B1E2B}    % deep burgundy
\definecolor{muted}{HTML}{545454}

\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}
\setlength{\emergencystretch}{3em}
\raggedbottom
\hyphenpenalty=10000 \exhyphenpenalty=10000 \raggedright
\renewcommand{\normalsize}{\fontsize{9.6}{11.8}\selectfont}
\AtBeginDocument{\normalsize}

% Small-caps heading framed top and bottom by a hairline rule -- quiet,
% formal, no fill color, just typography.
\newif\iffirstentry
\titleformat{\section}
  {\fontsize{10.2}{12}\selectfont\bfseries\scshape\color{accent}\global\firstentrytrue}
  {}{0em}{}
  [\vspace{-1.5pt}{\color{accent}\titlerule[0.3pt]}]
\titlespacing*{\section}{0pt}{9pt}{3pt}
\newcommand{\rulebefore}{\vspace{1pt}{\color{accent!55}\hrule height 0.3pt}\vspace{4pt}}

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
\newlength{\skilllabel}\setlength{\skilllabel}{1.35in}
\newcommand{\skill}[2]{%
  \noindent\hangindent=\skilllabel\hangafter=1
  \makebox[\skilllabel][l]{\textbf{#1}}#2\par\vspace{1.5pt}}

\begin{document}

% ---------------- HEADER ----------------
\begin{center}
  {\fontsize{22}{26}\selectfont\bfseries\scshape\color{accent}\fullname}\\[3pt]
  {\color{accent}\rule{0.32\linewidth}{0.3pt}\hspace{4pt}\raisebox{-1.5pt}{\color{accent}\tiny$\bullet$}\hspace{4pt}\rule{0.32\linewidth}{0.3pt}}\\[5pt]
  {\small
  @@HEADER_CONTENT@@}

\end{center}
\vspace{-3pt}

'''

# Only used to build `format`, the skeleton sent to the model. assemble()
# renders a fresh header per call and never returns this.
LOCKED_TOP = fill(LOCKED_TOP_TEMPLATE, _header_tokens(PLACEHOLDER_INFO))

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
     \section{}                      standard names only: Summary, Technical Skills,
                                     Experience, Projects, Education, Achievements,
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
8. Keep it to ONE page: bullets under ~28 words, at most 3 bullets per role or
   project, at most 4 certifications.
9. Never invent metrics, employers, locations, dates, technologies, or
   responsibilities. If a fact is not in the original resume, leave it out.
'''


def assemble(model_output: str, info: dict | None = None) -> str:
    """Re-attach the header for `info` to whatever body the model produced.

    Anything the model did to the preamble or the header is discarded, so
    contact details can only ever come from `info` -- never from something the
    model guessed. With no `info`, a clearly-marked placeholder is rendered.
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
    locked_top = fill(LOCKED_TOP_TEMPLATE, _header_tokens(info))
    return locked_top + BODY_MARK + "\n\n" + body + "\n\n\\end{document}\n"
