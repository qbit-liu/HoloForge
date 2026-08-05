#!/usr/bin/env python3
"""Scan proposed public-export files for common privacy boundary violations."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Optional, Sequence


DEFAULT_PATTERNS = (
    ("macOS home path", re.compile(r"/" + r"Users/[^/\s]+/")),
    ("Linux home path", re.compile(r"/" + r"home/[^/\s]+/")),
    ("Windows home path", re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+\\")),
    ("private key material", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
)

SKIP_DIRECTORIES = frozenset({".git", "__pycache__", ".pytest_cache", ".mypy_cache"})
MAX_FILE_BYTES = 5_000_000


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    column: int
    rule: str


def iter_files(paths: Sequence[Path]) -> Iterator[Path]:
    """Yield regular files under explicit paths in stable order."""

    for path in sorted(paths, key=lambda item: str(item)):
        if path.is_file():
            yield path
            continue
        if not path.exists():
            raise FileNotFoundError(path)
        for child in sorted(path.rglob("*")):
            if any(part in SKIP_DIRECTORIES for part in child.parts):
                continue
            if child.is_file():
                yield child


def read_text(path: Path) -> Optional[str]:
    """Return UTF-8 text, skipping large or binary files."""

    if path.stat().st_size > MAX_FILE_BYTES:
        return None
    payload = path.read_bytes()
    if b"\x00" in payload:
        return None
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError:
        return None


def custom_tokens(paths: Iterable[Path]) -> tuple[str, ...]:
    """Load nonempty, non-comment tokens from files kept outside the export."""

    tokens: list[str] = []
    for path in paths:
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            token = raw_line.strip()
            if token and not token.startswith("#"):
                tokens.append(token)
    return tuple(tokens)


def scan_text(path: Path, text: str, forbidden: Sequence[str]) -> list[Finding]:
    """Find default patterns and caller-supplied literal tokens."""

    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for rule, pattern in DEFAULT_PATTERNS:
            match = pattern.search(line)
            if match:
                findings.append(Finding(path, line_number, match.start() + 1, rule))
        for token in forbidden:
            column = line.find(token)
            if column >= 0:
                findings.append(
                    Finding(path, line_number, column + 1, "custom forbidden token")
                )
    return findings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Scan explicit files or directories for common private-path, key, "
            "and caller-supplied forbidden-token leaks."
        )
    )
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument(
        "--forbid-file",
        action="append",
        default=[],
        type=Path,
        help="UTF-8 file of literal forbidden tokens, one per line",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        forbidden = custom_tokens(args.forbid_file)
        files = list(iter_files(args.paths))
    except (FileNotFoundError, OSError) as error:
        print(f"audit error: {error}", file=sys.stderr)
        return 2

    findings: list[Finding] = []
    scanned = 0
    skipped = 0
    for path in files:
        try:
            text = read_text(path)
        except OSError as error:
            print(f"audit error: {path}: {error}", file=sys.stderr)
            return 2
        if text is None:
            skipped += 1
            continue
        scanned += 1
        findings.extend(scan_text(path, text, forbidden))

    for finding in findings:
        print(f"{finding.path}:{finding.line}:{finding.column}: {finding.rule}")

    if findings:
        print(f"FAIL: {len(findings)} finding(s) in {scanned} text file(s).")
        return 1

    print(f"PASS: {scanned} text file(s) scanned; {skipped} file(s) skipped.")
    print("Manual scientific, provenance, licensing, and disclosure review is still required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
