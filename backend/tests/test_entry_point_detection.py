"""Automated tests for entry-point identification across multiple languages."""

from app.services.entry_point_detection import detect_entry_points


def test_package_json_confirmed_entry_points() -> None:
    """Verify package.json 'bin' and 'main' properties yield confirmed entry points."""
    files = {
        "package.json": '{"name": "my-tool", "bin": "./cli.js", "main": "./index.js"}',
        "cli.js": '#!/usr/bin/env node\nconsole.log("running");',
        "index.js": 'module.exports = {};',
    }

    entry_points = detect_entry_points(files)
    assert len(entry_points) == 2

    paths = {ep.file_path: ep for ep in entry_points}
    assert "cli.js" in paths
    assert paths["cli.js"].confidence == "confirmed"
    assert "package.json" in paths["cli.js"].detection_method

    assert "index.js" in paths
    assert paths["index.js"].confidence == "confirmed"


def test_python_entry_points() -> None:
    """Verify detection of __main__.py, execution guards, and web app factories."""
    files = {
        "run.py": 'import sys\n\nif __name__ == "__main__":\n    print("started")\n',
        "pkg/__main__.py": 'print("package entry")',
        "web/app.py": 'from fastapi import FastAPI\n\napp = FastAPI()\n',
        "utils/helper.py": 'def add(a, b):\n    return a + b\n',
    }

    entry_points = detect_entry_points(files)
    paths = {ep.file_path: ep for ep in entry_points}

    assert "pkg/__main__.py" in paths
    assert paths["pkg/__main__.py"].confidence == "confirmed"

    assert "run.py" in paths
    assert paths["run.py"].confidence == "likely"
    assert "Line 3" in paths["run.py"].evidence

    assert "web/app.py" in paths
    assert paths["web/app.py"].confidence == "likely"

    # helper.py should NOT be an entry point
    assert "utils/helper.py" not in paths


def test_java_c_entry_points() -> None:
    """Verify Java and C/C++ main functions are detected."""
    files = {
        "src/Main.java": 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello");\n    }\n}\n',
        "engine/main.c": '#include <stdio.h>\n\nint main(int argc, char** argv) {\n    return 0;\n}\n',
    }

    entry_points = detect_entry_points(files)
    paths = {ep.file_path: ep for ep in entry_points}

    assert "src/Main.java" in paths
    assert paths["src/Main.java"].language == "Java"
    assert paths["src/Main.java"].confidence == "likely"

    assert "engine/main.c" in paths
    assert paths["engine/main.c"].language == "C/C++"
    assert paths["engine/main.c"].confidence == "likely"
