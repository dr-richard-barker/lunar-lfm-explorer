\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{npj-article}[2026/08/20 v2.0 npj Microgravity Publication Style Class]

\LoadClass[twocolumn,10pt,letterpaper]{article}

% Core Packages
\RequirePackage{graphicx}
\RequirePackage{amsmath,amssymb,amsfonts}
\RequirePackage{booktabs}
\RequirePackage{tabularx}
\RequirePackage{xcolor}
\RequirePackage{siunitx}
\RequirePackage[numbers,sort&compress,super]{natbib}
\RequirePackage{lineno}
\RequirePackage{fancyhdr}
\RequirePackage{microtype}
\RequirePackage{caption}

% Typography: Helvetica for sans, Times for serif
\RequirePackage{newtxtext,newtxmath}
\RequirePackage[scaled=0.92]{helvet}

% Page Geometry (NPG Standard)
\RequirePackage[
  top=20mm,
  bottom=22mm,
  left=18mm,
  right=18mm,
  columnsep=6.5mm,
  headheight=14pt,
  footskip=12mm
]{geometry}

% NPG Branding Colors
\definecolor{npjblue}{RGB}{0, 77, 115}
\definecolor{npjdblue}{RGB}{0, 48, 73}
\definecolor{npjorange}{RGB}{214, 40, 40}
\definecolor{linkblue}{RGB}{0, 102, 153}
\definecolor{grayhead}{RGB}{100, 100, 100}

% Hyperref Setup
\RequirePackage[
  colorlinks=true,
  linkcolor=linkblue,
  citecolor=linkblue,
  urlcolor=linkblue,
  breaklinks=true
]{hyperref}

% Section Heading Formatting (NPG Style)
\RequirePackage{titlesec}
\titleformat{\section}
  {\sffamily\bfseries\large\color{npjdblue}}
  {\thesection}{1em}{}[\titlerule]
\titleformat{\subsection}
  {\sffamily\bfseries\normalsize\color{npjdblue}}
  {\thesubsection}{1em}{}
\titleformat{\subsubsection}
  {\sffamily\bfseries\small\color{npjdblue}}
  {\thesubsubsection}{1em}{}

\titlespacing*{\section}{0pt}{14pt plus 2pt minus 2pt}{6pt plus 1pt minus 1pt}
\titlespacing*{\subsection}{0pt}{10pt plus 2pt minus 2pt}{4pt plus 1pt minus 1pt}
\titlespacing*{\subsubsection}{0pt}{8pt plus 2pt minus 2pt}{3pt plus 1pt minus 1pt}

% Caption Styling (NPG Style: bold Figure X | title)
\DeclareCaptionLabelSeparator{bar}{\space\textbf{|}\space}
\captionsetup{
  font={small,rm},
  labelfont={small,sf,bf},
  labelsep=bar,
  justification=justified,
  singlelinecheck=false
}

% Header and Footer
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\sffamily\footnotesize\textbf{npj} \textbf{\color{npjblue}microgravity}}
\fancyhead[R]{\sffamily\footnotesize\color{grayhead}ARTICLE \quad\textbar\quad OPEN}
\fancyfoot[L]{\sffamily\footnotesize\color{grayhead}Manuscript in preparation \quad \textbar\quad \url{https://github.com/dr-richard-barker/lunar-mars-magnetic-biology}}
\fancyfoot[R]{\sffamily\footnotesize\bfseries\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}

% Title and Metadata Storage
\newcommand{\abstracttext}[1]{\def\@abstracttext{#1}}
\newcommand{\keywordstext}[1]{\def\@keywordstext{#1}}

% npj Front Matter Macro
\newcommand{\makefrontmatter}{%
  \twocolumn[{%
    \vspace{-6mm}%
    {\sffamily\small\bfseries\color{npjblue}ARTICLE}\hfill{\sffamily\small\bfseries\color{npjorange}OPEN}\par
    \vspace{1.5mm}
    \hrule height 1.2pt
    \vspace{5mm}
    {\fontsize{18pt}{22pt}\sffamily\bfseries\color{npjdblue}\@title\par}%
    \vspace{4mm}
    {\fontsize{10.5pt}{13pt}\sffamily\@author\par}%
    \vspace{3mm}
    \hrule height 0.4pt
    \vspace{4mm}
    \@ifundefined{@abstracttext}{}{%
      \begin{minipage}{\textwidth}
        \sffamily\fontsize{9pt}{12.5pt}\selectfont
        \textbf{ABSTRACT}\par\vspace{1.5mm}
        \@abstracttext
        \@ifundefined{@keywordstext}{}{%
          \par\vspace{2mm}
          \textbf{Keywords:}\space\@keywordstext
        }
      \end{minipage}
      \vspace{4mm}
      \hrule height 0.4pt
    }
    \vspace{5mm}
  }]%
}
