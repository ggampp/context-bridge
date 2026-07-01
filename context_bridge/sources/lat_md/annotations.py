from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from context_bridge.sources.lat_md.wiki_links import WikiLink, parse_wiki_links

# `// @lat: [[auth#OAuth Flow]]`, `# @lat: [[auth#OAuth Flow]]`, `/* @lat: [[...]] */`, etc.
_ANNOTATION_RE = re.compile(r"@lat:\s*(\[\[[^\]]+\]\])")

_DEFAULT_EXTENSIONS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".py", ".go", ".rs", ".java", ".kt", ".rb", ".cs",
    ".cpp", ".cc", ".c", ".h", ".hpp", ".php", ".swift", ".scala",
}

_SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    ".understand-anything", ".context-bridge", "lat.md",
    "dist", "build", ".pytest_cache", ".mypy_cache", "site-packages",
}


@dataclass(frozen=True)
class LatAnnotation:
    file_path: str  # relative to project_root, forward slashes
    line: int
    link: WikiLink


def _iter_source_files(project_root: Path, extensions: set[str]):
    for path in project_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in extensions:
            continue
        if any(part in _SKIP_DIRS for part in path.relative_to(project_root).parts):
            continue
        yield path


def scan_annotations(
    project_root: str | Path,
    *,
    extensions: set[str] | None = None,
) -> list[LatAnnotation]:
    """Scan source files under `project_root` for `@lat: [[...]]` comment annotations.

    Best-effort text scan (no language parsing) — cheap enough to run on
    every `graph import lat-md`, and limited to a known set of code
    extensions to keep large repos fast (see Sprint 8 risks).
    """
    root = Path(project_root)
    exts = extensions or _DEFAULT_EXTENSIONS
    annotations: list[LatAnnotation] = []

    for path in _iter_source_files(root, exts):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if "@lat:" not in text:
            continue
        rel = path.relative_to(root).as_posix()
        for lineno, line in enumerate(text.splitlines(), start=1):
            for match in _ANNOTATION_RE.finditer(line):
                links = parse_wiki_links(match.group(1))
                for link in links:
                    annotations.append(LatAnnotation(file_path=rel, line=lineno, link=link))

    return annotations
