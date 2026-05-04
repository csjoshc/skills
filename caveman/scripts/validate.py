#!/usr/bin/env python3
"""
Validation for caveman - checks that compressed files preserve critical elements.

Validates that headings, code blocks, URLs, and file paths are preserved.
"""

import re
from pathlib import Path


def _extract_headings(content: str) -> list:
    pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    matches = pattern.findall(content)
    return [(len(m[0]), m[1]) for m in matches]


def _extract_code_blocks(content: str) -> list:
    blocks = []
    pattern1 = re.compile(r"```(?:\w+)?\n(.*?)\n```", re.DOTALL)
    for match in pattern1.finditer(content):
        blocks.append(match.group(1).strip())
    pattern2 = re.compile(r"~~~(?:\w+)?\n(.*?)\n~~~", re.DOTALL)
    for match in pattern2.finditer(content):
        blocks.append(match.group(1).strip())
    return blocks


def _extract_urls(content: str) -> list:
    pattern = re.compile(r"https?://[^\s\)\]]+")
    return pattern.findall(content)


def _extract_file_paths(content: str) -> list:
    paths = []
    pattern1 = re.compile(r"([\.]{1,2}/[^\s\)\]]+)")
    paths.extend(pattern1.findall(content))
    pattern2 = re.compile(r"(/[^\s\)\]]+)")
    paths.extend(pattern2.findall(content))
    pattern3 = re.compile(r"([A-Za-z]:\\[^\s\)\]]+)")
    paths.extend(pattern3.findall(content))
    return list(set(paths))


def _extract_bullets(content: str) -> list:
    pattern = re.compile(r"^[\s]*([-*+])\s+(.+)$", re.MULTILINE)
    return pattern.findall(content)


def validate_file(original_path: Path, compressed_path: Path) -> tuple:
    """
    Validate compressed file preserves critical elements.
    Returns (errors, warnings) — errors block, warnings allow.
    """
    try:
        original = original_path.read_text(encoding="utf-8")
        compressed = compressed_path.read_text(encoding="utf-8")
    except Exception as e:
        return ([f"Failed to read files: {e}"], [])

    errors = []
    warnings = []

    # Headings
    original_headings = _extract_headings(original)
    compressed_headings = _extract_headings(compressed)
    if len(original_headings) != len(compressed_headings):
        errors.append(
            f"Heading count mismatch: {len(original_headings)} original vs {len(compressed_headings)} compressed"
        )
    else:
        for i, (o_level, o_text) in enumerate(original_headings):
            if i < len(compressed_headings):
                c_level, c_text = compressed_headings[i]
                if o_level != c_level:
                    errors.append(f"Heading level mismatch at position {i}: {o_level} vs {c_level}")
                if o_text != c_text:
                    warnings.append(f"Heading text changed: '{o_text}' -> '{c_text}'")

    # Code blocks
    original_blocks = _extract_code_blocks(original)
    compressed_blocks = _extract_code_blocks(compressed)
    if original_blocks != compressed_blocks:
        errors.append("Code blocks were modified")

    # URLs
    original_urls = _extract_urls(original)
    compressed_urls = _extract_urls(compressed)
    if set(original_urls) != set(compressed_urls):
        added = set(compressed_urls) - set(original_urls)
        removed = set(original_urls) - set(compressed_urls)
        if added or removed:
            errors.append(f"URLs changed: {len(added)} added, {len(removed)} removed")

    # File paths
    original_paths = _extract_file_paths(original)
    compressed_paths = _extract_file_paths(compressed)
    if original_paths != compressed_paths:
        added = set(compressed_paths) - set(original_paths)
        removed = set(original_paths) - set(compressed_paths)
        if added or removed:
            warnings.append(f"File paths changed: {len(added)} added, {len(removed)} removed")

    # Bullet points (allow 15% variance)
    original_bullets = _extract_bullets(original)
    compressed_bullets = _extract_bullets(compressed)
    bullet_change = abs(len(original_bullets) - len(compressed_bullets))
    bullet_threshold = max(1, int(len(original_bullets) * 0.15))
    if bullet_change > bullet_threshold:
        warnings.append(
            f"Bullet point count changed significantly: {len(original_bullets)} -> {len(compressed_bullets)}"
        )

    return (errors, warnings)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python validate.py <original_file> <compressed_file>")
        sys.exit(1)
    original = Path(sys.argv[1])
    compressed = Path(sys.argv[2])
    errors, warnings = validate_file(original, compressed)
    print(f"Errors: {len(errors)}")
    for error in errors:
        print(f"  - {error}")
    print(f"Warnings: {len(warnings)}")
    for warning in warnings:
        print(f"  - {warning}")
    sys.exit(1 if errors else 0)
