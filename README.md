# RepoSense AI

> **An open-source developer tool for rapidly understanding, visualizing, and exploring unfamiliar public GitHub repositories.**

[![Development Phase](https://img.shields.io/badge/Phase-3%20Testing%2C%20Security%20%26%20Release-indigo.svg)](#3-current-development-status)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B%20%7C%203.14-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/Frontend-React%2019%20%2B%20Vite%208-61dafb.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%200.115-009688.svg)](https://fastapi.tiangolo.com/)
[![CI Status](https://img.shields.io/badge/CI-Passing-brightgreen.svg)](#8-automated-testing-and-verification)

---

## 1. Problem Statement

Developers frequently encounter unfamiliar codebases:
- **Onboarding friction:** Engineers spend hours or days manually tracing file hierarchies, entry points, and module boundaries.
- **Dependency opacity:** Complex import relationships and hidden architectural coupling make system comprehension tedious and error-prone.
- **Unverified AI explanations:** Generic AI chat tools lack complete repository grounding, leading to hallucinations about file paths, function signatures, and execution lifecycles.

---

## 2. Proposed Solution

**RepoSense AI** combines static code analysis, abstract syntax tree (AST) parsing, interactive dependency graph visualization, full-text code search, and source-grounded AI explanations. It transforms complex repositories into clear, verifiable architectural maps where every explanation is validated against real source files, lines, and Git commit revisions.

---

## 3. Current Development Status

> **Development Phase:** RepoSense AI has completed **Phase 3: Testing, Security, Performance & Public Release**.
>
> In Phase 3, the entire application has been hardened, optimized, tested across backend and frontend layers, documented, containerized with multi-stage Docker configurations, and prepared for public open-source release:
> - **Backend Test Coverage:** 49 automated tests passing ($100\%$ pass rate) covering ingestion, URL validation, SSRF prevention, path traversal defense, resource bounds, AST resolution, AI providers, performance benchmarks, and citation validation.
> - **Frontend Test Coverage:** 33 automated tests passing ($100\%$ pass rate across 10 component and integration suites) covering all views, search interactions, AI Q&A flows, error recovery, and file exploration.
> - **Code Quality:** Zero ESLint / Oxlint warnings across all frontend files.
> - **Production Optimization:** Code-split bundle with vendor chunking (React, React Flow, Highlight.js, Lucide) building in <2 seconds.
> - **Deployment Readiness:** Production multi-stage Dockerfiles (non-root execution) and unified `docker-compose.yml` for self-hosted deployment.
> - **CI/CD Automation:** GitHub Actions CI workflow covering tests, linting, and production builds.

---

## 4. Architecture & Technology Stack

```
   ┌──────────────────────────────────────────────────────────────┐
   │         Frontend: React 19 + TypeScript + Vite 8             │
   │  (React Flow Graph, Highlight.js Viewer, Full-Text Search)   │
   └──────────────────────────────┬───────────────────────────────┘
                                  │ HTTP / JSON REST APIs
                                  ▼
   ┌──────────────────────────────────────────────────────────────┐
   │              Backend: FastAPI + Python >= 3.11               │
   │  (Pydantic v2, AST Static Parsers, In-Memory Revision Store) │
   └──────────────┬───────────────────────────────┬───────────────┘
                  │                               │
                  ▼                               ▼
   ┌──────────────────────────────┐ ┌─────────────────────────────┐
   │      GitHub REST API         │ │    Configurable AI Layer    │
   │  (Trees, Blobs, Commits)     │ │  (Offline Mode / Cloud AI)  │
   └──────────────────────────────┘ └─────────────────────────────┘
```

### Technology Stack
- **Frontend:** React 19, TypeScript, Vite 8, Tailwind CSS v4, `@xyflow/react` (React Flow), Highlight.js, Lucide React, Vitest, Testing Library.
- **Backend:** FastAPI, Python (tested on 3.11, 3.12, 3.14), Uvicorn, Pydantic v2, Pydantic Settings, HTTPX, Pytest, AnyIO.
- **Containerization:** Docker (multi-stage non-root) & Docker Compose.
- **CI/CD:** GitHub Actions.

---

## 5. Core Implemented Features

1. **Public GitHub Ingestion & Sandboxing:** Validates URLs, blocks private IP / SSRF targets, enforces resource limits (5,000 files, 25MB total source, 1MB per file), and resolves canonical commit revisions.
2. **File Explorer:** Interactive tree view with folder navigation, entry-point badges, language tags, and instant name filtering.
3. **Source Code Viewer:** Monospace line-numbered viewer with syntax highlighting, copy-to-clipboard, and direct GitHub links.
4. **Language Breakdown:** Computes file count and exact byte percentages across all examined source code.
5. **Entry-Point Detection:** Heuristic and AST-based detection of main execution points for Python, JavaScript, TypeScript, Java, and C/C++.
6. **Static Dependency & Import Analysis:** Extracts relative imports, package dependencies, and manifest declarations (`package.json`, `requirements.txt`, `pyproject.toml`).
7. **Interactive Architecture Graph:** Visual node-link diagram with node filtering (Entry Points, Modules, Packages), search, pan, zoom, and inspection drawer.
8. **Code Search:** Fast full-text keyword search across repository contents with line numbers and context snippets.
9. **Source-Grounded AI Explanations:** Explain unfamiliar codebases in Beginner or Developer mode.
10. **Verified Source Citations:** AI explanations cite specific file paths and line ranges, validated against actual repository contents.
11. **Deterministic AI-Free Mode:** Fully functional without any AI API keys using deterministic static facts.

---

## 6. Supported Programming Languages

| Language / Manifest | Import & Dependency Extraction | Entry Point Detection | Syntax Highlighting |
|---|---|---|---|
| **Python** (`.py`) | Python `ast` AST parsing | `if __name__ == '__main__'`, `main()`, `cli()` | Yes |
| **JavaScript / TypeScript** (`.js`, `.jsx`, `.ts`, `.tsx`) | ES6 `import`, `export`, CommonJS `require()` | `package.json` `main`/`bin`, `index.ts`, `app.tsx` | Yes |
| **Java** (`.java`) | Package declarations, imports | `public static void main` | Yes |
| **C / C++** (`.c`, `.cpp`, `.h`, `.hpp`) | `#include` directives | `int main(` | Yes |
| **Go** (`.go`) | Package imports | `func main()` in `package main` | Yes |
| **Rust** (`.rs`) | Module dependencies | `fn main()` | Yes |
| **Manifests** (`package.json`, `requirements.txt`, `pyproject.toml`) | Direct dependency declarations | Configured entry scripts | Yes |

*Note: Monorepos and unsupported syntax fall back gracefully to directory and file viewing without breaking the application.*

---

## 7. Installation & Quickstart

### Option A: Local Development Setup

#### Prerequisites
- **Python:** Version >= 3.11 (Python 3.14 tested)
- **Node.js:** Version >= 18.0 (Node v22 / v24 tested)
- **Git**

#### 1. Clone and Configure
```bash
git clone https://github.com/your-username/RepoSense-AI.git
cd RepoSense-AI
cp .env.example .env
```

#### 2. Start the Backend
```bash
# Set up Python virtual environment
python -m venv backend/.venv

# Windows (PowerShell)
backend\.venv\Scripts\Activate.ps1

# Linux / macOS
source backend/.venv/bin/activate

# Install dependencies in editable mode
pip install -e backend/

# Run FastAPI development server
uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```
Verify backend health: `curl http://127.0.0.1:8000/api/v1/health`

#### 3. Start the Frontend
In another terminal:
```bash
cd frontend
npm install
npm run dev
```
Open [http://127.0.0.1:5173](http://127.0.0.1:5173) in your browser.

---

### Option B: Docker Compose (Single Command)

```bash
# Build and start all services
docker compose up -d

# Verify health status
docker compose ps
```
- Frontend UI: [http://localhost:3000](http://localhost:3000)
- Backend API: [http://localhost:8000](http://localhost:8000)
- API Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 8. Automated Testing and Verification

### Backend Pytest Suite
```bash
# Windows
backend\.venv\Scripts\pytest -v backend/tests

# Linux / macOS
pytest -v backend/tests
```
**Status:** 49 passed, 0 failed ($100\%$ pass rate).

### Frontend Vitest Suite
```bash
cd frontend
npm run test:run
```
**Status:** 33 passed across 10 suites, 0 failed ($100\%$ pass rate).

### Frontend Linter (oxlint)
```bash
cd frontend
npm run lint
```
**Status:** 0 warnings, 0 errors.

### Production Bundle Build
```bash
cd frontend
npm run build
```
**Status:** 0 warnings, built in <2.0 seconds with vendor chunk separation.

---

## 9. Security & Trust Architecture

RepoSense AI treats all analyzed repository contents as **untrusted input**:
- **Zero Command Execution:** Repository code is parsed strictly as passive text. No build scripts, tests, or package installers are ever executed.
- **SSRF Defenses:** Blocks private networks (`10.0.0.0/8`, `192.168.0.0/16`, `127.0.0.0/8`, `::1`), loopback targets, cloud metadata endpoints (`169.254.169.254`, `metadata.google.internal`), custom ports, and non-HTTPS protocols.
- **Path Traversal Protection:** Every file path is validated against traversal (`../`), Windows drive paths (`C:`), URL-encoded sequences (`%2e%2e`), null bytes, and path length bounds.
- **Resource Limits:** Server-side limits on tree size (5,000 entries), file count (600 files), single file size (1MB), total source size (25MB), and request timeouts (30s).
- **Prompt Injection Defense:** Source code snippets passed to AI models are wrapped inside explicit untrusted delimiter boundaries.
- **Citation Verification:** All model-generated citations are checked against genuine file paths and line ranges; non-existent citations are dropped.
- **Secret Redaction:** Active logging filter (`SensitiveDataFilter`) prevents credentials and tokens from leaking into logs.

For vulnerability reporting, see [SECURITY.md](SECURITY.md).

---

## 10. Contributing

We welcome contributions from the open-source community!
- Review [CONTRIBUTING.md](CONTRIBUTING.md) for local setup, commit conventions, and pull request guidelines.
- Use our [Issue Templates](.github/ISSUE_TEMPLATE/) to report bugs or request features.
- Ensure all tests pass before submitting a pull request.

---

## 11. License

This project is licensed under the [MIT License](LICENSE).
