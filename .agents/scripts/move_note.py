#!/usr/bin/env python3
"""Move a Markdown note inside src/ while preserving supported links.

The script is intentionally narrow. It handles one-line inline Markdown links
with explicit local .md targets. Unsupported Markdown reference forms that
refer to the moved note abort the operation before any file is changed.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


class MoveError(Exception):
    """A preflight error that must leave the notebook unchanged."""


INLINE_LINK = re.compile(
    r"(?<!!)(?P<whole>\[(?P<label>[^]\n]+)\]\((?P<target>[^()\s]+)\))"
)
REFERENCE_DEFINITION = re.compile(r"^\s*\[[^]\n]+\]:\s*(?P<target>\S+)")
WIKI_LINK = re.compile(r"\[\[[^]\n]+\]\]")


@dataclass(frozen=True)
class Rewrite:
    file: Path
    line: int
    old_target: str
    new_target: str


@dataclass
class MovePlan:
    root: Path
    source: Path
    destination: Path
    contents: dict[Path, str]
    rewrites: list[Rewrite]


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def safe_path(root: Path, relative: str, label: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute():
        raise MoveError(f"{label} must be relative to src/: {relative}")
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise MoveError(f"{label} escapes src/: {relative}") from error
    if resolved.suffix != ".md":
        raise MoveError(f"{label} must name a .md file: {relative}")
    return resolved


def is_local_markdown_target(target: str) -> bool:
    path, _, _anchor = target.partition("#")
    return (
        bool(path)
        and path.endswith(".md")
        and not path.startswith(("/", "~", "http:", "https:", "mailto:", "file:"))
    )


def resolve_target(source_file: Path, target: str, root: Path) -> Path | None:
    path_text, _, _anchor = target.partition("#")
    if not is_local_markdown_target(target):
        return None
    if "%" in path_text:
        raise MoveError(
            f"percent-encoded Markdown path is unsupported: {source_file}: {target}"
        )
    target_path = (source_file.parent / path_text).resolve()
    try:
        target_path.relative_to(root)
    except ValueError as error:
        raise MoveError(f"link escapes src/: {source_file}: {target}") from error
    return target_path


def markdown_files(root: Path) -> list[Path]:
    return sorted(path.resolve() for path in root.rglob("*.md") if path.is_file())


def mask_inline_code(line: str) -> str:
    """Mask paired inline-code spans without changing character positions."""
    masked = list(line)
    opener: tuple[int, int] | None = None
    index = 0
    while index < len(line):
        if line[index] != "`":
            index += 1
            continue
        end = index
        while end < len(line) and line[end] == "`":
            end += 1
        width = end - index
        if opener is None:
            opener = (index, width)
        elif opener[1] == width:
            for position in range(opener[0], end):
                masked[position] = " "
            opener = None
        index = end
    return "".join(masked)


def reject_unsupported_reference(
    line: str, source_file: Path, moved_source: Path, root: Path
) -> None:
    definition = REFERENCE_DEFINITION.match(line)
    if definition:
        target = definition.group("target")
        resolved = resolve_target(source_file, target, root)
        if resolved == moved_source:
            raise MoveError(
                f"reference-style link to moved note is unsupported: {source_file}: {target}"
            )
    if WIKI_LINK.search(line) and moved_source.name in line:
        raise MoveError(
            f"wiki-link-like reference may target moved note: {source_file}: {line.strip()}"
        )


def relative_target(target: Path, from_file: Path, anchor: str) -> str:
    relative = os.path.relpath(target, from_file.parent).replace(os.sep, "/")
    return f"{relative}#{anchor}" if anchor else relative


def rewrite_file(
    source_file: Path,
    new_file: Path,
    content: str,
    moved_source: Path,
    destination: Path,
    root: Path,
) -> tuple[str, list[Rewrite]]:
    lines = content.splitlines(keepends=True)
    in_fence = False
    rewrites: list[Rewrite] = []
    result: list[str] = []

    for line_number, line in enumerate(lines, start=1):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            result.append(line)
            continue
        if in_fence:
            result.append(line)
            continue
        visible_line = mask_inline_code(line)
        reject_unsupported_reference(visible_line, source_file, moved_source, root)
        pieces: list[str] = []
        position = 0
        for match in INLINE_LINK.finditer(visible_line):
            target = line[match.start("target") : match.end("target")]
            resolved = resolve_target(source_file, target, root)
            replacement = target
            if resolved is not None:
                effective_target = destination if resolved == moved_source else resolved
                if source_file == moved_source or resolved == moved_source:
                    _path, separator, anchor = target.partition("#")
                    replacement = relative_target(effective_target, new_file, anchor if separator else "")
            pieces.append(line[position : match.start("target")])
            pieces.append(replacement)
            position = match.end("target")
            if replacement != target:
                rewrites.append(Rewrite(source_file, line_number, target, replacement))
        pieces.append(line[position:])
        result.append("".join(pieces))
    return "".join(result), rewrites


def build_plan(root: Path, source_relative: str, destination_relative: str) -> MovePlan:
    root = root.resolve()
    source = safe_path(root, source_relative, "source")
    destination = safe_path(root, destination_relative, "destination")
    if not source.is_file():
        raise MoveError(f"source does not exist: {source_relative}")
    if destination.exists():
        raise MoveError(f"destination already exists: {destination_relative}")
    if source == destination:
        raise MoveError("source and destination are the same")

    contents: dict[Path, str] = {}
    rewrites: list[Rewrite] = []
    for file_path in markdown_files(root):
        original = file_path.read_text(encoding="utf-8")
        output_path = destination if file_path == source else file_path
        rewritten, file_rewrites = rewrite_file(
            file_path, output_path, original, source, destination, root
        )
        contents[output_path] = rewritten
        rewrites.extend(file_rewrites)
    return MovePlan(root, source, destination, contents, rewrites)


def validate_plan(plan: MovePlan) -> None:
    future_files = set(plan.contents)
    for source_file, content in plan.contents.items():
        in_fence = False
        for line_number, line in enumerate(content.splitlines(), start=1):
            if line.lstrip().startswith(("```", "~~~")):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            visible_line = mask_inline_code(line)
            for match in INLINE_LINK.finditer(visible_line):
                target = line[match.start("target") : match.end("target")]
                resolved = resolve_target(source_file, target, plan.root)
                if resolved is not None and resolved not in future_files:
                    raise MoveError(
                        f"broken local link after move: {source_file}:{line_number}: {target}"
                    )


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as temporary:
        temporary.write(content)
        temporary.flush()
        os.fsync(temporary.fileno())
        temporary_path = Path(temporary.name)
    temporary_path.replace(path)


def apply_plan(plan: MovePlan) -> None:
    originals = {path: path.read_text(encoding="utf-8") for path in markdown_files(plan.root)}
    changed_existing = [
        path
        for path, content in plan.contents.items()
        if path in originals and originals[path] != content
    ]
    try:
        for path in changed_existing:
            atomic_write(path, plan.contents[path])
        atomic_write(plan.destination, plan.contents[plan.destination])
        plan.source.unlink()
        validate_plan(plan)
    except Exception:
        for path, content in originals.items():
            atomic_write(path, content)
        if plan.destination.exists() and plan.destination not in originals:
            plan.destination.unlink()
        raise


def print_plan(plan: MovePlan) -> None:
    print(f"MOVE {plan.source.relative_to(plan.root)} -> {plan.destination.relative_to(plan.root)}")
    if not plan.rewrites:
        print("No supported link rewrites are required.")
        return
    for rewrite in plan.rewrites:
        print(
            f"{rewrite.file.relative_to(plan.root)}:{rewrite.line}: "
            f"{rewrite.old_target} -> {rewrite.new_target}"
        )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="existing path relative to src/")
    parser.add_argument("destination", help="new path relative to src/")
    parser.add_argument(
        "--apply", action="store_true", help="perform the reviewed move; default is dry-run"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        plan = build_plan(repository_root() / "src", args.source, args.destination)
        validate_plan(plan)
        print_plan(plan)
        if args.apply:
            apply_plan(plan)
            print("Move applied; local Markdown targets validated.")
        else:
            print("Dry run only. Re-run with --apply after reviewing this plan.")
    except MoveError as error:
        print(f"move_note: {error}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"move_note: filesystem failure: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
