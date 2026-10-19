"""Application entry point detection service with verifiable evidence."""

import json
import re
from pathlib import PurePosixPath
from typing import Dict, List, Optional
from app.schemas.repository import EntryPointInfo

# Regular expressions for detecting entry points in source content
PYTHON_MAIN_BLOCK_REGEX = re.compile(r'if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:', re.MULTILINE)
PYTHON_APP_INIT_REGEX = re.compile(r'(?:app|application)\s*=\s*(?:FastAPI|Flask|Django|Sanic|Tornado)\b', re.MULTILINE)
JAVA_MAIN_METHOD_REGEX = re.compile(r'public\s+static\s+void\s+main\s*\(\s*String\s*(\[\s*\]\s*\w+|\w+\s*\[\s*\]|\.\.\.\s*\w+)\s*\)', re.MULTILINE)
C_CPP_MAIN_REGEX = re.compile(r'(?:int|void)\s+main\s*\(\s*(?:int\s+\w+,\s*char\s*\*\s*\w+\[\s*\]|int\s+\w+,\s*char\s*\*\*\s*\w+|void)?\s*\)', re.MULTILINE)
GO_MAIN_REGEX = re.compile(r'func\s+main\s*\(\s*\)', re.MULTILINE)
RUST_MAIN_REGEX = re.compile(r'fn\s+main\s*\(\s*\)', re.MULTILINE)


def detect_entry_points(
    files: Dict[str, str]  # file_path -> text_content
) -> List[EntryPointInfo]:
    """
    Examine repository files to detect confirmed and likely application entry points.
    
    Returns:
        List of EntryPointInfo models with file_path, detection_method, evidence, and confidence.
    """
    entry_points: List[EntryPointInfo] = []
    detected_paths = set()

    # 1. Check Package Manifests for CONFIRMED entry points
    # A. package.json
    if "package.json" in files:
        try:
            pkg_data = json.loads(files["package.json"])
            if isinstance(pkg_data, dict):
                # "bin" field
                bin_field = pkg_data.get("bin")
                if isinstance(bin_field, str):
                    clean_bin = bin_field.lstrip("./")
                    if clean_bin in files:
                        entry_points.append(
                            EntryPointInfo(
                                file_path=clean_bin,
                                language="JavaScript/TypeScript",
                                detection_method="package.json 'bin' property declaration",
                                evidence=f'"bin": "{bin_field}" declared in package.json',
                                confidence="confirmed",
                            )
                        )
                        detected_paths.add(clean_bin)
                elif isinstance(bin_field, dict):
                    for bin_name, bin_target in bin_field.items():
                        if isinstance(bin_target, str):
                            clean_bin = bin_target.lstrip("./")
                            if clean_bin in files and clean_bin not in detected_paths:
                                entry_points.append(
                                    EntryPointInfo(
                                        file_path=clean_bin,
                                        language="JavaScript/TypeScript",
                                        detection_method="package.json named 'bin' property declaration",
                                        evidence=f'"bin": {{ "{bin_name}": "{bin_target}" }} in package.json',
                                        confidence="confirmed",
                                    )
                                )
                                detected_paths.add(clean_bin)

                # "main" field
                main_field = pkg_data.get("main")
                if isinstance(main_field, str):
                    clean_main = main_field.lstrip("./")
                    # Check exact or with .ts/.js
                    candidate = None
                    if clean_main in files:
                        candidate = clean_main
                    elif f"{clean_main}.js" in files:
                        candidate = f"{clean_main}.js"
                    elif f"{clean_main}.ts" in files:
                        candidate = f"{clean_main}.ts"

                    if candidate and candidate not in detected_paths:
                        entry_points.append(
                            EntryPointInfo(
                                file_path=candidate,
                                language="JavaScript/TypeScript",
                                detection_method="package.json 'main' module declaration",
                                evidence=f'"main": "{main_field}" in package.json',
                                confidence="confirmed",
                            )
                        )
                        detected_paths.add(candidate)
        except Exception:
            pass

    # 2. Check source files content for LIKELY entry points
    for file_path, content in files.items():
        if file_path in detected_paths or not content:
            continue

        pure_path = PurePosixPath(file_path)
        ext = pure_path.suffix.lower()
        name = pure_path.name.lower()

        # Python
        if ext in (".py", ".pyw"):
            # Special __main__.py module
            if name == "__main__.py":
                entry_points.append(
                    EntryPointInfo(
                        file_path=file_path,
                        language="Python",
                        detection_method="Python executable package entry module (__main__.py)",
                        evidence=f"Module filename is {file_path}",
                        confidence="confirmed",
                    )
                )
                detected_paths.add(file_path)
                continue

            # Check if __name__ == '__main__':
            match = PYTHON_MAIN_BLOCK_REGEX.search(content)
            if match:
                # Find line number
                line_no = content[:match.start()].count("\n") + 1
                evidence_line = content[match.start():content.find("\n", match.start())].strip()
                entry_points.append(
                    EntryPointInfo(
                        file_path=file_path,
                        language="Python",
                        detection_method="Python standard '__main__' execution guard",
                        evidence=f"Line {line_no}: {evidence_line}",
                        confidence="likely",
                    )
                )
                detected_paths.add(file_path)
                continue

            # Check WSGI/ASGI application factory
            app_match = PYTHON_APP_INIT_REGEX.search(content)
            if app_match and name in ("main.py", "app.py", "wsgi.py", "asgi.py", "server.py"):
                line_no = content[:app_match.start()].count("\n") + 1
                evidence_line = content[app_match.start():content.find("\n", app_match.start())].strip()
                entry_points.append(
                    EntryPointInfo(
                        file_path=file_path,
                        language="Python",
                        detection_method="Web framework application initialization",
                        evidence=f"Line {line_no}: {evidence_line}",
                        confidence="likely",
                    )
                )
                detected_paths.add(file_path)
                continue

        # JavaScript / TypeScript client/server entry files
        elif ext in (".ts", ".tsx", ".js", ".jsx", ".mjs"):
            # Recognized SPA/Node standard entry paths
            if file_path in ("src/main.tsx", "src/main.ts", "src/index.tsx", "src/index.ts", "src/App.tsx", "index.js", "server.js", "app.js"):
                entry_points.append(
                    EntryPointInfo(
                        file_path=file_path,
                        language="TypeScript" if "ts" in ext else "JavaScript",
                        detection_method="Standard framework entry file convention",
                        evidence=f"Conventional entry file path: '{file_path}'",
                        confidence="likely",
                    )
                )
                detected_paths.add(file_path)
                continue

        # Java
        elif ext == ".java":
            java_match = JAVA_MAIN_METHOD_REGEX.search(content)
            if java_match:
                line_no = content[:java_match.start()].count("\n") + 1
                evidence_line = content[java_match.start():content.find("\n", java_match.start())].strip()
                entry_points.append(
                    EntryPointInfo(
                        file_path=file_path,
                        language="Java",
                        detection_method="Java standard 'public static void main' entry method",
                        evidence=f"Line {line_no}: {evidence_line}",
                        confidence="likely",
                    )
                )
                detected_paths.add(file_path)
                continue

        # C / C++
        elif ext in (".c", ".cpp", ".cc", ".cxx"):
            c_match = C_CPP_MAIN_REGEX.search(content)
            if c_match:
                line_no = content[:c_match.start()].count("\n") + 1
                evidence_line = content[c_match.start():content.find("\n", c_match.start())].strip()
                entry_points.append(
                    EntryPointInfo(
                        file_path=file_path,
                        language="C/C++",
                        detection_method="C/C++ 'main()' execution function",
                        evidence=f"Line {line_no}: {evidence_line}",
                        confidence="likely",
                    )
                )
                detected_paths.add(file_path)
                continue

        # Go
        elif ext == ".go":
            if "package main" in content:
                go_match = GO_MAIN_REGEX.search(content)
                if go_match:
                    line_no = content[:go_match.start()].count("\n") + 1
                    entry_points.append(
                        EntryPointInfo(
                            file_path=file_path,
                            language="Go",
                            detection_method="Go 'package main' with 'func main()'",
                            evidence=f"Line {line_no}: func main() in package main",
                            confidence="likely",
                        )
                    )
                    detected_paths.add(file_path)
                    continue

        # Rust
        elif ext == ".rs":
            rust_match = RUST_MAIN_REGEX.search(content)
            if rust_match or file_path in ("src/main.rs", "main.rs"):
                evidence_str = "src/main.rs binary crate root" if file_path == "src/main.rs" else "fn main() function declared"
                entry_points.append(
                    EntryPointInfo(
                        file_path=file_path,
                        language="Rust",
                        detection_method="Rust binary crate main function",
                        evidence=evidence_str,
                        confidence="likely",
                    )
                )
                detected_paths.add(file_path)
                continue

    return entry_points
