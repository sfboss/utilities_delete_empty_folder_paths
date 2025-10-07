from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union

try:
    from rich import box
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn
    from rich.table import Table
    from rich.text import Text

    HAS_RICH = True
except ImportError:  # pragma: no cover - optional dependency
    box = None
    Console = None  # type: ignore
    Layout = None  # type: ignore
    Live = None  # type: ignore
    Panel = None  # type: ignore
    Progress = None  # type: ignore
    Text = None  # type: ignore
    BarColumn = TextColumn = TimeElapsedColumn = None  # type: ignore
    HAS_RICH = False

from .models import PathResult, ResultStatus


class FallbackConsole:
    """Minimal console with Rich-like API."""

    def __init__(self) -> None:
        self._terminal = bool(getattr(sys.stdout, "isatty", lambda: False)())

    @property
    def is_terminal(self) -> bool:
        return self._terminal

    def print(self, *args, **kwargs) -> None:
        print(*args, **kwargs)


class BaseRenderer:
    """Shared renderer interface for Rich and plain output modes."""

    def __enter__(self) -> "BaseRenderer":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def on_enqueue(self, index: int, path: Union[Path, str]) -> None:
        raise NotImplementedError

    def on_result(self, result: PathResult) -> None:
        raise NotImplementedError

    def on_complete(self, *, processed: int, deleted: int, skipped: int, errors: int, elapsed: float) -> None:
        raise NotImplementedError


if HAS_RICH:

    class RichRenderer(BaseRenderer):
        """Interactive Rich renderer with live-updating table and progress."""

        def __init__(self, console: Console, total: int, app_name: str = "Delete Empty Dirs") -> None:
            self.console = console
            self.total = total
            self.app_name = app_name
            self.start_time = datetime.now()
            self._rows: Dict[int, Dict[str, str]] = {}
            self._processed = 0
            self._deleted = 0
            self._skipped = 0
            self._errors = 0
            self._live: Optional[Live] = None
            self._progress = Progress(
                TextColumn("[bold blue]Progress"),
                BarColumn(),
                TextColumn("{task.completed}/{task.total}"),
                TimeElapsedColumn(),
                expand=True,
            )
            self._task_id = self._progress.add_task("paths", total=total)

        def __enter__(self) -> "RichRenderer":
            self._progress.start()
            self._live = Live(self._render_layout(), refresh_per_second=10, console=self.console)
            self._live.__enter__()
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            if self._live:
                self._live.__exit__(exc_type, exc, tb)
            self._progress.stop()

        def _render_header(self) -> Panel:
            header_text = Text()
            header_text.append(f"{self.app_name}\n", style="bold white")
            header_text.append(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}", style="dim")
            return Panel(header_text, style="bold green", padding=(1, 2))

        def _build_table(self) -> Table:
            table = Table(box=box.SIMPLE_HEAVY, expand=True)
            table.add_column("Index", justify="right", style="cyan", no_wrap=True)
            table.add_column("Path", overflow="fold")
            table.add_column("Exists", justify="center", style="dim")
            table.add_column("Dir", justify="center", style="dim")
            table.add_column("Entries", justify="center")
            table.add_column("Empty?", justify="center")
            table.add_column("Action", justify="center")
            table.add_column("Reason/Err", overflow="fold")

            for idx in sorted(self._rows):
                row = self._rows[idx]
                table.add_row(
                    str(idx + 1),
                    row.get("path", ""),
                    row.get("exists", ""),
                    row.get("dir", ""),
                    row.get("entries", ""),
                    row.get("empty", ""),
                    row.get("action", ""),
                    row.get("reason", ""),
                )
            return table

        def _build_footer(self) -> Panel:
            remaining = max(self.total - self._processed, 0)
            stats = Text()
            stats.append(f"Deleted: {self._deleted}  ", style="green")
            stats.append(f"Skipped: {self._skipped}  ", style="yellow")
            stats.append(f"Errors: {self._errors}  ", style="red")
            stats.append(f"Remaining: {remaining}", style="white")
            self._progress.update(self._task_id, completed=self._processed)
            footer_layout = Layout()
            footer_layout.split_row(
                Layout(self._progress, ratio=2),
                Layout(Panel(stats, border_style="blue"), ratio=1),
            )
            return Panel(footer_layout, padding=0, border_style="blue")

        def _render_layout(self) -> Layout:
            layout = Layout()
            layout.split_column(
                Layout(self._render_header(), size=3),
                Layout(self._build_table(), ratio=2),
                Layout(self._build_footer(), size=5),
            )
            return layout

        def _refresh(self) -> None:
            if self._live:
                self._live.update(self._render_layout(), refresh=True)

        def on_enqueue(self, index: int, path: Union[Path, str]) -> None:
            self._rows[index] = {
                "path": str(path),
                "exists": "...",
                "dir": "...",
                "entries": "...",
                "empty": "...",
                "action": "[cyan]queued",
                "reason": "",
            }
            self._refresh()

        def on_result(self, result: PathResult) -> None:
            self._processed += 1
            if result.status == ResultStatus.DELETED:
                self._deleted += 1
                action = "[green]deleted ✓"
            elif result.status == ResultStatus.ERROR:
                self._errors += 1
                action = "[red]error ✗"
            else:
                self._skipped += 1
                action = "[yellow]skipped △"

            row = self._rows.setdefault(result.index, {})
            row.update(
                {
                    "path": str(result.path),
                    "exists": "yes" if result.exists else "no",
                    "dir": "yes" if result.is_dir else ("symlink" if result.is_symlink else "no"),
                    "entries": str(result.entries_count if result.entries_count >= 0 else "?"),
                    "empty": "yes" if result.empty_verified else "no",
                    "action": action,
                    "reason": (result.reason.value if result.reason else "") or (result.message or ""),
                }
            )
            self._refresh()

        def on_complete(self, *, processed: int, deleted: int, skipped: int, errors: int, elapsed: float) -> None:
            footer_note = Text()
            footer_note.append(f"Processed: {processed}  ", style="bold white")
            footer_note.append(f"Deleted: {deleted}  ", style="green")
            footer_note.append(f"Skipped: {skipped}  ", style="yellow")
            footer_note.append(f"Errors: {errors}  ", style="red")
            footer_note.append(f"Elapsed: {elapsed:.2f}s", style="bold blue")
            if self._live:
                self._live.update(self._render_layout())
            self.console.print(Panel(footer_note, title="Summary", border_style="green"))
else:  # pragma: no cover - optional dependency
    RichRenderer = None  # type: ignore


class PlainRenderer(BaseRenderer):
    """Line-by-line output intended for non-TTY usage."""

    def __init__(self, console, verbosity: int = 0) -> None:
        self.console = console
        self.verbosity = verbosity

    def on_enqueue(self, index: int, path: Union[Path, str]) -> None:
        if self.verbosity > 0:
            self.console.print(f"[queued] {index+1}\t{path}")

    def on_result(self, result: PathResult) -> None:
        symbol = {
            ResultStatus.DELETED: "[green]deleted",
            ResultStatus.ERROR: "[red]error",
            ResultStatus.SKIPPED: "[yellow]skipped",
        }[result.status]
        extras = []
        if result.reason:
            extras.append(result.reason.value)
        if result.message:
            extras.append(result.message)
        detail = " | ".join(extras)
        if self.verbosity <= -1 and result.status == ResultStatus.SKIPPED:
            return
        self.console.print(f"{symbol}\t{result.path}\t{detail}")

    def on_complete(self, *, processed: int, deleted: int, skipped: int, errors: int, elapsed: float) -> None:
        self.console.print(
            f"Summary: processed={processed} deleted={deleted} skipped={skipped} errors={errors} elapsed={elapsed:.2f}s"
        )


def create_renderer(
    *,
    console,
    use_rich: bool,
    total: int,
    verbosity: int,
) -> BaseRenderer:
    """Factory returning a renderer appropriate for the current environment."""
    if use_rich and HAS_RICH:
        return RichRenderer(console=console, total=total)
    return PlainRenderer(console=console, verbosity=verbosity)


def make_console():
    """Return a Console-compatible object."""
    if HAS_RICH:
        return Console()
    return FallbackConsole()
