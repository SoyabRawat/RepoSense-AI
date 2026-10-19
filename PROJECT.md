# RepoSense AI — Project Definition & Vision

## 1. Executive Summary

**RepoSense AI** is an open-source developer tool designed to dramatically shorten the time it takes engineers, reviewers, and open-source contributors to understand unfamiliar codebases. By synthesizing static repository analysis, dependency graphs, entry-point detection, and grounded AI explanations, RepoSense AI transforms complex repositories into navigable, transparent, and approachable software maps.

---

## 2. Problem Statement

Modern software engineers frequently encounter unfamiliar repositories:
- **Onboarding friction:** New hires and team transfers spend weeks tracing code execution paths, build pipelines, and undocumented conventions.
- **Open-source contribution barriers:** External contributors struggle to locate entry points, understand module boundaries, or identify which files implement a given feature.
- **Dependency opacity:** Complex import chains and circular dependencies obscure how components communicate.
- **AI hallucination risks:** Generic AI chatbots lack complete codebase context and frequently invent non-existent functions, outdated signatures, or incorrect file paths.

---

## 3. Product Vision & Value Proposition

RepoSense AI delivers:
1. **Instant Structural Clarity:** Automated file inventory, language breakdown, and directory layout.
2. **Deterministic Architecture Mapping:** Direct AST and import analysis generating verifiable dependency graphs.
3. **Source-Grounded AI Explanations:** Explanations that cite exact file paths and line ranges, ensuring transparency and trust.
4. **Developer-First Design:** Zero vendor lock-in, open-source architecture, and modular backends where AI assistance is optional rather than a prerequisite.

---

## 4. Target Users & Personas

### 4.1 Persona 1: Alex — The Onboarding Software Engineer
- **Background:** Mid-level full-stack engineer joining a new organization.
- **Need:** Understand a 50,000-line monolith with minimal documentation.
- **Goal:** Identify the primary request lifecycle, detect where routes are registered, and trace database migrations.

### 4.2 Persona 2: Priya — The Open-Source Contributor
- **Background:** Independent developer seeking to contribute a bugfix to a popular library.
- **Need:** Find where specific CLI commands are parsed without reading every file.
- **Goal:** Get a high-level module map and find the relevant source file within 5 minutes.

### 4.3 Persona 3: Marcus — The Security / Code Reviewer
- **Background:** Security engineer performing an initial audit of a third-party open-source dependency.
- **Need:** Review external dependencies, entry points, and trust boundaries without executing untrusted code.
- **Goal:** Inspect dependency fan-out and unvetted imports quickly and safely.

---

## 5. Main Use Cases

1. **Repository Exploration:** Submit a public GitHub repository URL to receive a high-level summary, language breakdown, and entry point suggestions.
2. **Dependency & Architecture Visualization:** Inspect an interactive node-link graph of modules and import relationships.
3. **Source-Grounded Question Answering:** Ask architectural questions (e.g., *"How is authentication middleware injected?"*) and receive answers with verifiable file and line references.
4. **Offline / Self-Hosted Analysis:** Run static analysis locally without sending proprietary code to commercial AI APIs if desired.

---

## 6. Product Principles

1. **Static Analysis Precedes AI:** Factual relationships (imports, file structures, language distributions) must be derived from verifiable static analysis, never guessed by an LLM.
2. **Never Execute Untrusted Code:** All repository inspection is purely passive analysis of text and abstract syntax trees. No repository scripts, tests, or build commands are executed.
3. **Strict Source Grounding:** AI responses must link to real files and line numbers. Statements without citations are flagged as speculative.
4. **Modular & Provider-Agnostic:** Support multiple LLM backends (OpenAI, Anthropic, Gemini, local Ollama) or none at all.
5. **Radical Transparency:** The application never feigns analysis completion; status, limits, and errors are clearly communicated.

---

## 7. Scope & Non-Goals

### In Scope
- Static analysis of public GitHub repositories.
- AST parsing for major languages (Python, TypeScript, JavaScript, Go, Rust planned for Phase 2).
- Module import graph construction and visualization.
- Semantic and keyword code search.
- Optional LLM-assisted code explanations with citations.
- Self-hostable via standard local tooling (Docker planned).

### Non-Goals
- **Code Execution:** RepoSense AI will not run, test, or build repository code.
- **Dynamic Profiling / Runtime Tracing:** No memory profiling or runtime execution monitoring.
- **Automated Refactoring / PR Generation:** RepoSense AI focuses strictly on comprehension, not automated code writing.
- **Private Intranet Repository Cloning (in Phase 1/2):** Initial focus is exclusively on public GitHub repositories with strict SSRF protections.

---

## 8. Target Success Metrics

*Note: These are measurable target criteria for evaluating Phase 2 and Phase 3 implementations; they are not fabricated historical measurements.*

1. **Analysis Success Rate:** $\ge 95\%$ of supported public repositories under 50MB analyzed without error.
2. **Citation Verifiability:** $100\%$ of AI-generated file citations resolve to existing files and line ranges in the target commit.
3. **Time to First Overview:** Initial directory inventory and language breakdown rendered in $\le 5$ seconds for typical repositories.
4. **Reproducible Setup:** A new developer can clone and run both frontend and backend locally in under 5 minutes following documented instructions.
