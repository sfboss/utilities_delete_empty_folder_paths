from __future__ import annotations

import argparse
import json
import os
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Iterable, List, Sequence

from . import __version__
from .core import ExecutionSettings, normalise_path, process_paths
from .logging_utils import JsonlLogger, build_log_context, default_log_path, fallback_log_path
from .models import PathResult, ResultStatus, SkipReason
from .render import create_renderer, make_console


def _detect_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


def _compute_protected_roots(repo_root: Path) -> Sequence[Path]:
    roots = {repo_root, Path.home()}
    if sys.platform.startswith("win"):
        anchor = repo_root.anchor or Path.home().anchor
        if anchor:
            roots.add(Path(anchor))
    else:
        roots.add(Path("/"))
    return tuple(roots)


def _load_paths_from_files(files: Iterable[str]) -> List[str]:
    collected: List[str] = []
    for file_path in files:
        candidate = Path(file_path)
        try:
            text = candidate.read_text(encoding="utf-8")
        except OSError as exc:
            raise ValueError(f"Failed reading {candidate}: {exc}") from exc
        for line in text.splitlines():
            stripped = line.strip()
            if stripped:
                collected.append(stripped)
    return collected


def _load_paths_from_stdin() -> List[str]:
    data = sys.stdin.read()
    return [line.strip() for line in data.splitlines() if line.strip()]


def _dedupe_paths(paths: Sequence[Path]) -> List[Path]:
    ordered = OrderedDict()
    for path in paths:
        ordered.setdefault(path, None)
    return list(ordered.keys())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ded",
        description="Delete Empty Dirs safely and interactively.",
    )
    parser.add_argument("paths", nargs="*", help="Paths to check for empty directories.")
    parser.add_argument(
        "--from-file",
        "-f",
        action="append",
        default=[],
        dest="from_file",
        metavar="PATH",
        help="Read newline-delimited paths from this file (can repeat).",
    )
    parser.add_argument("--stdin", action="store_true", help="Read newline-delimited paths from stdin.")
    parser.add_argument("--follow-symlinks", action="store_true", help="Follow directory symlinks.")
    parser.add_argument("--no-dedupe", action="store_true", help="Process duplicate paths exactly as provided.")
    parser.add_argument(
        "--restrict-to",
        action="append",
        default=[],
        dest="restrict_to",
        metavar="PATH",
        help="Only allow deletions within this subtree (can repeat).",
    )
    parser.add_argument(
        "--allow-root",
        action="append",
        default=[],
        dest="allow_root",
        metavar="PATH",
        help="Explicitly allow deleting this exact protected root path.",
    )
    parser.add_argument("--workers", type=int, default=None, metavar="INT", help="Number of worker threads to use.")
    parser.add_argument("--log", dest="log_path", metavar="PATH", help="Write JSONL log to this path.")
    parser.add_argument("--no-log", action="store_true", help="Disable JSONL logging.")
    parser.add_argument("--no-rich", action="store_true", help="Disable live Rich UI.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary to stdout at the end.")
    parser.add_argument("-q", "--quiet", action="store_true", help="Reduce output to essential information.")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase verbosity (can repeat).")
    parser.add_argument("--version", action="version", version=__version__)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:  # pragma: no cover - argparse behaviour
        return exc.code

    if not args.paths and not args.from_file and not args.stdin:
        parser.print_usage(sys.stderr)
        print("ded: error: no paths provided", file=sys.stderr)
        return 2

    raw_paths: List[str] = list(args.paths)

    try:
        if args.from_file:
            raw_paths.extend(_load_paths_from_files(args.from_file))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.stdin:
        raw_paths.extend(_load_paths_from_stdin())

    processed_paths: List[Path] = []
    invalid_inputs: List[str] = []

    for raw in raw_paths:
        try:
            processed_paths.append(normalise_path(raw))
        except (ValueError, OSError):
            invalid_inputs.append(raw)

    if not args.no_dedupe:
        processed_paths = _dedupe_paths(processed_paths)

    if not processed_paths and not invalid_inputs:
        print("ded: error: no valid paths to process", file=sys.stderr)
        return 2

    repo_root = _detect_repo_root(Path.cwd())
    protected_roots = tuple(_compute_protected_roots(repo_root))
    allow_roots = tuple(normalise_path(str(p)) for p in args.allow_root)
    restrict_roots = tuple(normalise_path(str(p)) for p in args.restrict_to)

    worker_count = args.workers or min(32, (os.cpu_count() or 4) * 4)
    if worker_count <= 0:
        worker_count = 1

    console = make_console()
    stdout_tty = bool(getattr(sys.stdout, "isatty", lambda: False)())
    is_tty = bool(getattr(console, "is_terminal", False)) and stdout_tty
    verbosity = -1 if args.quiet else args.verbose
    use_rich = is_tty and not args.no_rich

    total_paths = len(processed_paths) + len(invalid_inputs)
    renderer = create_renderer(console=console, use_rich=use_rich, total=total_paths, verbosity=verbosity)

    log_context = build_log_context()
    logger: JsonlLogger | None = None
    chosen_log_path: Path | None = None

    if not args.no_log:
        chosen_log_path = normalise_path(args.log_path) if args.log_path else default_log_path()
        try:
            logger = JsonlLogger(chosen_log_path)
            logger.open()
        except OSError:
            fallback = fallback_log_path()
            logger = JsonlLogger(fallback)
            logger.open()
            chosen_log_path = fallback

    settings = ExecutionSettings(
        follow_symlinks=args.follow_symlinks,
        restrict_to=restrict_roots,
        allow_roots=allow_roots,
        protected_roots=protected_roots,
        repo_root=repo_root,
    )

    totals = None
    elapsed = 0.0

    try:
        with renderer:
            for idx, path in enumerate(processed_paths):
                renderer.on_enqueue(idx, path)
            for idx, raw in enumerate(invalid_inputs, start=len(processed_paths)):
                renderer.on_enqueue(idx, raw)

            for idx, raw in enumerate(invalid_inputs, start=len(processed_paths)):
                dummy = PathResult(
                    index=idx,
                    path=raw,
                    exists=False,
                    is_dir=False,
                    entries_count=-1,
                    status=ResultStatus.SKIPPED,
                    reason=SkipReason.INVALID_PATH,
                    message="Path string could not be normalised",
                )
                renderer.on_result(dummy)
                if logger:
                    logger.write(dummy.to_log_record(**log_context))

            def collect(res: PathResult) -> None:
                renderer.on_result(res)
                if logger:
                    logger.write(res.to_log_record(**log_context))

            _, totals, elapsed = process_paths(
                processed_paths,
                settings,
                workers=worker_count,
                callback=collect,
            )

            processed_total = totals.total + len(invalid_inputs)
            renderer.on_complete(
                processed=processed_total,
                deleted=totals.deleted,
                skipped=totals.skipped + len(invalid_inputs),
                errors=totals.errors,
                elapsed=elapsed,
            )

    except KeyboardInterrupt:  # pragma: no cover - interactive interruption
        console.print("[red]Interrupted by user.[/red]")
        if logger:
            logger.close()
        return 1
    finally:
        if logger:
            logger.close()

    if totals is None:
        return 1

    if args.json:
        summary = {
            "total": len(processed_paths) + len(invalid_inputs),
            "deleted": totals.deleted,
            "skipped": totals.skipped + len(invalid_inputs),
            "errors": totals.errors,
            "log_path": str(chosen_log_path) if chosen_log_path else None,
        }
        console.print(json.dumps(summary))

    return 1 if totals.errors > 0 else 0


def main_entry() -> None:
    sys.exit(main())


if __name__ == "__main__":  # pragma: no cover
    main_entry()
