from __future__ import annotations

import errno
import os
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Sequence, Tuple

from .models import PathResult, ProcessingTotals, ResultStatus, SkipReason


@dataclass(frozen=True)
class ExecutionSettings:
    """Execution wide configuration for processing paths."""

    follow_symlinks: bool
    restrict_to: Tuple[Path, ...]
    allow_roots: Tuple[Path, ...]
    protected_roots: Tuple[Path, ...]
    repo_root: Path


def normalise_path(raw: str) -> Path:
    """Normalise incoming raw path strings to absolute Paths without forcing symlink resolution."""
    expanded = os.path.expandvars(raw)
    expanded = os.path.expanduser(expanded)
    path = Path(expanded)
    if not path.is_absolute():
        joined = os.path.join(os.getcwd(), str(path))
        return Path(os.path.abspath(joined))
    return Path(os.path.abspath(str(path)))


def _is_protected_root(path: Path, settings: ExecutionSettings) -> bool:
    path_canonical = _canonical(path)
    allowed = {_canonical(p) for p in settings.allow_roots}
    if path_canonical in allowed:
        return False
    protected = {_canonical(p) for p in settings.protected_roots}
    if path_canonical in protected:
        return True
    if path_canonical == _canonical(settings.repo_root):
        return True
    anchor = Path(path.anchor) if path.anchor else None
    if anchor and path_canonical == _canonical(anchor):
        return True
    home = _canonical(Path.home())
    if path_canonical == home:
        return True
    return False


def _canonical(path: Path) -> Path:
    try:
        return path.resolve(strict=False)
    except OSError:
        return Path(os.path.abspath(str(path)))


def _is_within_restrict(path: Path, restrict_to: Tuple[Path, ...]) -> bool:
    if not restrict_to:
        return True
    path_c = _canonical(path)
    for root in restrict_to:
        root_c = _canonical(root)
        try:
            if path_c.is_relative_to(root_c):
                return True
        except AttributeError:
            # Python <3.9 fallback
            try:
                path_c.relative_to(root_c)
                return True
            except ValueError:
                continue
    return False


def _scan_directory(path: Path) -> Tuple[int, Optional[SkipReason], Optional[str]]:
    """Return entry count limited to first item. If error, return -1 and reason."""
    entries = 0
    try:
        with os.scandir(path) as it:
            for _ in it:
                entries += 1
                if entries > 0:
                    break
    except PermissionError as exc:
        return -1, SkipReason.PERMISSION_DENIED, str(exc)
    except FileNotFoundError:
        return -1, SkipReason.NOT_EXISTS, "Directory no longer exists"
    except NotADirectoryError as exc:
        return -1, SkipReason.NOT_DIR, str(exc)
    except OSError as exc:
        return -1, SkipReason.IO_ERROR, str(exc)
    return entries, None, None


def _prepare_target(path: Path, settings: ExecutionSettings) -> Tuple[Path, Optional[Path], bool]:
    """Return the directory to operate on, optional resolved target for symlinks, and bool is_symlink."""
    try:
        is_symlink = path.is_symlink()
    except OSError:
        is_symlink = False

    if is_symlink:
        try:
            resolved = path.resolve(strict=False)
        except OSError:
            resolved = path
    else:
        resolved = None

    if is_symlink and not settings.follow_symlinks:
        return path, resolved, True
    if is_symlink and resolved is not None:
        return resolved, resolved, True
    return path, None, False


def _evaluate_path(index: int, path: Path, settings: ExecutionSettings) -> PathResult:
    start = time.perf_counter()
    result = PathResult(index=index, path=path)

    try:
        path.lstat()
        result.exists = True
    except FileNotFoundError:
        result.reason = SkipReason.NOT_EXISTS
        result.status = ResultStatus.SKIPPED
        result.duration_ms = (time.perf_counter() - start) * 1000
        return result
    except OSError as exc:
        result.reason = SkipReason.IO_ERROR
        result.status = ResultStatus.ERROR
        result.message = str(exc)
        result.duration_ms = (time.perf_counter() - start) * 1000
        return result

    try:
        result.is_dir = path.is_dir()
    except OSError:
        result.is_dir = False

    try:
        result.is_symlink = path.is_symlink()
    except OSError:
        result.is_symlink = False

    if not result.is_dir and not (result.is_symlink and settings.follow_symlinks):
        result.reason = SkipReason.NOT_DIR
        result.status = ResultStatus.SKIPPED
        result.duration_ms = (time.perf_counter() - start) * 1000
        return result

    target, resolved, is_symlink = _prepare_target(path, settings)

    if is_symlink and not settings.follow_symlinks:
        result.reason = SkipReason.SYMLINK_DIR_REFUSED
        result.status = ResultStatus.SKIPPED
        result.duration_ms = (time.perf_counter() - start) * 1000
        return result

    effective_path = target

    if not _is_within_restrict(effective_path, settings.restrict_to):
        result.reason = SkipReason.POLICY_BLOCKED
        result.status = ResultStatus.SKIPPED
        result.message = "Outside allowed restrict-to roots"
        result.duration_ms = (time.perf_counter() - start) * 1000
        return result

    if _is_protected_root(effective_path, settings):
        result.reason = SkipReason.PROTECTED_ROOT
        result.status = ResultStatus.SKIPPED
        result.duration_ms = (time.perf_counter() - start) * 1000
        return result

    entries, reason, message = _scan_directory(effective_path)
    result.entries_count = entries
    if reason:
        result.reason = reason
        if reason == SkipReason.IO_ERROR:
            result.status = ResultStatus.ERROR
        elif reason == SkipReason.PERMISSION_DENIED:
            result.status = ResultStatus.SKIPPED
        elif reason == SkipReason.NOT_EXISTS:
            result.exists = False
            result.status = ResultStatus.SKIPPED
        else:
            result.status = ResultStatus.SKIPPED
        result.message = message
        result.duration_ms = (time.perf_counter() - start) * 1000
        return result

    if entries > 0:
        result.reason = SkipReason.NOT_EMPTY
        result.status = ResultStatus.SKIPPED
        result.duration_ms = (time.perf_counter() - start) * 1000
        return result

    result.empty_verified = True

    try:
        effective_path.rmdir()
        result.deleted = True
        result.status = ResultStatus.DELETED
        if is_symlink and resolved and resolved != path:
            result.message = f"Deleted symlink target: {resolved}"
    except FileNotFoundError:
        result.reason = SkipReason.NOT_EXISTS
        result.exists = False
        result.status = ResultStatus.ERROR
        result.message = "Directory disappeared before deletion"
    except PermissionError as exc:
        result.status = ResultStatus.ERROR
        result.reason = SkipReason.PERMISSION_DENIED
        result.message = str(exc)
    except OSError as exc:
        result.status = ResultStatus.ERROR
        result.reason = SkipReason.IO_ERROR
        result.message = str(exc)
        if getattr(exc, "errno", None) == errno.ENOTEMPTY:
            result.message = "Directory not empty at deletion time"

    result.duration_ms = (time.perf_counter() - start) * 1000
    return result


def process_paths(
    paths: Sequence[Path],
    settings: ExecutionSettings,
    *,
    workers: int,
    callback: Optional[Callable[[PathResult], None]] = None,
) -> Tuple[List[PathResult], ProcessingTotals, float]:
    """Process paths concurrently and return results, totals, and elapsed seconds."""
    start = time.perf_counter()
    totals = ProcessingTotals()
    results: List[PathResult] = []

    def handle_result(res: PathResult) -> None:
        results.append(res)
        totals.update(res)
        if callback:
            callback(res)

    with ThreadPoolExecutor(max_workers=max(workers, 1)) as executor:
        futures: List[Future[PathResult]] = [
            executor.submit(_evaluate_path, idx, path, settings) for idx, path in enumerate(paths)
        ]
        for future in as_completed(futures):
            res = future.result()
            handle_result(res)

    elapsed = time.perf_counter() - start
    return results, totals, elapsed
