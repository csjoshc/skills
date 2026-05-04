#!/usr/bin/env python3
"""
File type detection for caveman - classifies files as natural language, code, config, or unknown.
"""

import json
import re
from pathlib import Path


# File extensions that are compressible (natural language)
COMPRESSIBLE_EXTENSIONS = {".md", ".txt", ".markdown", ".rst"}

# File extensions that should be skipped (code/config)
SKIPPABLE_EXTENSIONS = {
    # Python
    ".py", ".pyi", ".pyx",
    # JavaScript
    ".js", ".jsx", ".ts", ".tsx",
    # Other languages
    ".java", ".c", ".cpp", ".h", ".cs", ".go", ".rs", ".rb", ".php",
    ".swift", ".kt", ".scala", ".r", ".m", ".mm",
    # Config files
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".xml", ".html", ".css", ".scss", ".sass",
    # Data/Binary
    ".csv", ".xlsx", ".xls", ".pdf",
    ".zip", ".tar", ".gz", ".rar", ".7z",
    # Media
    ".mp4", ".mov", ".avi", ".mkv", ".mp3", ".wav", ".flac",
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".ico",
    # Build/Package
    ".gradle", ".maven", ".npm", ".cargo", ".go.sum", ".go.mod", ".lock",
    # Other
    ".sh", ".bash", ".env", ".git",
    ".gitignore", ".gitattributes", ".editorconfig",
    ".prettierrc", ".eslintrc",
}


def _is_json(content: str) -> bool:
    try:
        json.loads(content)
        return True
    except (json.JSONDecodeError, ValueError):
        return False


def _is_yaml(content: str) -> bool:
    lines = [line.strip() for line in content.split("\n") if line.strip()]
    if not lines:
        return False
    yaml_indicators = 0
    if lines[0].startswith("---"):
        yaml_indicators += 1
    key_value_pattern = re.compile(r"^[a-zA-Z0-9_-]+:\s*.+$")
    key_value_count = sum(1 for line in lines if key_value_pattern.match(line))
    list_pattern = re.compile(r"^-\s+.+$")
    list_count = sum(1 for line in lines if list_pattern.match(line))
    yaml_line_count = key_value_count + list_count
    if yaml_line_count > 0 and yaml_line_count / len(lines) > 0.6:
        return True
    return False


def _is_code(content: str) -> bool:
    lines = [line.strip() for line in content.split("\n") if line.strip()]
    if not lines:
        return False
    patterns = [
        re.compile(r"^(import|from)\s+"),
        re.compile(r"^(def|function|class|async|const|let|var)\s+"),
        re.compile(r"^(if|for|while|switch|try|catch)\s*[\(\{]"),
        re.compile(r"^\s*@\w+"),
        re.compile(r"^return\s+"),
        re.compile(r"^(export|public|private|protected)\s+"),
        re.compile(r"^[a-zA-Z_]\w*\s*[=\(]"),
    ]
    code_pattern_count = 0
    for line in lines:
        for pattern in patterns:
            if pattern.match(line):
                code_pattern_count += 1
                break
    if len(lines) > 0 and code_pattern_count / len(lines) > 0.4:
        return True
    return False


def detect_file_type(filepath: Path) -> str:
    extension = filepath.suffix.lower()
    if extension in COMPRESSIBLE_EXTENSIONS:
        return "natural_language"
    if extension in SKIPPABLE_EXTENSIONS:
        return "code"
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return "unknown"
    if _is_json(content):
        return "config"
    if _is_yaml(content):
        return "config"
    if _is_code(content):
        return "code"
    if content and len(content) > 0:
        return "natural_language"
    return "unknown"


def should_compress(filepath: Path) -> bool:
    """Returns True only for natural language files, skipping backups and code."""
    if filepath.name.endswith(".original.md"):
        return False
    file_type = detect_file_type(filepath)
    return file_type == "natural_language"


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 detect.py <filepath>")
        sys.exit(2)
    path = Path(sys.argv[1])
    file_type = detect_file_type(path)
    print(file_type)
    sys.exit(0 if should_compress(path) else 1)
