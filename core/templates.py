"""
core/templates.py
Pre-seeded master LaTeX resume templates for Daisy Phukan and Shashwat Gautam.
"""

DEFAULT_DAISY_TEX = r"""%-------------------------
% Master Resume - Daisy Phukan
% Jake Gutierrez Template (MIT)
%------------------------

\documentclass[letterpaper,10pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\usepackage{fontawesome5}
\usepackage{multicol}
\input{glyphtounicode}

\definecolor{linkblue}{RGB}{11, 87, 208}
\usepackage[colorlinks=true, urlcolor=linkblue, linkcolor=linkblue]{hyperref}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

\addtolength{\oddsidemargin}{-0.60in}
\addtolength{\evensidemargin}{-0.60in}
\addtolength{\textwidth}{1.20in}
\addtolength{\topmargin}{-.70in}
\addtolength{\textheight}{1.42in}

\urlstyle{same}
\raggedbottom
\setlength{\tabcolsep}{0in}

\titleformat{\section}{
  \vspace{-3pt}\scshape\raggedright\small\bfseries
}{}{0em}{}[\color{black}\titlerule \vspace{-3pt}]

\pdfgentounicode=1

\newcommand{\resumeItem}[1]{
  \item\footnotesize{
    {#1 \vspace{-2.5pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2.5pt}\item
    \begin{tabular*}{1.0\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{\footnotesize #1} & \textbf{\footnotesize #2} \\
      \textit{\footnotesize #3} & \textit{\footnotesize #4} \\
    \end{tabular*}\vspace{-5pt}
}

\newcommand{\resumeProjectHeading}[3]{
    \vspace{-2.5pt}\item
    \begin{tabular*}{1.0\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{\footnotesize #1} $|$ \textit{\footnotesize #2} & \footnotesize #3 \\
    \end{tabular*}\vspace{-5pt}
}

\renewcommand\labelitemi{$\vcenter{\hbox{\tiny$\bullet$}}$}
\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.0in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}[leftmargin=0.15in, itemsep=1.5pt, parsep=0pt, topsep=1.5pt]}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-3pt}}

\begin{document}

%----------HEADING----------
\begin{center}
    {\LARGE \scshape Daisy Phukan} \\ \vspace{2pt}
    \textbf{\small Technical Project Manager -- Trainee $|$ Enterprise Operations \& Systems $|$ B.Tech Mechanical} \\ \vspace{2.5pt}
    \footnotesize \raisebox{-0.1\height}\faPhone\ +91 6003617978 ~$\cdot$~
    \href{mailto:daisyphukan6004@gmail.com}{\raisebox{-0.2\height}\faEnvelope\ daisyphukan6004@gmail.com} ~$\cdot$~
    \href{https://linkedin.com/in/daisy-phukan-a401a4228}{\raisebox{-0.2\height}\faLinkedin\ linkedin.com/in/daisy-phukan} ~$\cdot$~
    \href{https://github.com/Daizy-Mgmt}{\raisebox{-0.2\height}\faGithub\ github.com/Daizy-Mgmt} ~$\cdot$~
    \raisebox{-0.1\height}\faMapMarkerAlt\ Bengaluru, India
    \vspace{-7pt}
\end{center}

%-----------SUMMARY-----------
\section{Professional Summary}
 \begin{itemize}[leftmargin=0.0in, label={}]
    \footnotesize{\item{
    Foundational technical operations member at \textbf{Agile Robots SE} (Munich-based Physical AI unicorn) establishing the India entity from the ground up (0-to-1 market entry). Shipped the official \textbf{Franka Robotics India enterprise platform}, engineered customer ROI calculators and pricing frameworks enabling \textbf{€6M+ qualified pipeline (€2M+ closed contracts)} across 30+ CXO evaluations, and coordinated cross-border Agile sprint delivery between Munich R\&D and Bengaluru engineering.
    }}
 \end{itemize}
 \vspace{-12pt}

%-----------CORE SKILLS-----------
\section{Core Skills \& Technical Competencies}
  \begin{itemize}[leftmargin=0.0in, label={}, itemsep=1.2pt]
    \footnotesize{\item{\textbf{Product Lifecycle \& Strategy: } PRD/TRD Authoring $\cdot$ User Problem Discovery $\cdot$ Feature Prioritization (RICE) $\cdot$ Agile / Scrum $\cdot$ Cross-Border Sprint Delivery $\cdot$ Jira $\cdot$ Confluence $\cdot$ Critical Path Management $\cdot$ Risk Registers}}
    \footnotesize{\item{\textbf{Product Analytics \& Experimentation: } Funnel Drop-Off Optimization $\cdot$ Cohort Retention Analysis $\cdot$ Customer ROI Modeling $\cdot$ CapEx vs. OpEx Analysis $\cdot$ Unit Economics $\cdot$ What-If / Sensitivity Modeling $\cdot$ A/B Testing Principles}}
    \footnotesize{\item{\textbf{Technical \& Systems: } Hardware-Software Integration $\cdot$ Robotics Feasibility $\cdot$ Automation Systems Architecture $\cdot$ Web Platform Delivery $\cdot$ Python (pandas, NumPy) $\cdot$ SQL (PostgreSQL, Star Schema)}}
    \footnotesize{\item{\textbf{Telemetry \& Tools: } Power BI (Pipeline \& Sprint Telemetry) $\cdot$ Advanced Excel (DCF, Tornado Charts) $\cdot$ Product Telemetry $\cdot$ HubSpot CRM $\cdot$ Docker $\cdot$ Git/GitHub}}
  \end{itemize}
  \vspace{-12pt}

%-----------EXPERIENCE-----------
\section{Professional Experience}
  \resumeSubHeadingListStart

    \resumeSubheading
      {Agile Robots SE (Munich-based Physical AI \& Robotics Unicorn)}{Nov 2025 -- Present}
      {Technical Project Manager -- Trainee (Core Launch Team, India Market Entry)}{Bengaluru, India}
      \resumeItemListStart
        \resumeItem{Joined as foundational technical operations member establishing the India entity from scratch (\textbf{0-to-1 market entry}), bridging Munich R\&D engineering with Indian enterprise commercial deployment.}
        \resumeItem{Led end-to-end digital product delivery and production launch of the official \textbf{Franka Robotics India enterprise platform}; authored PRDs/TRDs, aligned Munich stakeholders with local engineering, and managed Agile web sprints through QA/UAT.}
        \resumeItem{Engineered standardized Franka cobot unit-economics frameworks, GTM pricing models, and CapEx-vs-labor ROI calculators deployed across 30+ CXO evaluations, directly enabling commercial leadership to qualify \textbf{€6M+ pipeline} and convert \textbf{€2M+ in closed contracts}.}
        \resumeItem{Conducted qualitative user discovery and technical feasibility scoping across \textbf{30+ enterprise accounts}, synthesizing factory-floor kinematic bottlenecks into PRDs and prioritizing POC feature backlogs using RICE frameworks.}
        \resumeItem{Orchestrated cross-border Agile delivery between Munich R\&D and Bengaluru engineering in Jira/Confluence, managing hardware-software dependency risk logs and cutting cross-timezone coordination turnaround by \textbf{$\sim$40\%}.}
      \resumeItemListEnd

    \resumeSubheading
      {NoBroker}{Sept 2025 -- Nov 2025}
      {Client Advisor}{Bengaluru, India}
      \resumeItemListStart
        \resumeItem{Conducted \textbf{42+ consultative client discovery sessions monthly}, analyzing customer friction points to optimize funnel conversion by \textbf{25\%} and generating \textbf{Rs.\,1.25L+ revenue} within 2 months.}
      \resumeItemListEnd

  \resumeSubHeadingListEnd
\vspace{-11pt}

%-----------PROJECTS-----------
\section{Featured Technical \& Product Projects}
    \resumeSubHeadingListStart
      \resumeProjectHeading
          {Industrial Automation CapEx \& Robot Cell Payback Simulator}{Python, Streamlit, Sensitivity Modeling, Plotly}
          {\href{https://industrial-robot-capex-simulator-daisy-phukan.streamlit.app/}{\faExternalLinkAlt\ Live Demo} ~$|$~ \href{https://github.com/Daizy-Mgmt/industrial-robot-capex-simulator}{\faGithub\ GitHub} ~$|$~ 2026}
          \resumeItemListStart
            \resumeItem{\textbf{Situation \& Task:} Built an executive decision-support and financial modeling platform to evaluate collaborative robot cell investments against multi-shift manual assembly lines across industrial manufacturing scenarios.}
            \resumeItem{\textbf{Action:} Modeled discounted cash flow (DCF), labor-arbitrage depreciation, throughput gains, and scrap-rate variance; engineered an interactive Streamlit simulation engine with real-time sensitivity sliders and Tornado charts for risk analysis.}
            \resumeItem{\textbf{Result:} Formulated standardized payback timelines (14.2 months average across 2-shift automotive assembly scenarios) and breakeven thresholds, productizing complex techno-commercial trade-offs for manufacturing decision-makers.}
          \resumeItemListEnd
      \vspace{2pt}
      \resumeProjectHeading
          {Enterprise Logistics SLA Decision Simulator \& Analytics Platform}{Python, Streamlit, PostgreSQL, Plotly}
          {\href{https://daisy-olist-analytics.streamlit.app}{\faExternalLinkAlt\ Live Demo} ~$|$~ \href{https://github.com/Daizy-Mgmt/olist-delivery-satisfaction-analytics}{\faGithub\ GitHub} ~$|$~ 2026}
          \resumeItemListStart
            \resumeItem{\textbf{Situation \& Task:} Designed an operational SLA monitoring and executive decision-support system analyzing \textbf{99.4K marketplace fulfillment events (\$13.6M GMV)} to model supply-chain penalty thresholds.}
            \resumeItem{\textbf{Action:} Modeled a 3-layer PostgreSQL analytical schema, engineered an interactive Streamlit simulation engine with cohort delivery analysis and funnel drop-off metrics, and built dynamic breakeven sensitivity models across 14 reconciled KPI measures.}
            \resumeItem{\textbf{Result:} Isolated an \textbf{8+ day delivery cliff} (ratings drop 4.29$\star$ $\rightarrow$ 1.70$\star$; 79.3\% negative sentiment) and proved \textbf{10\% of fulfillment nodes drive 52.5\% of SLA breaches}, defining critical dispatch intervention thresholds.}
          \resumeItemListEnd
    \resumeSubHeadingListEnd
\vspace{-11pt}

%-----------EDUCATION-----------
\section{Education}
  \resumeSubHeadingListStart
    \resumeSubheading
      {Guru Ghasidas Vishwavidyalaya (Central University)}{Nov 2021 -- May 2025}
      {Bachelor of Technology (B.Tech) in Mechanical Engineering}{Bilaspur, India}
  \resumeSubHeadingListEnd
  \vspace{-13pt}

%-----------LEADERSHIP & HONORS---------------
\section{Leadership \& Honors}
  \begin{itemize}[leftmargin=0.15in, itemsep=2.2pt, parsep=0pt, topsep=1.5pt]
    \resumeItem{\textbf{Student Placement Coordinator} $|$ \textit{Central Training \& Placement Cell, GGU} \hfill \textbf{2024 -- 2025}\\
    Led 4 student coordinator teams managing campus recruitment drives, coordinating corporate outreach and expanding placement invitations by \textbf{20\% year-on-year}.}
    
    \resumeItem{\textbf{AICTE Pragati Scholarship} $|$ \textit{Ministry of Education, Govt. of India} \hfill \textbf{2021 -- 2025}\\
    Awarded prestigious national merit scholarship of \textbf{Rs.\,50,000/year} throughout undergraduate studies for academic excellence in technical engineering education.}
    
    \resumeItem{\textbf{JNVST National Scholar} $|$ \textit{Navodaya Vidyalaya Samiti} \hfill \textbf{2014 -- 2021}\\
    Ranked in top merit percentile nationally in Jawahar Navodaya Vidyalaya Selection Test, earning \textbf{7 years of fully funded} competitive residential schooling.}
    
    \resumeItem{\textbf{Community Leadership \& Athletics: }
    \textbf{Women President}, Panidihingia Unnayan Manch (rural welfare NGO, 2022--Present) $\cdot$ Selected as \textbf{National-Level Handball Player} (NVS Samiti) $\cdot$ \textbf{Gold Medalist} in cultural dance competition $\cdot$ Volunteer, Inclusion Movement Community.}
  \end{itemize}
  \vspace{-10pt}
\end{document}
"""

DEFAULT_SHASHWAT_TEX = r"""%-------------------------
% Master Resume - Shashwat Kumar Gautam
% Jake Gutierrez Template (MIT)
%------------------------

\documentclass[letterpaper,10pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\usepackage{fontawesome5}
\usepackage{multicol}
\input{glyphtounicode}

\definecolor{linkblue}{RGB}{11, 87, 208}
\usepackage[colorlinks=true, urlcolor=linkblue, linkcolor=linkblue]{hyperref}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

\addtolength{\oddsidemargin}{-0.60in}
\addtolength{\evensidemargin}{-0.60in}
\addtolength{\textwidth}{1.20in}
\addtolength{\topmargin}{-.70in}
\addtolength{\textheight}{1.42in}

\urlstyle{same}
\raggedbottom
\setlength{\tabcolsep}{0in}

\titleformat{\section}{
  \vspace{-3pt}\scshape\raggedright\small\bfseries
}{}{0em}{}[\color{black}\titlerule \vspace{-3pt}]

\pdfgentounicode=1

\newcommand{\resumeItem}[1]{
  \item\footnotesize{
    {#1 \vspace{-2.5pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2.5pt}\item
    \begin{tabular*}{1.0\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{\footnotesize #1} & \textbf{\footnotesize #2} \\
      \textit{\footnotesize #3} & \textit{\footnotesize #4} \\
    \end{tabular*}\vspace{-5pt}
}

\newcommand{\resumeProjectHeading}[3]{
    \vspace{-2.5pt}\item
    \begin{tabular*}{1.0\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{\footnotesize #1} $|$ \textit{\footnotesize #2} & \footnotesize #3 \\
    \end{tabular*}\vspace{-5pt}
}

\renewcommand\labelitemi{$\vcenter{\hbox{\tiny$\bullet$}}$}
\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.0in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}[leftmargin=0.15in, itemsep=1.5pt, parsep=0pt, topsep=1.5pt]}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-3pt}}

\begin{document}

%----------HEADING----------
\begin{center}
    {\LARGE \scshape Shashwat Kumar Gautam} \\ \vspace{2pt}
    \textbf{\small Software Systems Engineer $|$ Full-Stack \& Cloud Infrastructure $|$ IIIT Allahabad} \\ \vspace{2.5pt}
    \footnotesize \raisebox{-0.1\height}\faPhone\ +91 9999999999 ~$\cdot$~
    \href{mailto:iit2020030@iiita.ac.in}{\raisebox{-0.2\height}\faEnvelope\ iit2020030@iiita.ac.in} ~$\cdot$~
    \href{https://github.com/Shockshwat}{\raisebox{-0.2\height}\faGithub\ github.com/Shockshwat} ~$\cdot$~
    \raisebox{-0.1\height}\faMapMarkerAlt\ Prayagraj / Bengaluru, India
    \vspace{-7pt}
\end{center}

%-----------SUMMARY-----------
\section{Professional Summary}
 \begin{itemize}[leftmargin=0.0in, label={}]
    \footnotesize{\item{
    Software Systems Engineer from \textbf{Indian Institute of Information Technology, Allahabad (IIITA)}. Experienced in full-stack architecture, distributed backend pipelines, performance tuning, and cross-platform desktop/mobile engineering. Proficient in Python, C/C++, JavaScript/TypeScript, SQL, and cloud infrastructure, building low-latency, scalable solutions under demanding latency SLAs.
    }}
 \end{itemize}
 \vspace{-12pt}

%-----------CORE SKILLS-----------
\section{Technical Skills \& Competencies}
  \begin{itemize}[leftmargin=0.0in, label={}, itemsep=1.2pt]
    \footnotesize{\item{\textbf{Languages: } Python $\cdot$ C/C++ $\cdot$ JavaScript / TypeScript $\cdot$ SQL $\cdot$ Bash / Shell Scripting}}
    \footnotesize{\item{\textbf{Frameworks \& Systems: } Node.js $\cdot$ React $\cdot$ FastAPI $\cdot$ Electron $\cdot$ Docker $\cdot$ RESTful APIs $\cdot$ PostgreSQL $\cdot$ Redis}}
    \footnotesize{\item{\textbf{Developer Tools \& DevOps: } Git / GitHub Actions $\cdot$ Linux Kernel \& Systems Programming $\cdot$ CI/CD Pipelines $\cdot$ Postman $\cdot$ Microservices}}
    \footnotesize{\item{\textbf{Core Concepts: } Data Structures \& Algorithms $\cdot$ Distributed Systems $\cdot$ System Design $\cdot$ Object-Oriented Design (OOP)}}
  \end{itemize}
  \vspace{-12pt}

%-----------EXPERIENCE-----------
\section{Professional Experience}
  \resumeSubHeadingListStart
    \resumeSubheading
      {Systems Engineering \& Open Source Development}{2021 -- Present}
      {Software Engineer / Open-Source Contributor}{Remote}
      \resumeItemListStart
        \resumeItem{Architected and released multiple open-source utilities and system tools in C++ and Python with 1,000+ active developer downloads.}
        \resumeItem{Engineered automated CI/CD build scripts and packaging workflows across macOS, Windows, and Linux environments.}
        \resumeItem{Optimized low-level memory handling and thread execution pipelines, improving throughput and reducing cold-start latency by \textbf{35\%}.}
      \resumeItemListEnd
  \resumeSubHeadingListEnd
\vspace{-11pt}

%-----------PROJECTS-----------
\section{Featured Technical Projects}
    \resumeSubHeadingListStart
      \resumeProjectHeading
          {AudioSync -- Distributed Real-Time Low-Latency Audio Streaming}{C++, Python, WebSockets, Audio DSP}
          {\href{https://github.com/Shockshwat/AudioSync}{\faGithub\ GitHub} ~$|$~ 2024}
          \resumeItemListStart
            \resumeItem{\textbf{Architecture:} Engineered a cross-device low-latency audio transmission engine synchronizing audio feeds across distributed local network nodes.}
            \resumeItem{\textbf{Performance:} Implemented ring-buffer audio scheduling reducing jitter and network drop-out rates under 15ms buffer latencies.}
          \resumeItemListEnd
      \vspace{2pt}
      \resumeProjectHeading
          {Latex ATS Resume Optimizer \& Portal}{Python, Streamlit, SQLite, LaTeX Compilers}
          {\href{https://github.com/Shockshwat}{\faGithub\ GitHub} ~$|$~ 2026}
          \resumeItemListStart
            \resumeItem{\textbf{Architecture:} Built a full-stack resume tailoring and job-application tracking portal enabling real-time ATS keyword matching and live LaTeX-to-PDF synchronization.}
            \resumeItem{\textbf{Features:} Integrated dual Overleaf-style code and PDF viewer with sub-3s cloud compilation and persistent multi-user database storage.}
          \resumeItemListEnd
    \resumeSubHeadingListEnd
\vspace{-11pt}

%-----------EDUCATION-----------
\section{Education}
  \resumeSubHeadingListStart
    \resumeSubheading
      {Indian Institute of Information Technology, Allahabad (IIITA)}{2020 -- 2024}
      {Bachelor of Technology (B.Tech) in Information Technology}{Prayagraj, India}
  \resumeSubHeadingListEnd
  \vspace{-13pt}

%-----------HONORS & ACHIEVEMENTS---------------
\section{Honors \& Achievements}
  \begin{itemize}[leftmargin=0.15in, itemsep=2.2pt, parsep=0pt, topsep=1.5pt]
    \resumeItem{\textbf{JEE Advanced Merit: } Secured top percentile in Joint Entrance Examination (Advanced), qualifying for elite national engineering institute admission.}
    \resumeItem{\textbf{Competitive Programming: } Active problem solver with 500+ algorithmic problems solved across LeetCode, Codeforces, and CodeChef.}
  \end{itemize}
  \vspace{-10pt}
\end{document}
"""
