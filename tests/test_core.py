import os
from pathlib import Path

import pytest

from delete_empty_dirs.core import ExecutionSettings, normalise_path, process_paths
from delete_empty_dirs.models import ResultStatus, SkipReason


def make_settings(tmp_path: Path, *, follow_symlinks: bool = False, restrict_to: tuple[Path, ...] = ()) -> ExecutionSettings:
    protected = {tmp_path, Path.home()}
    if os.name == "nt":
        anchor = tmp_path.anchor or Path.home().anchor
        if anchor:
            protected.add(Path(anchor))
    else:
        protected.add(Path("/"))
    return ExecutionSettings(
        follow_symlinks=follow_symlinks,
        restrict_to=restrict_to,
        allow_roots=(),
        protected_roots=tuple(protected),
        repo_root=tmp_path,
    )


def test_process_empty_directory_deleted(tmp_path: Path) -> None:
    target = tmp_path / "empty"
    target.mkdir()
    settings = make_settings(tmp_path)

    results, totals, _ = process_paths([target], settings, workers=1)

    assert results[0].status == ResultStatus.DELETED
    assert results[0].empty_verified is True
    assert not target.exists()
    assert totals.deleted == 1


def test_process_non_empty_directory_skipped(tmp_path: Path) -> None:
    target = tmp_path / "non_empty"
    target.mkdir()
    (target / "file.txt").write_text("content")
    settings = make_settings(tmp_path)

    results, totals, _ = process_paths([target], settings, workers=1)

    assert results[0].status == ResultStatus.SKIPPED
    assert results[0].reason == SkipReason.NOT_EMPTY
    assert target.exists()
    assert totals.skipped == 1


def test_restrict_policy_blocks(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    restrict_root = tmp_path / "allowed"
    restrict_root.mkdir()
    settings = make_settings(tmp_path, restrict_to=(restrict_root,))

    results, totals, _ = process_paths([outside], settings, workers=1)

    assert results[0].status == ResultStatus.SKIPPED
    assert results[0].reason == SkipReason.POLICY_BLOCKED
    assert totals.skipped == 1


def test_symlink_refused_without_follow(tmp_path: Path) -> None:
    target = tmp_path / "target"
    link = tmp_path / "link"
    target.mkdir()
    try:
        os.symlink(target, link, target_is_directory=True)
    except (AttributeError, NotImplementedError):
        pytest.skip("Symlinks not supported on this platform")
    except OSError as exc:
        pytest.skip(f"Symlink creation failed: {exc}")

    settings = make_settings(tmp_path, follow_symlinks=False)
    results, totals, _ = process_paths([link], settings, workers=1)

    assert results[0].status == ResultStatus.SKIPPED
    assert results[0].reason == SkipReason.SYMLINK_DIR_REFUSED
    assert target.exists()
    assert totals.skipped == 1


def test_symlink_follow_deletes_target(tmp_path: Path) -> None:
    target = tmp_path / "target_follow"
    link = tmp_path / "link_follow"
    target.mkdir()
    try:
        os.symlink(target, link, target_is_directory=True)
    except (AttributeError, NotImplementedError):
        pytest.skip("Symlinks not supported on this platform")
    except OSError as exc:
        pytest.skip(f"Symlink creation failed: {exc}")

    settings = make_settings(tmp_path, follow_symlinks=True)
    results, totals, _ = process_paths([link], settings, workers=1)

    assert results[0].status == ResultStatus.DELETED
    assert not target.exists()
    assert totals.deleted == 1


def test_normalise_path_expands_user(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    path = normalise_path("~/example")
    assert str(path).startswith(str(fake_home))
