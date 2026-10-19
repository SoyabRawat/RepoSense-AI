# RepoSense AI — Product Requirements Document

This document defines the functional and nonfunctional requirements for RepoSense AI across its three top-level phases.

> **Status Notice:** Requirements marked as **Phase 1** are implemented and verified in the current foundation. Requirements marked as **Phase 2** or **Phase 3** represent planned capabilities and are NOT implemented in Phase 1.

---

## 1. Requirement Traceability Matrix

| Identifier | Category | Planned Phase | Status in Phase 1 |
|---|---|---|---|
| **FR-101** | Foundation Scaffolding | Phase 1 | Implemented |
| **FR-102** | Backend Health Endpoint | Phase 1 | Implemented |
| **FR-103** | Frontend Health Display | Phase 1 | Implemented |
| **FR-104** | Modular Configuration | Phase 1 | Implemented |
| **FR-105** | Sanitized Logging | Phase 1 | Implemented |
| **FR-106** | Initial Automated Testing | Phase 1 | Implemented |
| **FR-201** | Public GitHub Repo Ingestion | Phase 2 | Implemented & Tested |
| **FR-202** | Repository Metadata Extraction | Phase 2 | Implemented & Tested |
| **FR-203** | Language & File Breakdown | Phase 2 | Implemented & Tested |
| **FR-204** | Entry-Point Detection | Phase 2 | Implemented & Tested |
| **FR-205** | Import & Dependency Analysis | Phase 2 | Implemented & Tested |
| **FR-206** | Interactive Architecture Graph | Phase 2 | Implemented & Tested |
| **FR-207** | Source-Code Search Engine | Phase 2 | Implemented & Tested |
| **FR-208** | Provider-Agnostic AI Explanations | Phase 2 | Implemented & Tested |
| **FR-209** | Source File & Line Citations | Phase 2 | Implemented & Tested |
| **FR-301** | Comprehensive End-to-End Suite | Phase 3 | Planned (Unimplemented) |
| **FR-302** | Exportable Architecture Diagrams | Phase 3 | Planned (Unimplemented) |
| **FR-303** | Public Release Packaging & Docker | Phase 3 | Planned (Unimplemented) |
| **NFR-101** | Zero Credential Commit | Phase 1 | Enforced |
| **NFR-102** | CORS Restricted Local Origins | Phase 1 | Enforced |
| **NFR-103** | Structured Error Handling | Phase 1 | Implemented |
| **NFR-201** | Untrusted Code Isolation (No Exec) | Phase 2 | Enforced & Tested |
| **NFR-202** | SSRF & Private IP Protection | Phase 2 | Implemented & Tested |
| **NFR-203** | Path Traversal Prevention | Phase 2 | Implemented & Tested |
| **NFR-204** | Resource Limits & Rate Limiting | Phase 2 | Implemented & Tested |
| **NFR-205** | AI Prompt Injection Resistance | Phase 2 | Implemented & Tested |
| **NFR-206** | Offline / AI-Free Operation | Phase 2 | Implemented & Tested |

---

## 2. Functional Requirements

### Phase 1: Foundation & Architecture

- **FR-101: Foundation Scaffolding**
  - *Description:* The codebase must provide a modular monorepo-style structure separating frontend (`frontend/`), backend (`backend/`), and system documentation (`docs/`).
  - *Phase:* Phase 1 (Foundation)

- **FR-102: Backend Health Endpoint**
  - *Description:* The backend API must expose structured health endpoints (`/health` and `/api/v1/health`) returning application name, semantic version, active development phase, environment name, and an explicit capability readiness map.
  - *Phase:* Phase 1 (Foundation)

- **FR-103: Frontend Health Display**
  - *Description:* The frontend landing page must connect to the backend health endpoint and render distinct UI states for Loading, Connected, and Connection Failure (with retry capabilities).
  - *Phase:* Phase 1 (Foundation)

- **FR-104: Modular Configuration**
  - *Description:* Application settings must be managed through strongly typed environment configurations (Pydantic Settings) with safe local defaults and `.env.example` guidance.
  - *Phase:* Phase 1 (Foundation)

- **FR-105: Sanitized Logging**
  - *Description:* Backend logging must be initialized with format standards and an automated filter to redact potential sensitive tokens, keys, and authorization data.
  - *Phase:* Phase 1 (Foundation)

- **FR-106: Initial Automated Testing**
  - *Description:* Automated unit and integration tests must verify backend startup, configuration loading, error responses, and frontend component rendering.
  - *Phase:* Phase 1 (Foundation)

---

### Phase 2: Core Development (Implemented & Tested)

- **FR-201: Public GitHub Repository Ingestion**
  - *Description:* Accept a validated public GitHub repository URL, verify its existence via GitHub API or shallow clone, and isolate it in a temporary ephemeral sandbox.
  - *Phase:* Phase 2 (Core)

- **FR-202: Repository Metadata Extraction**
  - *Description:* Retrieve star count, license, default branch, latest commit hash, contributor count, and description.
  - *Phase:* Phase 2 (Core)

- **FR-203: Language & File Breakdown**
  - *Description:* Inventory all files, categorize by file extension and byte count, and compute language distribution percentages.
  - *Phase:* Phase 2 (Core)

- **FR-204: Entry-Point Detection**
  - *Description:* Automatically detect common application entry points (e.g., `main.py`, `index.ts`, `app.tsx`, `main.go`, `src/index.js`, `Cargo.toml` bins).
  - *Phase:* Phase 2 (Core)

- **FR-205: Import & Dependency Analysis**
  - *Description:* Parse source files into ASTs to extract module import relationships and package dependencies without executing repository code.
  - *Phase:* Phase 2 (Core)

- **FR-206: Interactive Architecture Graph**
  - *Description:* Generate node-link graph data representing modules and relationships, rendered interactively using React Flow.
  - *Phase:* Phase 2 (Core)

- **FR-207: Source-Code Search Engine**
  - *Description:* Index repository files to support fast substring, regex, and symbol search across the codebase.
  - *Phase:* Phase 2 (Core)

- **FR-208: Provider-Agnostic AI Explanations**
  - *Description:* Provide an abstract AI service interface capable of querying LLMs (e.g., OpenAI, Anthropic, Gemini, Ollama) with contextual code snippets.
  - *Phase:* Phase 2 (Core)

- **FR-209: Source File & Line Citations**
  - *Description:* Every factual statement in an AI explanation must be accompanied by verified file path links and line number ranges.
  - *Phase:* Phase 2 (Core)

---

### Phase 3: Testing & Public Release (Planned)

- **FR-301: Comprehensive End-to-End Suite**
  - *Description:* Full automated E2E test coverage testing repository ingestion, graph generation, search indexing, and citation accuracy.
  - *Phase:* Phase 3 (Release)

- **FR-302: Exportable Architecture Diagrams**
  - *Description:* Allow users to export architecture graphs as SVG, PNG, or Mermaid markdown snippets.
  - *Phase:* Phase 3 (Release)

- **FR-303: Public Release Packaging & Docker**
  - *Description:* Containerize frontend and backend into production-grade multi-stage Docker images with `docker-compose.yml`.
  - *Phase:* Phase 3 (Release)

---

## 3. Nonfunctional Requirements

- **NFR-101: Zero Credential Commit**
  - *Standard:* No private API keys, tokens, or credentials may be stored in code or git history. Enforced via `.gitignore` and static inspections.
  - *Phase:* Phase 1 (Foundation)

- **NFR-102: CORS Restricted Local Origins**
  - *Standard:* Development CORS policy must strictly restrict cross-origin requests to configured local development URLs (e.g., `http://localhost:5173`). Wildcard `*` with credentials is prohibited.
  - *Phase:* Phase 1 (Foundation)

- **NFR-103: Structured Error Handling**
  - *Standard:* All API errors (4xx, 5xx) must return consistent JSON payloads matching `ErrorResponse` schema with error message, code, and safe metadata.
  - *Phase:* Phase 1 (Foundation)

- **NFR-201: Untrusted Code Isolation (No Exec)**
  - *Standard:* Under no circumstances shall the application run, build, or execute untrusted code from analyzed repositories. Analysis must be strictly passive AST/text parsing.
  - *Phase:* Phase 2 (Core)

- **NFR-202: SSRF & Private IP Protection**
  - *Standard:* Repository ingestion routines must validate URLs to ensure they only resolve to public GitHub hostnames (`github.com`) and block loopback (`127.0.0.1`), LAN IPs (`10.0.0.0/8`, `192.168.0.0/16`), and cloud metadata services (`169.254.169.254`).
  - *Phase:* Phase 2 (Core)

- **NFR-203: Path Traversal Prevention**
  - *Standard:* File paths extracted from repository archives or trees must be validated using path normalization to prevent directory traversal (`../`) attacks outside the sandbox root.
  - *Phase:* Phase 2 (Core)

- **NFR-204: Resource Limits & Rate Limiting**
  - *Standard:* Set strict ingestion bounds: maximum repository size (default: 50MB), maximum file count (default: 5,000 files), maximum single file size (default: 1MB), and analysis timeout (default: 60s).
  - *Phase:* Phase 2 (Core)

- **NFR-205: AI Prompt Injection Resistance**
  - *Standard:* Content extracted from repository source files, comments, and READMEs must be treated as untrusted data and strictly isolated from system prompts via delimited data blocks.
  - *Phase:* Phase 2 (Core)

- **NFR-206: Offline / AI-Free Operation**
  - *Standard:* The core repository overview, AST dependency graph, and code search features must operate completely without an AI API key or network access to third-party LLM providers.
  - *Phase:* Phase 2 (Core)
