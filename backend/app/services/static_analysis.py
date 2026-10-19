"""Static analysis service for extracting import relationships and manifest dependencies."""

import ast
import json
import posixpath
import re
import sys
from pathlib import PurePosixPath
from typing import Dict, List, Optional, Set
import tomllib

from app.schemas.repository import ImportRelationship

# Known standard library modules for Python
PYTHON_STDLIB = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else {
    "abc", "argparse", "ast", "asyncio", "base64", "collections", "contextlib",
    "copy", "csv", "dataclasses", "datetime", "decimal", "enum", "functools",
    "hashlib", "http", "io", "itertools", "json", "logging", "math", "os",
    "pathlib", "random", "re", "shutil", "socket", "sqlite3", "ssl", "string",
    "subprocess", "sys", "tempfile", "threading", "time", "typing", "unittest",
    "urllib", "uuid", "warnings", "weakref", "zipfile",
}

# Regex patterns for JS/TS, Java, C/C++
JS_IMPORT_REGEX = re.compile(
    r'''(?:import\s+(?:[\w*\s{},$]+from\s+)?|export\s+(?:[\w*\s{},$]+from\s+)?|require\s*\(\s*|import\s*\(\s*)['"]([^'"]+)['"]''',
    re.MULTILINE
)
JAVA_IMPORT_REGEX = re.compile(r'import\s+(?:static\s+)?([a-zA-Z0-9_.]+);', re.MULTILINE)
C_INCLUDE_REGEX = re.compile(r'#include\s*([<"])([^>"]+)([>"])', re.MULTILINE)
REQUIREMENTS_LINE_REGEX = re.compile(r'^([a-zA-Z0-9_\-\.]+)', re.MULTILINE)


def resolve_python_import(
    source_file: str,
    module_name: str,
    level: int,  # 0 for absolute, >0 for relative
    all_files: Set[str],
) -> Optional[str]:
    """Resolve a Python import to a specific repository file if internal."""
    source_dir = posixpath.dirname(source_file)

    if level > 0:
        # Relative import
        cur = source_dir
        for _ in range(level - 1):
            if not cur:
                # Attempted relative import beyond top-level package
                return None
            cur = posixpath.dirname(cur)
        if module_name:
            rel_path = posixpath.normpath(posixpath.join(cur, module_name.replace(".", "/")))
        else:
            rel_path = cur

        if rel_path.startswith("../") or rel_path == "..":
            return None

        for candidate in (
            f"{rel_path}.py",
            posixpath.join(rel_path, "__init__.py"),
        ):
            if candidate in all_files:
                return candidate
        return None

    # Absolute import
    # Try direct mapping: module.sub -> module/sub.py or module/sub/__init__.py
    path_from_module = module_name.replace(".", "/")
    candidates = [
        f"{path_from_module}.py",
        posixpath.join(path_from_module, "__init__.py"),
    ]

    # Also check from common roots (e.g., "src/", "app/", or same dir as source)
    for root in ("", "src", "app", source_dir):
        prefix = f"{root}/" if root else ""
        candidates.extend([
            f"{prefix}{path_from_module}.py",
            posixpath.join(f"{prefix}{path_from_module}", "__init__.py"),
        ])

    for c in candidates:
        norm = posixpath.normpath(c)
        if norm in all_files:
            return norm

    return None


def resolve_jsts_import(
    source_file: str,
    import_path: str,
    all_files: Set[str],
) -> Optional[str]:
    """Resolve a JS/TS import specifier to a repository file."""
    source_dir = posixpath.dirname(source_file)

    if import_path.startswith("./") or import_path.startswith("../"):
        joined = posixpath.normpath(posixpath.join(source_dir, import_path))
        if joined.startswith("../") or joined == "..":
            return None
        candidates = [
            joined,
            f"{joined}.ts",
            f"{joined}.tsx",
            f"{joined}.js",
            f"{joined}.jsx",
            posixpath.join(joined, "index.ts"),
            posixpath.join(joined, "index.tsx"),
            posixpath.join(joined, "index.js"),
            posixpath.join(joined, "index.jsx"),
        ]
        for c in candidates:
            if c in all_files:
                return c
        return None

    # Handle alias paths like '@/...' or '~/...'
    if import_path.startswith("@/") or import_path.startswith("~/"):
        sub = import_path[2:]
        for base in ("src", ""):
            joined = posixpath.normpath(posixpath.join(base, sub))
            for c in (
                joined,
                f"{joined}.ts",
                f"{joined}.tsx",
                f"{joined}.js",
                f"{joined}.jsx",
                posixpath.join(joined, "index.ts"),
                posixpath.join(joined, "index.js"),
            ):
                if c in all_files:
                    return c

    return None


def parse_python_imports(
    file_path: str, content: str, all_files: Set[str]
) -> List[ImportRelationship]:
    """Parse imports from a Python source file using the AST parser."""
    relationships: List[ImportRelationship] = []

    try:
        tree = ast.parse(content, filename=file_path)
    except SyntaxError:
        # Graceful recovery for syntax errors
        return relationships

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod_name = alias.name
                resolved = resolve_python_import(file_path, mod_name, 0, all_files)
                is_internal = resolved is not None
                is_stdlib = mod_name.split(".")[0] in PYTHON_STDLIB

                status = "resolved" if is_internal else ("external" if is_stdlib else "unresolved")
                rel_type = "internal_import" if is_internal else "external_dependency"

                relationships.append(
                    ImportRelationship(
                        source_file=file_path,
                        target_module=mod_name,
                        resolved_target_file=resolved,
                        relationship_type=rel_type,
                        source_line=node.lineno,
                        resolution_status=status,
                    )
                )

        elif isinstance(node, ast.ImportFrom):
            mod_name = node.module or ""
            level = node.level
            full_mod = f"{'.' * level}{mod_name}" if level > 0 else mod_name

            resolved = resolve_python_import(file_path, mod_name, level, all_files)
            is_internal = resolved is not None
            root_mod = mod_name.split(".")[0] if mod_name else ""
            is_stdlib = root_mod in PYTHON_STDLIB and level == 0

            status = "resolved" if is_internal else ("external" if is_stdlib else "unresolved")
            rel_type = "internal_import" if is_internal else "external_dependency"

            relationships.append(
                ImportRelationship(
                    source_file=file_path,
                    target_module=full_mod,
                    resolved_target_file=resolved,
                    relationship_type=rel_type,
                    source_line=node.lineno,
                    resolution_status=status,
                )
            )

    return relationships


def parse_jsts_imports(
    file_path: str, content: str, all_files: Set[str]
) -> List[ImportRelationship]:
    """Parse imports and requires from JavaScript/TypeScript code."""
    relationships: List[ImportRelationship] = []

    for match in JS_IMPORT_REGEX.finditer(content):
        import_path = match.group(1).strip()
        line_no = content[:match.start()].count("\n") + 1

        resolved = resolve_jsts_import(file_path, import_path, all_files)
        if resolved:
            relationships.append(
                ImportRelationship(
                    source_file=file_path,
                    target_module=import_path,
                    resolved_target_file=resolved,
                    relationship_type="internal_import",
                    source_line=line_no,
                    resolution_status="resolved",
                )
            )
        elif import_path.startswith("./") or import_path.startswith("../"):
            relationships.append(
                ImportRelationship(
                    source_file=file_path,
                    target_module=import_path,
                    resolved_target_file=None,
                    relationship_type="internal_import",
                    source_line=line_no,
                    resolution_status="unresolved",
                )
            )
        else:
            # External npm dependency
            relationships.append(
                ImportRelationship(
                    source_file=file_path,
                    target_module=import_path,
                    resolved_target_file=None,
                    relationship_type="external_dependency",
                    source_line=line_no,
                    resolution_status="external",
                )
            )

    return relationships


def parse_java_imports(
    file_path: str, content: str, all_files: Set[str]
) -> List[ImportRelationship]:
    """Parse Java import statements."""
    relationships: List[ImportRelationship] = []

    for match in JAVA_IMPORT_REGEX.finditer(content):
        pkg_class = match.group(1).strip()
        line_no = content[:match.start()].count("\n") + 1

        # Check if resolves to a repo .java file
        path_candidate = f"{pkg_class.replace('.', '/')}.java"
        resolved = None
        for f in all_files:
            if f.endswith(path_candidate) or f.endswith(f"/{path_candidate}"):
                resolved = f
                break

        is_std = pkg_class.startswith("java.") or pkg_class.startswith("javax.")
        status = "resolved" if resolved else ("external" if is_std else "external")
        rel_type = "internal_import" if resolved else "external_dependency"

        relationships.append(
            ImportRelationship(
                source_file=file_path,
                target_module=pkg_class,
                resolved_target_file=resolved,
                relationship_type=rel_type,
                source_line=line_no,
                resolution_status=status,
            )
        )

    return relationships


def parse_c_includes(
    file_path: str, content: str, all_files: Set[str]
) -> List[ImportRelationship]:
    """Parse C/C++ #include statements."""
    relationships: List[ImportRelationship] = []
    source_dir = posixpath.dirname(file_path)

    for match in C_INCLUDE_REGEX.finditer(content):
        open_char = match.group(1)
        include_path = match.group(2).strip()
        line_no = content[:match.start()].count("\n") + 1

        if open_char == '"':
            # Quoted include (local/project header)
            candidate = posixpath.normpath(posixpath.join(source_dir, include_path))
            resolved = candidate if candidate in all_files else None
            status = "resolved" if resolved else "unresolved"
            relationships.append(
                ImportRelationship(
                    source_file=file_path,
                    target_module=include_path,
                    resolved_target_file=resolved,
                    relationship_type="internal_import",
                    source_line=line_no,
                    resolution_status=status,
                )
            )
        else:
            # Angle-bracket include (system/external library)
            relationships.append(
                ImportRelationship(
                    source_file=file_path,
                    target_module=include_path,
                    resolved_target_file=None,
                    relationship_type="external_dependency",
                    source_line=line_no,
                    resolution_status="external",
                )
            )

    return relationships


def parse_manifest_dependencies(
    files: Dict[str, str]
) -> List[ImportRelationship]:
    """Extract declared project dependencies from package manifests."""
    manifest_deps: List[ImportRelationship] = []

    # 1. package.json
    if "package.json" in files:
        try:
            data = json.loads(files["package.json"])
            if isinstance(data, dict):
                for dep_kind in ("dependencies", "devDependencies"):
                    deps = data.get(dep_kind, {})
                    if isinstance(deps, dict):
                        for pkg_name, pkg_version in deps.items():
                            manifest_deps.append(
                                ImportRelationship(
                                    source_file="package.json",
                                    target_module=f"{pkg_name} ({pkg_version})",
                                    resolved_target_file=None,
                                    relationship_type="manifest_dependency",
                                    source_line=None,
                                    resolution_status="external",
                                )
                            )
        except Exception:
            pass

    # 2. requirements.txt
    if "requirements.txt" in files:
        for line_idx, line in enumerate(files["requirements.txt"].splitlines(), start=1):
            clean = line.strip()
            if not clean or clean.startswith("#") or clean.startswith("-"):
                continue
            match = REQUIREMENTS_LINE_REGEX.match(clean)
            if match:
                pkg_name = match.group(1)
                manifest_deps.append(
                    ImportRelationship(
                        source_file="requirements.txt",
                        target_module=clean,
                        resolved_target_file=None,
                        relationship_type="manifest_dependency",
                        source_line=line_idx,
                        resolution_status="external",
                    )
                )

    # 3. pyproject.toml
    if "pyproject.toml" in files:
        try:
            data = tomllib.loads(files["pyproject.toml"])
            # [project.dependencies]
            project_deps = data.get("project", {}).get("dependencies", [])
            if isinstance(project_deps, list):
                for dep in project_deps:
                    if isinstance(dep, str):
                        manifest_deps.append(
                            ImportRelationship(
                                source_file="pyproject.toml",
                                target_module=dep,
                                resolved_target_file=None,
                                relationship_type="manifest_dependency",
                                source_line=None,
                                resolution_status="external",
                            )
                        )
            # [tool.poetry.dependencies]
            poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            if isinstance(poetry_deps, dict):
                for pkg, spec in poetry_deps.items():
                    if pkg.lower() != "python":
                        manifest_deps.append(
                            ImportRelationship(
                                source_file="pyproject.toml",
                                target_module=f"{pkg} ({spec})",
                                resolved_target_file=None,
                                relationship_type="manifest_dependency",
                                source_line=None,
                                resolution_status="external",
                            )
                        )
        except Exception:
            pass

    return manifest_deps


def analyze_repository_relationships(
    files: Dict[str, str]  # file_path -> text_content
) -> List[ImportRelationship]:
    """
    Run language-aware static import analysis on all repository files.
    """
    all_files = set(files.keys())
    all_relationships: List[ImportRelationship] = []

    # 1. Manifest dependencies
    manifest_deps = parse_manifest_dependencies(files)
    all_relationships.extend(manifest_deps)

    # 2. Source-level imports
    for file_path, content in files.items():
        if not content:
            continue

        ext = PurePosixPath(file_path).suffix.lower()

        if ext in (".py", ".pyw"):
            all_relationships.extend(parse_python_imports(file_path, content, all_files))
        elif ext in (".ts", ".tsx", ".js", ".jsx", ".mjs"):
            all_relationships.extend(parse_jsts_imports(file_path, content, all_files))
        elif ext == ".java":
            all_relationships.extend(parse_java_imports(file_path, content, all_files))
        elif ext in (".c", ".cpp", ".cc", ".cxx", ".h", ".hpp"):
            all_relationships.extend(parse_c_includes(file_path, content, all_files))

    return all_relationships
