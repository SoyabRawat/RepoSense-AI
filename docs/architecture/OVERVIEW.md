# RepoSense AI — Architecture Overview & Design Patterns

## Overview
RepoSense AI is structured as a modular client-server application optimized for local development and eventual containerized deployment.

```
+--------------------------------------------------------+
|                     User Browser                       |
|       React 19 + TypeScript + Vite + Tailwind CSS       |
+---------------------------+----------------------------+
                            | HTTP / JSON (REST)
                            v
+--------------------------------------------------------+
|                 FastAPI Application                    |
|        Uvicorn ASGI + Pydantic v2 + Structured Logs    |
+---------------------------+----------------------------+
                            |
           +----------------+----------------+
           | (Implemented Analysis Engine)   |
           v                                 v
+-----------------------+       +------------------------+
| AST & Static Analyzers|       | Provider-Agnostic AI   |
| (Python/TS/Java/C AST)|       | (Ollama, Gemini, OpenAI|
+-----------------------+       +------------------------+
```

## Layer Responsibilities

### 1. Presentation Layer (`frontend/src/`)
- Pure client-side SPA built with React 19, TypeScript, and Vite.
- Strongly-typed HTTP service communication (`services/repoService.ts`, `services/api.ts`).
- Interactive dependency graph visualization powered by `@xyflow/react` (React Flow).
- High-performance monospace source code viewer with syntax highlighting and line targeting (`SourceViewer.tsx`).
- Full-text search interface with snippet matching and line jumping (`CodeSearchView.tsx`).
- Source-grounded AI explanation and citation navigation (`AskAIView.tsx`).

### 2. API Gateway & Routing (`backend/app/api/`)
- Exposes versioned REST routes under `/api/v1/repositories/`.
- Strict input sanitization and SSRF prevention on repository URLs.
- Validates request and response payloads via Pydantic schemas.
- Converts exceptions into standardized `ErrorResponse` objects with `error` and `detail` fields.

### 3. Core Foundation (`backend/app/core/`)
- Environment variable parsing via `Pydantic Settings`.
- Log sanitization through `SensitiveDataFilter`.
- CORS configuration with strict origins.

### 4. Static Analysis & AI Pipeline (`backend/app/services/`)
- **Ingestion engine:** Fetches Git trees and file blobs via GitHub REST API under strict resource bounds (5,000 tree entries, 25MB total source, 600 files, 1MB per file).
- **AST parser:** Traverses files, computes import relationships, and builds dependency graphs without executing repository code.
- **Entry-point detection:** Analyzes package manifests (`package.json`, `pyproject.toml`) and source guards (`__name__ == '__main__'`) with verified evidence.
- **Search engine:** Fast literal substring search across all indexed repository files with line indexing and context snippets.
- **AI layer:** In-memory evidence retriever extracts relevant snippets, encapsulates them in untrusted data delimiters, and delegates to configured providers (Gemini, OpenAI, Ollama, or deterministic offline NullProvider).
- **Citation validator:** Rigorously verifies all returned citations against the repository files and line counts.
