from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Union


class ResultStatus(str, Enum):
    """High level outcomes for processing a path."""

    DELETED = "deleted"
    SKIPPED = "skipped"
    ERROR = "error"


class SkipReason(str, Enum):
    """Reasons why a path was skipped or otherwise not deleted."""

    NOT_EXISTS = "not_exists"
    NOT_DIR = "not_dir"
    NOT_EMPTY = "not_empty"
    PERMISSION_DENIED = "permission_denied"
    IO_ERROR = "io_error"
    SYMLINK_DIR_REFUSED = "symlink_dir_refused"
    PROTECTED_ROOT = "protected_root"
    POLICY_BLOCKED = "policy_blocked"
    INVALID_PATH = "invalid_path"


@dataclass(slots=True)
class PathResult:
    """Structured result emitted for each processed path."""

    index: int
    path: Union[Path, str]
    exists: bool = False
    is_dir: bool = False
    is_symlink: bool = False
    entries_count: int = -1
    empty_verified: bool = False
    deleted: bool = False
    status: ResultStatus = ResultStatus.SKIPPED
    reason: Optional[SkipReason] = None
    message: Optional[str] = None
    duration_ms: float = 0.0
    ts: datetime = field(default_factory=datetime.utcnow)

    def to_log_record(self, pid: int, host: str, cwd: str) -> dict:
        """Convert result into JSON-serialisable dict for durable logging."""
        return {
            "path": str(self.path),
            "exists": self.exists,
            "is_dir": self.is_dir,
            "is_symlink": self.is_symlink,
            "entries_count": self.entries_count,
            "empty_verified": self.empty_verified,
            "deleted": self.deleted,
            "status": self.status.value,
            "reason": self.reason.value if self.reason else None,
            "duration_ms": self.duration_ms,
            "ts": self.ts.isoformat() + "Z",
            "pid": pid,
            "host": host,
            "cwd": cwd,
            "message": self.message,
        }


@dataclass(slots=True)
class ProcessingTotals:
    """Mutable totals for summarising run progress."""

    total: int = 0
    deleted: int = 0
    skipped: int = 0
    errors: int = 0

    def update(self, result: PathResult) -> None:
        self.total += 1
        if result.status == ResultStatus.DELETED:
            self.deleted += 1
        elif result.status == ResultStatus.ERROR:
            self.errors += 1
        else:
            self.skipped += 1
