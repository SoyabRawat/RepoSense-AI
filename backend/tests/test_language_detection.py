"""Automated tests for language detection and distribution metrics."""

from app.services.language_detection import (
    calculate_language_distribution,
    detect_file_language,
    is_binary_or_excluded,
)


def test_extension_language_mapping() -> None:
    """Verify correct identification of key programming languages."""
    assert detect_file_language("main.py") == "Python"
    assert detect_file_language("src/index.ts") == "TypeScript"
    assert detect_file_language("components/Button.tsx") == "TypeScript"
    assert detect_file_language("utils.js") == "JavaScript"
    assert detect_file_language("App.jsx") == "JavaScript"
    assert detect_file_language("Server.java") == "Java"
    assert detect_file_language("main.c") == "C"
    assert detect_file_language("engine.cpp") == "C++"
    assert detect_file_language("header.hpp") == "C++ Header"
    assert detect_file_language("main.go") == "Go"
    assert detect_file_language("lib.rs") == "Rust"
    assert detect_file_language("index.html") == "HTML"
    assert detect_file_language("styles.css") == "CSS"
    assert detect_file_language("config.json") == "JSON"
    assert detect_file_language("deploy.yaml") == "YAML"
    assert detect_file_language("Cargo.toml") == "TOML"


def test_special_filenames() -> None:
    """Verify detection of special build and configuration filenames."""
    assert detect_file_language("Dockerfile") == "Dockerfile"
    assert detect_file_language("docker/Dockerfile") == "Dockerfile"
    assert detect_file_language("Makefile") == "Makefile"
    assert detect_file_language("CMakeLists.txt") == "CMake"


def test_binary_and_vendor_exclusion() -> None:
    """Verify that images, archives, binaries, and vendors are recognized as excluded."""
    assert is_binary_or_excluded("logo.png") is True
    assert is_binary_or_excluded("archive.zip") is True
    assert is_binary_or_excluded("program.exe") is True
    assert is_binary_or_excluded("cache.pyc") is True
    assert is_binary_or_excluded("node_modules/lodash/index.js") is True
    assert is_binary_or_excluded(".venv/lib/site.py") is True
    assert is_binary_or_excluded("dist/bundle.min.js") is True

    # Real source files should not be excluded
    assert is_binary_or_excluded("src/components/App.tsx") is False
    assert is_binary_or_excluded("backend/app/main.py") is False


def test_language_distribution_calculation() -> None:
    """Verify percentage calculation is grounded and based strictly on classified files."""
    files = [
        ("src/app.py", 1000),
        ("src/utils.py", 500),
        ("frontend/index.ts", 1500),
        ("assets/logo.png", 50000),  # Binary: excluded
        ("node_modules/pkg/index.js", 2000),  # Vendor: excluded
    ]

    counts, pcts, bytes_map, supported_total, examined_total = calculate_language_distribution(files)

    assert examined_total == 5
    assert supported_total == 3  # 2 python + 1 typescript
    assert counts["Python"] == 2
    assert counts["TypeScript"] == 1
    assert pcts["Python"] == 66.7
    assert pcts["TypeScript"] == 33.3
    assert bytes_map["Python"] == 1500
    assert bytes_map["TypeScript"] == 1500
