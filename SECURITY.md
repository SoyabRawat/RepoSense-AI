# RepoSense AI — Security Policy & Trust Model

## 1. Security Philosophy: The Untrusted Code Boundary

RepoSense AI is designed to inspect arbitrary, third-party source code repositories. **All repository content—including file names, directory trees, source code, comments, documentation, and configuration files—must be treated as untrusted and potentially adversarial input.**

The primary defensive objective is to provide deep repository understanding **without ever compromising the host system running RepoSense AI, executing untrusted instructions, or exposing internal network services**.

---

## 2. Threat Modeling & Verified Mitigations

| Threat Vector | Severity | Mitigation Strategy | Implementation | Status |
|---|---|---|---|---|
| **Arbitrary Code Execution** | Critical | Passive text/AST parsing only; zero command execution | `static_analysis.py`, `entry_point_detection.py` | **VERIFIED** |
| **Server-Side Request Forgery (SSRF)** | Critical | Strict URL scheme/host whitelist, CIDR blocklist, metadata blocking | `github_url.py:parse_and_validate_github_url` | **VERIFIED** |
| **Path Traversal (`../`, `C:\`, `%2e%2e`)** | High | Comprehensive path sanitizer on trees and API lookups | `github_ingestion.py:validate_path_safety` | **VERIFIED** |
| **Resource Exhaustion (DoS)** | High | Server-side bounds on tree entries, file counts, file sizes, timeouts | `Settings` in `config.py`, `github_ingestion.py` | **VERIFIED** |
| **Credential & Secret Leakage** | High | Active logging filter redacting sensitive tokens; `.gitignore` enforcement | `SensitiveDataFilter` in `logging.py` | **VERIFIED** |
| **AI Prompt Injection** | Medium | Isolated delimiter tagging, citation validation against commit revisions | `context_retriever.py`, `citation_validator.py` | **VERIFIED** |
| **Cross-Site Scripting (XSS)** | Medium | Safe text rendering in React JSX; Highlight.js text output (no `innerHTML`) | `SourceViewer.tsx`, `CodeSearchView.tsx` | **VERIFIED** |

---

## 3. Implemented Defensive Mechanisms

### 3.1 Strict URL Validation & SSRF Prevention
Implemented in `backend/app/services/github_url.py`:
- Only canonical GitHub HTTPS URLs (`https://github.com/{owner}/{repo}`) are accepted.
- Non-standard protocols (`ftp://`, `ssh://`, `file://`, `gopher://`, `javascript:`) are rejected.
- Hostnames are constrained strictly to `github.com` and `www.github.com`.
- Blocks private IPv4 (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`), IPv6 loopback (`::1`), link-local/cloud metadata (`169.254.169.254`, `metadata.google.internal`).
- Embedded credentials (`https://user:password@...`) and custom port numbers (`:8080`) are rejected.

### 3.2 Path Traversal Defense
Implemented in `backend/app/services/github_ingestion.py:validate_path_safety`:
- Validates all file paths from GitHub git trees and API requests (`/api/v1/repositories/{id}/files/content?path=...`).
- Rejects relative traversal (`../`, `..\\`), Windows drive roots (`C:`, `D:`), URL-encoded traversals (`%2e%2e`, `%2f`, `%5c`), and NULL bytes (`\0`).
- Rejects path strings exceeding 500 characters.

### 3.3 Resource Limits & DoS Prevention
Configured in `Settings` and enforced during ingestion:
- **Maximum Tree Entries:** 5,000 entries.
- **Maximum Files Processed:** 600 files.
- **Maximum Single File Size:** 1 MB (larger files are excluded from processing).
- **Maximum Total Source Data:** 25 MB.
- **Request Timeout:** 30.0 seconds hard timeout per external HTTP request.
- When limits are reached, the analysis is clearly marked as `partial` with exceeded limits detailed in `limits_exceeded`.

### 3.4 Zero Code Execution Policy
- RepoSense AI **never** runs `npm install`, `pip install`, `make`, `setup.py`, or arbitrary shell scripts found inside analyzed repositories.
- All relationships and entry points are detected using passive AST analysis and static token scanners.

### 3.5 AI Prompt Injection Defense & Citation Validation
Implemented in `backend/app/services/ai/`:
- Ingested code snippets are isolated in explicit untrusted delimiters:
  `=== UNTRUSTED REPOSITORY SOURCE EVIDENCE: <path> (Lines <start>-<end>) ===`
- System instructions instruct models that enclosed text represents untrusted user data.
- Citations returned by AI models are strictly verified against actual repository files and line counts. Non-existent citations are dropped.
- In AI-free mode (`NullProvider`), answers are compiled deterministically from static analysis facts.

### 3.6 Secret Protection
- Logging uses `SensitiveDataFilter` to redact keys, tokens, and authorization headers.
- Gemini provider securely transmits API keys via `x-goog-api-key` HTTP headers rather than URL query parameters to prevent leakage in proxy logs and tracebacks.
- `.gitignore` prevents `.env` or credential files from being tracked.
- `.env.example` provides safe placeholder values only.

---

## 4. Remaining Security Risks & Operational Considerations

1. **GitHub API Rate Limits:** Unauthenticated requests are subject to GitHub's 60 req/hr IP limit. Users should configure a personal access token (`GITHUB_TOKEN`) for heavy usage (5,000 req/hr).
2. **ReDoS in Complex Third-Party Code:** While core token regexes use simple patterns, extremely large single-line minified files could increase parsing time. Large files (>1MB) are automatically skipped to mitigate this.
3. **Public Deployment Hardening:** When deploying publicly on the internet (outside private networks), operators should place RepoSense AI behind a reverse proxy (e.g., Nginx, Caddy, Cloudflare) with HTTPS termination, rate limiting, and standard DDoS protection.

---

## 5. Reporting a Vulnerability

If you discover a security vulnerability in RepoSense AI:
1. **Do NOT report security vulnerabilities through public GitHub issues.**
2. Report vulnerabilities privately to the maintainers or use GitHub's private vulnerability reporting feature.
3. Please include:
   - Detailed description of the vulnerability.
   - Minimal reproduction steps, proof-of-concept repository, or payload.
   - Assessment of potential security impact.
4. We acknowledge reports within 48 hours and work with reporters on coordinated disclosure.
