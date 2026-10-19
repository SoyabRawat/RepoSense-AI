"""Language detection and distribution analysis service."""

from pathlib import PurePosixPath
from typing import Dict, List, Optional, Tuple


# Documented mapping of extensions to normalized programming languages
EXTENSION_LANGUAGE_MAP: Dict[str, str] = {
    # Python
    ".py": "Python",
    ".pyi": "Python",
    ".pyx": "Python",
    # TypeScript
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    # JavaScript
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    # Java & JVM
    ".java": "Java",
    ".kt": "Kotlin",
    ".scala": "Scala",
    ".groovy": "Groovy",
    # C / C++
    ".c": "C",
    ".h": "C/C++ Header",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".hpp": "C++ Header",
    ".hh": "C++ Header",
    # Systems & Compiled
    ".go": "Go",
    ".rs": "Rust",
    ".swift": "Swift",
    ".cs": "C#",
    # Web & Style
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "Sass",
    ".less": "Less",
    # Data & Config
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".xml": "XML",
    ".sql": "SQL",
    # Shell & Scripting
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".ps1": "PowerShell",
    ".rb": "Ruby",
    ".php": "PHP",
    # Documentation
    ".md": "Markdown",
    ".markdown": "Markdown",
    ".rst": "reStructuredText",
}

# Known special filenames mapping to languages
SPECIAL_FILENAMES: Dict[str, str] = {
    "dockerfile": "Dockerfile",
    "containerfile": "Dockerfile",
    "makefile": "Makefile",
    "cmakelists.txt": "CMake",
    "jenkinsfile": "Groovy",
    "vagrantfile": "Ruby",
    "gemfile": "Ruby",
    "rakefile": "Ruby",
}

# Excluded binary extensions and build artifacts
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".svg", ".bmp", ".tiff",
    ".mp4", ".mov", ".avi", ".mkv", ".mp3", ".wav",
    ".zip", ".tar", ".gz", ".tgz", ".bz2", ".7z", ".rar",
    ".exe", ".dll", ".so", ".dylib", ".bin", ".o", ".a", ".obj",
    ".pyc", ".pyo", ".pyd", ".class", ".jar", ".war",
    ".wasm", ".woff", ".woff2", ".ttf", ".eot",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".sqlite", ".db", ".lock",
}

# Directories typically excluded from analysis
EXCLUDED_DIRECTORIES = {
    "node_modules", "vendor", "dist", "build", "target", ".git", ".github",
    ".idea", ".vscode", "__pycache__", ".venv", "venv", "env", ".next", ".nuxt",
}


def is_binary_or_excluded(path_str: str) -> bool:
    """Determine if a file path points to a binary asset or an excluded directory."""
    pure_path = PurePosixPath(path_str)
    
    # Check directory exclusion
    for part in pure_path.parts[:-1]:
        if part.lower() in EXCLUDED_DIRECTORIES:
            return True

    # Check extension exclusion
    suffix = pure_path.suffix.lower()
    if suffix in BINARY_EXTENSIONS:
        return True

    # Check minified scripts
    name = pure_path.name.lower()
    if name.endswith(".min.js") or name.endswith(".min.css") or name.endswith(".bundle.js"):
        return True

    return False


def detect_file_language(path_str: str) -> Optional[str]:
    """Detect language for a single file path based on documented extension and filename maps."""
    pure_path = PurePosixPath(path_str)
    filename = pure_path.name.lower()

    # 1. Check exact special filenames
    if filename in SPECIAL_FILENAMES:
        return SPECIAL_FILENAMES[filename]

    # 2. Check extension
    suffix = pure_path.suffix.lower()
    if suffix in EXTENSION_LANGUAGE_MAP:
        return EXTENSION_LANGUAGE_MAP[suffix]

    return None


def calculate_language_distribution(
    files: List[Tuple[str, int]]  # List of (file_path, byte_size)
) -> Tuple[Dict[str, int], Dict[str, float], Dict[str, int], int, int]:
    """
    Calculate deterministic language breakdown across supported files.

    Returns:
        (language_file_counts, language_percentages, language_byte_counts, total_supported, total_examined)
    """
    language_counts: Dict[str, int] = {}
    language_bytes: Dict[str, int] = {}
    total_supported = 0
    total_examined = len(files)

    for path_str, size in files:
        if is_binary_or_excluded(path_str):
            continue

        lang = detect_file_language(path_str)
        if lang:
            language_counts[lang] = language_counts.get(lang, 0) + 1
            language_bytes[lang] = language_bytes.get(lang, 0) + size
            total_supported += 1

    # Calculate percentages based strictly on classified supported files
    language_percentages: Dict[str, float] = {}
    if total_supported > 0:
        for lang, count in language_counts.items():
            language_percentages[lang] = round((count / total_supported) * 100, 1)

    return language_counts, language_percentages, language_bytes, total_supported, total_examined
