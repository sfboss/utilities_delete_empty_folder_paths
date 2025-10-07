import json
import os
import subprocess
import sys
from pathlib import Path


def _run_cli(args, cwd: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    src_dir = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = str(src_dir)
    cmd = [sys.executable, "-m", "delete_empty_dirs.cli", *args]
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)


def test_cli_deletes_empty_directory(tmp_path: Path) -> None:
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()
    full_dir = tmp_path / "full_dir"
    full_dir.mkdir()
    (full_dir / "file.txt").write_text("data", encoding="utf-8")

    result = _run_cli(
        [str(empty_dir), str(full_dir), "--no-rich", "--no-log"],
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "deleted" in result.stdout
    assert not empty_dir.exists()
    assert full_dir.exists()


def test_cli_reads_paths_from_file_and_outputs_json(tmp_path: Path) -> None:
    empty_one = tmp_path / "a"
    empty_two = tmp_path / "b"
    empty_one.mkdir()
    empty_two.mkdir()
    path_file = tmp_path / "paths.txt"
    path_file.write_text(f"{empty_one}\n{empty_two}\n", encoding="utf-8")

    result = _run_cli(
        ["--from-file", str(path_file), "--no-rich", "--no-log", "--json"],
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert not empty_one.exists()
    assert not empty_two.exists()
    summary_line = result.stdout.strip().splitlines()[-1]
    summary = json.loads(summary_line)
    assert summary["deleted"] == 2
    assert summary["errors"] == 0
