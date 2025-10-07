from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from platformdirs import user_log_dir
except ImportError:  # pragma: no cover - optional dependency
    user_log_dir = None  # type: ignore

DEFAULT_LOG_DIR_NAME = ".project_logs"


def default_log_path(now: Optional[datetime] = None, cwd: Optional[Path] = None) -> Path:
    """Resolve the default JSONL log path under the project log directory."""
    now = now or datetime.utcnow()
    cwd = cwd or Path.cwd()
    log_dir = cwd / DEFAULT_LOG_DIR_NAME
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    return log_dir / f"empty_delete_{timestamp}.jsonl"


def fallback_log_path(app_name: str = "delete-empty-dirs") -> Path:
    """Fallback path when project directory is not writable."""
    if user_log_dir:
        log_dir = Path(user_log_dir(app_name, appauthor=False))
    else:
        log_dir = Path.home() / f".{app_name}"
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return log_dir / f"empty_delete_{timestamp}.jsonl"


class JsonlLogger:
    """Simple JSONL logger that flushes data to disk for durability."""

    def __init__(self, path: Path):
        self.path = path
        self._fp = None

    def __enter__(self) -> "JsonlLogger":
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def open(self) -> None:
        if self._fp is not None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fp = self.path.open("a", encoding="utf-8")

    def write(self, record: dict) -> None:
        if self._fp is None:
            raise RuntimeError("Logger not opened")
        json.dump(record, self._fp, ensure_ascii=False)
        self._fp.write("\n")
        self._fp.flush()
        os.fsync(self._fp.fileno())

    def close(self) -> None:
        if self._fp:
            self._fp.close()
            self._fp = None


def build_log_context() -> dict:
    """Common host/process metadata included with every log record."""
    return {
        "pid": os.getpid(),
        "host": os.uname().nodename,
        "cwd": str(Path.cwd()),
    }
