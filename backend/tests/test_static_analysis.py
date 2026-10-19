"""Automated tests for static import extraction and manifest dependency analysis."""

from app.services.static_analysis import (
    analyze_repository_relationships,
    parse_python_imports,
    parse_jsts_imports,
    parse_manifest_dependencies,
)


def test_python_ast_import_resolution() -> None:
    """Verify Python AST import extraction, line numbers, and internal file resolution."""
    all_files = {"app/main.py", "app/core/config.py", "app/utils.py"}
    content = (
        "import os\n"
        "import sys\n"
        "from app.core.config import get_settings\n"
        "from .utils import helper\n"
        "import nonexistent_module\n"
    )

    rels = parse_python_imports("app/main.py", content, all_files)

    by_target = {r.target_module: r for r in rels}

    # stdlib
    assert "os" in by_target
    assert by_target["os"].resolution_status == "external"

    # resolved internal absolute import
    assert "app.core.config" in by_target
    assert by_target["app.core.config"].resolution_status == "resolved"
    assert by_target["app.core.config"].resolved_target_file == "app/core/config.py"
    assert by_target["app.core.config"].source_line == 3

    # resolved relative import
    assert ".utils" in by_target
    assert by_target[".utils"].resolution_status == "resolved"
    assert by_target[".utils"].resolved_target_file == "app/utils.py"

    # unresolved internal import
    assert "nonexistent_module" in by_target
    assert by_target["nonexistent_module"].resolution_status == "unresolved"


def test_jsts_import_resolution() -> None:
    """Verify JavaScript and TypeScript import extraction."""
    all_files = {"src/App.tsx", "src/components/Button.tsx", "src/main.tsx"}
    content = (
        "import React from 'react';\n"
        "import { Button } from './components/Button';\n"
        "import lodash from 'lodash';\n"
    )

    rels = parse_jsts_imports("src/App.tsx", content, all_files)
    by_target = {r.target_module: r for r in rels}

    # internal relative
    assert "./components/Button" in by_target
    assert by_target["./components/Button"].resolution_status == "resolved"
    assert by_target["./components/Button"].resolved_target_file == "src/components/Button.tsx"

    # external npm
    assert "react" in by_target
    assert by_target["react"].resolution_status == "external"
    assert "lodash" in by_target
    assert by_target["lodash"].resolution_status == "external"


def test_manifest_dependencies() -> None:
    """Verify extraction of dependencies from package.json and requirements.txt."""
    files = {
        "package.json": '{"dependencies": {"react": "^19.0.0"}, "devDependencies": {"vite": "^6.0.0"}}',
        "requirements.txt": "fastapi>=0.115.0\nuvicorn[standard]>=0.30.0\n# comment\n",
    }

    manifest_rels = parse_manifest_dependencies(files)
    targets = {r.target_module for r in manifest_rels}

    assert any("react" in t for t in targets)
    assert any("vite" in t for t in targets)
    assert any("fastapi" in t for t in targets)
    assert any("uvicorn" in t for t in targets)


def test_full_repository_relationship_analysis() -> None:
    """Verify unified repository relationship analyzer."""
    files = {
        "requirements.txt": "fastapi>=0.115.0\n",
        "app/main.py": "from fastapi import FastAPI\nfrom app.router import api_router\n",
        "app/router.py": "pass\n",
    }

    rels = analyze_repository_relationships(files)
    assert len(rels) >= 3

    internal = [r for r in rels if r.relationship_type == "internal_import"]
    assert len(internal) >= 1
    assert internal[0].resolved_target_file == "app/router.py"
