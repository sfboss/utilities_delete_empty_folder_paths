AGENTS.md — Delete Empty Folder Paths CLI

Purpose and Scope

- Goal: Implement a fast, safe CLI that ingests one or more folder paths and permanently deletes only those directories that are truly empty (including hidden files). Non-empty, inaccessible, or invalid paths are skipped and reported. The CLI must provide an in-place, live-updating table UI (Rich-style) and a durable log capturing what was verified as empty and what was skipped, with reasons.
- Non‑negotiable rule: No deletions occur unless emptiness is positively verified at the moment of deletion. Hidden files count as contents. No “dry run” mode is required; the “validation rule” is the safety gate.
- Audience: Agents implementing the CLI, writing tests, and shipping a minimal package for local use.
- Language: Python 3.9+ (Rich ecosystem is mature and portable). If a different language is chosen, you must match the CLI contract, safety rules, and UX described below.

High-Level Requirements

- Input sources
  - Positional arguments: one or more paths.
  - Optional: read newline-delimited paths from a file via `--from-file PATH`.
  - Optional: read newline-delimited paths from STDIN when `--stdin` is supplied.
  - Deduplicate paths unless `--no-dedupe` is set.
- Emptiness validation
  - A directory is considered empty only if it contains zero entries when enumerated with `os.scandir()` using `follow_symlinks=False`.
  - Hidden files (e.g., dotfiles, .DS_Store), symlinks, and special files count as contents. If any entry exists, the directory is NOT empty.
  - Symlinked directories should be skipped by default with reason `symlink_dir_refused` unless `--follow-symlinks` is provided. If following, the same emptiness rule applies to the real target.
- Deletion behavior
  - Delete only with `Path.rmdir()` (or equivalent) so the OS enforces emptiness at deletion time. Never perform recursive deletion.
  - If verification says empty but `rmdir` fails, record the error and mark as `error` (don’t retry by default).
  - Absolutely refuse to delete critical roots (denylist): `/`, user home, drive roots on Windows (e.g., `C:\`, `D:\`). Also refuse the repository root by default; allow override via `--allow-root PATH`.
- Output and UX
  - Provide a live, in-place updating table using Rich (`rich.live.Live`) that resembles but does not clone the screenshot’s style.
  - Columns: `Index`, `Path`, `Exists`, `Dir`, `Entries`, `Empty?`, `Action`, `Reason/Err`.
  - Show a progress bar and running totals (Deleted, Skipped, Errors, Remaining). Update as each item is processed.
  - If stdout is not a TTY or `--no-rich` is set, fall back to plain line-by-line logs and a final summary.
- Logging and auditability
  - Write a durable log by default to `.project_logs/empty_delete_<timestamp>.jsonl` (create directory if missing). Allow override via `--log PATH`. Add `--no-log` to disable.
  - Log schema (JSON Lines):
    - `path` (string, normalized, absolute)
    - `exists` (bool)
    - `is_dir` (bool)
    - `is_symlink` (bool)
    - `entries_count` (int, -1 if unknown due to error)
    - `empty_verified` (bool)
    - `deleted` (bool)
    - `status` (enum: `deleted`, `skipped`, `error`)
    - `reason` (nullable enum: `not_exists`, `not_dir`, `not_empty`, `permission_denied`, `io_error`, `symlink_dir_refused`, `protected_root`, `policy_blocked`, `invalid_path`)
    - `duration_ms` (number)
    - `ts` (ISO8601 string)
    - `pid` (int), `host` (string), `cwd` (string)
  - Rationale: The user wants proof that an empty directory was actually verified and removed; `entries_count` and `empty_verified` capture that moment-in-time evidence.
- Summary and exit codes
  - Print a final summary with totals: `total`, `deleted`, `skipped`, `errors`, and elapsed time.
  - Exit code `0` if no errors, `1` if any `error` occurred, `2` for invalid CLI usage.

CLI Contract

Command name

- Package name: `delete-empty-dirs` (internal module `delete_empty_dirs`).
- Console script: `ded` (short) and `delete-empty-dirs` (long). Both point to the same entrypoint.

Usage

`ded [OPTIONS] [PATHS]...`

Options

- `--from-file PATH` Read newline-delimited paths from file.
- `--stdin` Read newline-delimited paths from STDIN.
- `--follow-symlinks` Follow directory symlinks (default: skip with reason).
- `--no-dedupe` Process duplicate paths as provided (default: dedupe by normalized absolute path).
- `--restrict-to PATH` Only allow deletions within this subtree (policy guard). Multiple allowed.
- `--allow-root PATH` Explicitly allow deleting the exact provided path if it would otherwise be considered a protected root.
- `--workers INT` Number of worker threads for validation/deletion. Default: auto (min(32, os.cpu_count()*4)).
- `--log PATH` Write JSONL log here (default path if not provided).
- `--no-log` Disable logging.
- `--no-rich` Disable the live UI; use plain output.
- `--json` Emit a machine-readable JSON summary to stdout at the end.
- `--version` Show version and exit.
- `-q/--quiet`, `-v/--verbose` Adjust verbosity.

Examples

- Delete empty directories passed as args: `ded ~/tmp/empty1 ~/tmp/empty2`.
- From file: `ded --from-file to_delete.txt`.
- From STDIN: `cat paths.txt | ded --stdin`.
- Strict subtree: `ded --restrict-to ~/projects ./paths_to_check.txt`.
- Plain mode without Rich: `ded --no-rich --log deletions.jsonl --from-file paths.txt`.

Behavioral Details and Edge Cases

- Path normalization: Expand `~`, env vars, relative paths; resolve to absolute with `Path.resolve(strict=False)`. Do not follow symlinks unless requested.
- Nonexistent path: skip with reason `not_exists`.
- Not a directory: skip with reason `not_dir`.
- Permission denied on listing: skip with reason `permission_denied`.
- I/O error (e.g., transient): mark as `error` with captured message.
- Directory becomes non-empty between check and `rmdir`: `rmdir` will fail; record as `error` with message `Directory not empty`.
- Windows considerations: handle `OSError` `Access is denied`; ensure path length support via `\\?\` when needed (Rich display uses the human path). Do not attempt attribute toggles; if it fails, record the error.
- Unicode paths: always handle/print safely; avoid truncating in logs, but visually truncate in table columns with Rich as needed.
- Protected roots: always deny `/`, drive roots, and home directory. If the exact path equals a protected root, skip with `protected_root` unless explicitly allowed via `--allow-root PATH` matching exactly.

UX and TUI Design (Rich)

- Use `rich.live.Live` with `refresh_per_second=10` and a layout containing:
  - A header panel with the app name and run start time.
  - Center table with columns: `#`, `Path`, `Exists`, `Dir`, `Entries`, `Empty?`, `Action`, `Reason/Err`.
  - A bottom progress panel showing a progress bar, processed count, and totals.
- Row updates
  - On enqueue: show `Action=queued`.
  - After scan: set `Exists`, `Dir`, `Entries`, `Empty?`.
  - On decision: set `Action=delete` or `skip`, and optionally color the row (green for delete, yellow for skip, red for error).
  - After attempt: finalize `Action=deleted` or `Action=error` and fill `Reason/Err` if applicable.
- Color and icons
  - Deleted: green checkmark; Skipped: yellow triangle; Error: red cross.
  - Keep the theme similar in spirit to the screenshot, but unique in layout and palette.
- Fallback
  - When not a TTY or `--no-rich`, print compact lines: `STATUS	PATH	DETAILS` and a final summary block.

Architecture

- Package layout (src layout)
  - `src/delete_empty_dirs/__init__.py`
  - `src/delete_empty_dirs/cli.py` (Typer or Click CLI)
  - `src/delete_empty_dirs/core.py` (validation + delete logic)
  - `src/delete_empty_dirs/render.py` (Rich table/live UI)
  - `src/delete_empty_dirs/models.py` (dataclasses/enums for statuses, results)
  - `src/delete_empty_dirs/logging_utils.py` (JSONL logging and helpers)
  - `src/delete_empty_dirs/version.py`
- Third-party dependencies
  - `rich` for UI
  - `typer` (preferred) or `click` for CLI
  - `platformdirs` for default log directory resolution
- Concurrency
  - Use `concurrent.futures.ThreadPoolExecutor` for path checks/deletions; I/O-bound and simple syscalls benefit from threads.
  - Ensure UI updates are marshaled to the main thread; workers return events to a queue processed by the UI loop.
- Data flow
  1) Resolve inputs → normalize → apply policy guards (denylist, `--restrict-to`).
  2) Enqueue jobs for workers.
  3) Worker validates emptiness and attempts deletion if empty.
  4) Main thread updates UI and writes JSONL entries.
  5) On completion, print summary and exit with proper code.

Models (suggested)

- `ResultStatus`: `deleted`, `skipped`, `error`.
- `SkipReason`: as listed in log schema.
- `PathResult` dataclass:
  - fields matching the JSON schema plus `index` and `message` (error text).

Testing Strategy

- Use `pytest`.
- Unit tests for `core.is_empty(path)` with cases: truly empty, file present, hidden file present, symlink present, permission denied (use tmp dirs + monkeypatch), symlinked dir refused, symlinked dir followed.
- Unit tests for deletion policy guards (protected roots, restrict-to).
- Integration tests for CLI: feed paths via args, file, and stdin; assert exit codes and JSONL content.
- Snapshot-style test for plain output mode (`--no-rich`). Do not test Rich visuals pixel-by-pixel; instead verify that updates occur and final summary content is present.

Performance and Limits

- Target: comfortably process 50k paths within a minute on a typical dev machine with default worker count, assuming normal FS latency and most paths nonexistent or already non-empty.
- Ensure minimal per‑path allocations; use `os.scandir()` for listing and short-circuit after the first found entry.

Security and Safety

- Never recurse; never call `rmtree`.
- Enforce denylist and `--restrict-to` boundaries before any delete attempt.
- Treat symlinks conservatively by default.
- Handle concurrent modifications gracefully and record accurate outcomes.

Developer Workflow

- Environment: Python 3.11 recommended; create venv.
- Dependencies: `pip install -e .[dev]` with extras: `rich`, `typer`, `platformdirs`, `pytest`.
- Run: `delete-empty-dirs --help` or `ded --help`.
- Lint/format: Use `ruff` and `black` if available; keep changes minimal and in-repo.

Definition of Done

- All CLI options implemented as specified.
- Live table works in TTY; plain output in non-TTY.
- JSONL log written by default with fields above; `entries_count` reflects verification time; `empty_verified=true` when deletion attempted.
- Correct totals and exit codes.
- Tests cover core logic and main CLI flows; CI job (optional) runs tests.

Implementation Plan (step-by-step)

1) Scaffold package structure and CLI with Typer; wire `--version`.
2) Implement protected roots and `--restrict-to` policy guards.
3) Implement `is_empty(path)` using `os.scandir()`; add symlink handling.
4) Implement worker pipeline: validate → delete → return `PathResult`.
5) Implement JSONL logger and log schema.
6) Implement Rich UI (`render.py`) with live table + progress + summary.
7) Implement plain output fallback and `--json` final summary.
8) Integrate inputs from args, `--from-file`, and `--stdin`; add dedupe.
9) Wire concurrency and UI updates safely; ensure graceful shutdown on Ctrl+C.
10) Add tests; verify exit codes and logs.
11) Polish messages, colors, and examples; update README.

Coding Conventions

- Use `pathlib.Path` for paths; convert to absolute early.
- Keep functions small and pure where possible; no global state other than constants.
- Avoid inline prints in workers; return data to the main thread.
- Type annotate public functions; enable `from __future__ import annotations` when using Python 3.11.

Open Questions (log answers in PROJECT_LOG.md as decisions)

- Should we add an allowlist for ignorable clutter files (e.g., `.DS_Store`)? Default is strict “no entries at all”. If added, must be opt-in via `--ignore NAME` with explicit names.
- Do we need a CSV reader for path lists (selectable column)? Default is newline-delimited only.
- Do we need per‑path confirmation? Default is non-interactive. If added, it must time out and default to skip.

Notes for Future Enhancements

- Optional metrics export (Prometheus textfile) with totals.
- Optional `--retries` for transient I/O errors.
- Optional `--summary-table` write to Markdown.

Attribution and License

- Do not add license headers to files unless requested.
- Keep the UI theming unique; do not copy third‑party screenshots or styles verbatim.
