# RepoSense AI — Project Roadmap

This roadmap governs the entire lifecycle of RepoSense AI across **exactly three top-level development phases**.

---

## Strict Development Phases

```
+-----------------------------------+
|  PHASE 1: Foundation & Arch       |  [COMPLETED]
|  (Scaffolding, Docs, Health API)  |
+-----------------+-----------------+
                  |
                  v
+-----------------+-----------------+
|  PHASE 2: Core Development        |  [COMPLETED]
|  (Ingestion, AST, Graphs, Search) |
+-----------------+-----------------+
                  |
                  v
+-----------------+-----------------+
|  PHASE 3: Testing & Release       |  [COMPLETED - RELEASE CANDIDATE]
|  (E2E Tests, Hardening, Docker)   |
+-----------------------------------+
```

---

## Phase 1 — Foundation & Architecture
**Status:** Completed

### 1.1 Scope & Deliverables
- Requirements analysis, architectural modeling, and security boundary definition.
- Repository structure and development environment verification.
- Scaffolding of React 19 + TypeScript + Vite frontend and FastAPI backend.
- Implementation and verification of structured system health checks and connectivity.
- Configuration management with safe defaults, sanitized logging, and initial test harnesses.

---

## Phase 2 — Core Development
**Status:** Completed

### 2.1 Scope & Deliverables
- Public GitHub repository URL validation with SSRF protection and sandboxed retrieval.
- Repository metadata extraction via GitHub REST API (owner, name, stars, forks, commit SHA, license).
- Hierarchical file tree inventory and language breakdown percentages.
- Static AST and token parsing for Python, TypeScript, JavaScript, Java, C/C++, Go, and Rust.
- Application entry-point identification with confidence ratings and verifiable evidence.
- Interactive architecture graph generation rendered with React Flow (`@xyflow/react`).
- Full-text source-code keyword and phrase search indexing.
- Provider-agnostic AI explanation adapter (Gemini, OpenAI, Ollama, and offline NullProvider).
- Grounded citations linking AI responses to verified file paths and line ranges.
- Full React 19 frontend tabbed workspace (Overview, Explorer, Graph, Search, Ask AI).

---

## Phase 3 — Testing, Security, Performance & Public Release
**Status:** Completed (Release Candidate v0.3.0 Ready for Public Release)

### 3.1 Scope & Deliverables
- Comprehensive automated test suite expansion:
  - Backend: 49 tests passing ($100\%$ pass rate) covering URL validation, SSRF defenses, path traversal, resource limits, empty repo handling, rate limit handling, search, AST resolution, AI providers, performance benchmarks, and citation checks.
  - Frontend: 33 tests passing ($100\%$ pass rate across 10 component and integration suites) covering workspace views, file explorer, source viewer, code search, graph canvas, error recovery, and end-to-end user workflows.
- Security hardening and verification:
  - SSRF protection tested across loopback, private IPv4/IPv6, and cloud metadata targets.
  - Path traversal protections hardened against `../`, `..\\`, Windows drives (`C:`), URL-encoded paths (`%2e%2e`), and NULL bytes.
  - Resource bounds actively enforced on trees, file sizes, and memory usage.
  - Safe source-code rendering without HTML/script execution.
- Performance profiling and optimization:
  - Frontend production bundle optimized with Rollup manual vendor chunking (`vendor-react`, `vendor-xyflow`, `vendor-highlight`, `vendor-icons`), reducing main bundle size from 1.39MB to 65kB and building in under 2 seconds.
  - Idiomatic React state management eliminating cascading synchronous renders in effects.
  - Runtime TypeError protection in code search result context mapping.
- Production deployment preparation:
  - Multi-stage non-root `backend/Dockerfile` with healthcheck.
  - Multi-stage `frontend/Dockerfile` with Nginx SPA routing and gzip compression.
  - Unified `docker-compose.yml` for single-command deployment.
  - GitHub Actions CI workflow (`.github/workflows/ci.yml`).
  - GitHub Pull Request template (`.github/PULL_REQUEST_TEMPLATE.md`).
- Documentation completion:
  - Updated `README.md`, `ARCHITECTURE.md`, `SECURITY.md`, `CONTRIBUTING.md`, and `.env.example`.
  - Open-source readiness checklist complete.

---

## Post-Release Maintenance Guidelines
Following the completion of Phase 3, no additional top-level development phases (e.g. "Phase 4") will be created. Subsequent work will be conducted via standard open-source maintenance:
- Community bug fixes and security patch releases.
- Additional language parser heuristics (e.g. Ruby, Kotlin, Swift).
- User interface accessibility enhancements.
