# resume_format_locked.py  (v3)
#
# LOCKED_TOP  = preamble + macros + header.  The model must never change it.
# BODY        = the only part the model rewrites.
# format      = LOCKED_TOP + BODY   (paste into the prompt as "Required Format")
# assemble()  = takes the model's output, DISCARDS whatever it did to the top,
#               and re-attaches the real LOCKED_TOP.
#
# To change your name / contact details, edit \fullname and the HEADER block
# inside LOCKED_TOP. Nothing else needs to change.

import re

LOCKED_TOP = r'''\documentclass[a4paper,10pt]{article}

\usepackage{iftex}
\usepackage{etoolbox}
\usepackage{parskip}
\usepackage[top=0.4in,bottom=0.4in,left=0.5in,right=0.5in]{geometry}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{xcolor}

% ---- Font: works on ANY engine, and ligatures are OFF ----------------------
% Ligatures (fi, fl, ffi) can extract as a single odd glyph in some ATS
% parsers, turning "workflow" into "work ow". Disabling them costs nothing.
\ifPDFTeX
  \usepackage[utf8]{inputenc}
  \usepackage[T1]{fontenc}
  \usepackage{helvet}
  \renewcommand{\familydefault}{\sfdefault}
  \usepackage{microtype}
  \DisableLigatures[f]{encoding = *, family = *}
  \input{glyphtounicode}   % map glyphs to Unicode so copy/paste + ATS work
  \pdfgentounicode=1
\else
  \usepackage{fontspec}
  \defaultfontfeatures{Ligatures={NoCommon,TeX}}
  \IfFontExistsTF{Liberation Sans}
    {\setmainfont{Liberation Sans}}
    {\IfFontExistsTF{TeX Gyre Heros}{\setmainfont{TeX Gyre Heros}}{}}
\fi

\usepackage[hidelinks,unicode]{hyperref}

% ---- Identity (edit here; ATS parsers expect first + last name) ------------
\newcommand{\fullname}{Vishal}
\hypersetup{pdftitle={\fullname{} - Resume},pdfauthor={\fullname}}

% ---- Colors ----------------------------------------------------------------
\definecolor{accent}{HTML}{1F3A5F}    % deep navy (use 000000 for pure black)
\definecolor{muted}{HTML}{4D4D4D}     % dates / secondary text

% ---- Page ------------------------------------------------------------------
\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}
\setlength{\emergencystretch}{3em}
\raggedbottom
% No hyphenation: a parser must never see "Chro-" + "maDB" for ChromaDB.
% Ragged-right (not justified) so disabling hyphenation leaves no wide gaps.
\hyphenpenalty=10000 \exhyphenpenalty=10000 \raggedright
% Body type: 9.5pt on 11.4pt leading (headings stay 10pt bold, so hierarchy holds).
% FIT KNOB: if a longer resume spills onto page 2, use {9}{10.8}.
\renewcommand{\normalsize}{\fontsize{9.5}{11.4}\selectfont}
\AtBeginDocument{\normalsize}

% ---- Section headings: bold, navy, uppercase, thin rule --------------------
% \firstentrytrue resets at every section so entry spacing is never added
% directly under a heading.
\newif\iffirstentry
% NB: \MakeUppercase lives in the *before-code* slot (4th argument), where it
% receives only the title. Putting \uppercase at the end of the format slot made
% it swallow the rule code after it and uppercase "accent" -> "ACCENT".
\titleformat{\section}
  {\fontsize{10.5}{12}\selectfont\bfseries\color{accent}\global\firstentrytrue}
  {}{0em}{\MakeUppercase}
  [\vspace{-2pt}{\color{accent}\titlerule[0.5pt]}]
\titlespacing*{\section}{0pt}{7pt}{3pt}

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
%   Company ........................ Location
%   Role (italic) .................. Dates
\newcommand{\entry}[4]{%
  \gap\noindent\textbf{#1}\hfill #2\par
  \noindent\textit{#3}\hfill\textcolor{muted}{#4}\par\vspace{1pt}}

% \project{Name}{Tech, Stack}{Links}                     ({} = empty)
\newcommand{\project}[3]{%
  \gap\noindent\textbf{#1}\ifblank{#2}{}{\sep\textit{#2}}\hfill #3\par\vspace{1pt}}

% \skill{Label}{comma, separated, items}
% One hanging-indent paragraph: no table, no box, clean ATS reading order.
\newlength{\skilllabel}\setlength{\skilllabel}{1.35in}
\newcommand{\skill}[2]{%
  \noindent\hangindent=\skilllabel\hangafter=1
  \makebox[\skilllabel][l]{\textbf{#1}}#2\par\vspace{1.5pt}}

\begin{document}

% ---------------- HEADER (LOCKED) ----------------
\begin{center}
  {\fontsize{23}{27}\selectfont\bfseries\color{accent}\fullname}\\[5pt]
  {\small
  \href{mailto:vishalsingh31879@gmail.com}{\textcolor{accent}{vishalsingh31879@gmail.com}}\sep
  +91 7290908461\\[1.5pt]
  \link{https://github.com/wVishal007}{github.com/wVishal007}\sep
  \link{https://linkedin.com/in/vishal-singh-188013324}{linkedin.com/in/vishal-singh-188013324}\sep
  \link{https://vishal4u.vercel.app}{vishal4u.vercel.app}}
\end{center}
\vspace{-4pt}

'''

BODY_MARK = "%%%%%%%%%% BODY: rewrite everything below this line %%%%%%%%%%"

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


def assemble(model_output: str) -> str:
    """Re-attach the real LOCKED_TOP to whatever body the model produced.

    Anything the model did to the preamble/header is discarded. Also strips
    markdown fences and guarantees exactly one \\end{document}.
    """
    s = (model_output or "").strip()
    s = re.sub(r"^```[a-zA-Z]*[ \t]*\n?", "", s)   # opening fence
    s = re.sub(r"\n?```[ \t]*$", "", s)             # closing fence

    if BODY_MARK in s:
        body = s.split(BODY_MARK, 1)[1]
    else:
        m = re.search(r"\\section\s*\{", s)           # marker dropped: first section
        if not m:
            raise ValueError("Model output contains no body (no marker, no \\section).")
        body = s[m.start():]

    body = re.sub(r"\\end\{document\}\s*$", "", body.strip()).strip()
    return LOCKED_TOP + BODY_MARK + "\n\n" + body + "\n\n\\end{document}\n"