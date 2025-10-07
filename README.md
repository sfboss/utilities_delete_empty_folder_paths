# Delete Empty Dirs (`ded`)

Safe, auditable command-line utility for removing directories only when they are truly empty. Designed for large batches of folder checks with a live Rich UI, durable JSONL logging, and cautious safety guards around symlinks, protected roots, and policy boundaries.

## Key Features

- Verifies emptiness with `os.scandir()` (no recursion); deletes via `Path.rmdir()` only after a fresh empty check.
- Rich-powered live table with progress, per-path status, and color-coded outcomes; automatic fallback to plain logs when Rich is disabled or stdout is not a TTY.
- Threaded validation/deletion pipeline (configurable via `--workers`) to comfortably handle tens of thousands of paths.
- Durable JSONL audit log (`.project_logs/empty_delete_<timestamp>.jsonl` by default) capturing per-path evidence: entry counts, verification state, reason codes, host metadata, and timings.
- Policy guardrails: protected roots (`/`, home directory, repository root, drive anchors) and optional `--restrict-to` subtrees; explicit overrides via `--allow-root`.
- Flexible inputs: positional arguments, newline-delimited files (`--from-file`), or STDIN (`--stdin`); deduplication by default with `--no-dedupe` escape hatch.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .[dev]
```

This project targets Python 3.9+. Rich and Platformdirs power the interactive UI and logging fallbacks; when they are missing, the CLI gracefully degrades to plain output and simple home-directory logging.

## Usage

Console scripts registered: `ded`, `delete-empty-dirs`, and `delete_empties`.

```bash
ded [OPTIONS] [PATHS]...
```

Common options:

| Option | Description |
| ------ | ----------- |
| `--from-file PATH` | Read newline-delimited paths from a file. |
| `--stdin` | Read newline-delimited paths from STDIN. |
| `--follow-symlinks` | Opt in to following directory symlinks. |
| `--no-dedupe` | Process duplicate paths exactly as provided. |
| `--restrict-to PATH` | Policy guard: only delete within this subtree (repeatable). |
| `--allow-root PATH` | Allow deleting a protected root exactly matching PATH. |
| `--workers INT` | Override worker count (default auto = `min(32, cpu_count*4)`). |
| `--log PATH` / `--no-log` | Custom log destination or disable logging. |
| `--no-rich` | Force plain output even when stdout is a TTY. |
| `--json` | Emit final JSON summary to stdout. |
| `-q/--quiet`, `-v/--verbose` | Adjust verbosity. |

### Safety Notes

- Hidden files, dot directories, and special files count as contents. Any entry prevents deletion.
- Symlinked directories are skipped by default (`symlink_dir_refused`). `--follow-symlinks` treats the real target as if it were provided directly.
- Critical roots are never deleted: filesystem root, user home, drive anchors on Windows, and the repository root. Use `--allow-root PATH` for explicit overrides.
- No recursive deletion is ever performed. If `Path.rmdir()` fails after verification, the directory is left intact and the failure recorded.

### Logging

Logs are written in JSON Lines format with the following schema:

```
path, exists, is_dir, is_symlink, entries_count, empty_verified,
deleted, status, reason, duration_ms, ts, pid, host, cwd, message
```

Set `--log PATH` to choose a location, `--no-log` to disable logging, or rely on the default `.project_logs/` directory. On IO errors while opening the default log, the CLI falls back to a user log directory (or the user home directory if Platformdirs is unavailable).

## Development

```bash
pip install -e .[dev]
python3 -m pytest
```

Tests cover core deletion logic (emptiness verification, policy guards, symlink handling) and CLI flows (file input, JSON summary). If `pytest` or other dependencies are not available in your environment, install them first via `pip install -e .[dev]`.

## CLI Screenshot

Text capture of the plain (non-Rich) mode for reference:

````text
$ delete_empties --no-rich --no-log /tmp/demo_empty /tmp/demo_nonempty
deleted    /tmp/demo_empty
skipped    /tmp/demo_nonempty    not_empty
Summary: processed=2 deleted=1 skipped=1 errors=0 elapsed=0.02s
````

The Rich-powered TUI shows the same information as a live-updating table with progress indicators when stdout is a TTY.

## VHS Recordings

Three tapes are provided in `recordings/` for generating GIF walkthroughs with [VHS](https://github.com/charmbracelet/vhs):

- `delete_empty_dirs_help.tape` – runs the CLI help with the default Dracula theme.
- `delete_empty_dirs_run.tape` – demonstrates deleting/keeping directories in plain mode.
- `delete_empty_dirs_aurora.tape` – uses the custom **Aurora Midnight** palette defined inline in the tape for a distinct aesthetic, captures deletion plus JSONL logging output.

Render any tape with:

```bash
vhs recordings/delete_empty_dirs_aurora.tape
```

Each tape writes its GIF to the same folder; feel free to tweak the theme colors further to match your brand.

### Template Gallery

Browse reusable themed templates under `templates/`. Each one references the project root placeholder (`{{PROJECT_ROOT}}`) so the commands stay portable:

- `nebula_overview.tape` – cosmic palette highlighting project discovery.
- `citrus_console.tape` – upbeat hues driving a quick empty/keep run.
- `noir_minimal.tape` – low-key monochrome focusing on policy checks.
- `forest_glow.tape` – biophilic vibe with JSONL logging showcase.
- `neon_grid.tape` – synthwave snapshot of help text and directory listings.

Render them individually after replacing the placeholder, or let the helper script handle that substitution for you (outputs default to `recordings/generated/`):

```bash
./templates/render_all.sh               # writes GIFs under recordings/generated
./templates/render_all.sh ~/Desktop/gif # custom destination
```
