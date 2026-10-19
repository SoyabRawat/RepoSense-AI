# Contributing to RepoSense AI

Thank you for your interest in contributing to RepoSense AI! This document outlines guidelines for setting up your local environment, writing code, running tests, and submitting contributions.

---

## 1. Project Overview & Phase Boundaries

RepoSense AI has completed its 3 planned development phases:
- **Phase 1:** Foundation, Architecture & Health Connectivity.
- **Phase 2:** Core Repository Ingestion, AST Parsing, Dependency Graphs, Code Search, and Grounded AI Q&A.
- **Phase 3:** Testing, Security Hardening, Performance Optimization & Public Release Preparation.

Contributions should focus on bug fixes, performance enhancements, additional language extractors, security hardening, and documentation improvements.

---

## 2. Prerequisites

Ensure you have the following installed:
- **Git** (>= 2.30)
- **Node.js** (>= 18.0, Node 22+ recommended) & **npm** (>= 9.0)
- **Python** (>= 3.11, tested on 3.11, 3.12, and 3.14)
- **Docker** (optional, for containerized testing)

---

## 3. Local Development Setup

### 3.1 Clone the Repository
```bash
git clone https://github.com/your-username/RepoSense-AI.git
cd RepoSense-AI
cp .env.example .env
```

### 3.2 Backend Setup
```bash
# Create and activate Python virtual environment
python -m venv backend/.venv

# Windows (PowerShell)
backend\.venv\Scripts\Activate.ps1

# Linux / macOS
source backend/.venv/bin/activate

# Install backend in editable mode with development dependencies
pip install -e backend/
pip install pytest anyio httpx

# Start the development server
uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```
Verify backend health: `curl http://127.0.0.1:8000/api/v1/health`

### 3.3 Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open [http://127.0.0.1:5173](http://127.0.0.1:5173) in your browser.

---

## 4. Running Automated Tests & Quality Checks

### 4.1 Backend Tests
```bash
# Run complete backend pytest suite
pytest -v backend/tests
```
All 49 backend tests must pass.

### 4.2 Frontend Tests
From the `frontend/` directory:
```bash
# Run Vitest component tests
npm run test:run
```
All 33 frontend tests must pass.

### 4.3 Frontend Linting
```bash
npm run lint
```
Must pass with 0 warnings and 0 errors.

### 4.4 Production Build Verification
```bash
npm run build
```
Must compile cleanly without errors.

---

## 5. Development Guidelines & Code Standards

- **Type Safety:** Full type annotations required in Python (Pydantic v2 schemas). Strict TypeScript in frontend.
- **Security:**
  - Never commit real secrets, API keys, or personal tokens.
  - All repository content is untrusted data: never use `eval()`, `exec()`, or execute repository files.
  - Preserve SSRF and path traversal safeguards.
- **Architecture Integrity:** Keep endpoints thin; place business logic in modular services under `backend/app/services/` and `frontend/src/services/`.
- **Error Handling:** Backend errors must return structured JSON conforming to `ErrorResponse`.

---

## 6. How to Report Bugs

1. Search existing issues to avoid duplicates.
2. File a new issue using the **Bug Report** template.
3. Provide your operating system, Python version, Node.js version, exact error messages, and reproduction steps.
4. *For security vulnerabilities, please refer to [SECURITY.md](SECURITY.md) for private reporting procedures.*

---

## 7. Submitting Changes

1. Create a descriptive feature branch:
   ```bash
   git checkout -b fix/issue-description
   ```
2. Make your changes adhering to code style, type safety, and architectural boundaries.
3. Ensure backend tests (`pytest`), frontend tests (`vitest`), linter (`oxlint`), and build (`npm run build`) all pass.
4. Submit a Pull Request following our [PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md).
