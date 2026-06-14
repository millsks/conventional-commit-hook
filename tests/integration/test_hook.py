"""Integration tests: run the installed console script via subprocess."""

from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest


@pytest.mark.integration
class TestConsolescript:
    """End-to-end tests that invoke the installed console script."""

    def test_valid_commit_exits_zero(self, tmp_path: pathlib.Path) -> None:
        msg_file = tmp_path / "COMMIT_EDITMSG"
        msg_file.write_text("feat: add user authentication\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-m", "conventional_commit_hook.main", str(msg_file)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_invalid_commit_exits_one(self, tmp_path: pathlib.Path) -> None:
        msg_file = tmp_path / "COMMIT_EDITMSG"
        msg_file.write_text("This is not a conventional commit\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-m", "conventional_commit_hook.main", str(msg_file)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert result.stderr  # error message must be present on stderr

    def test_error_output_goes_to_stderr(self, tmp_path: pathlib.Path) -> None:
        msg_file = tmp_path / "COMMIT_EDITMSG"
        msg_file.write_text("bad message format\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-m", "conventional_commit_hook.main", str(msg_file)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert result.stderr
        assert result.stdout == ""

    def test_missing_file_exits_one(self, tmp_path: pathlib.Path) -> None:
        missing = tmp_path / "nonexistent.txt"
        result = subprocess.run(
            [sys.executable, "-m", "conventional_commit_hook.main", str(missing)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1

    def test_custom_types_argument(self, tmp_path: pathlib.Path) -> None:
        msg_file = tmp_path / "COMMIT_EDITMSG"
        msg_file.write_text("hotfix: patch critical crash\n", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "conventional_commit_hook.main",
                str(msg_file),
                "--types",
                "hotfix",
                "feat",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_breaking_change_accepted(self, tmp_path: pathlib.Path) -> None:
        msg_file = tmp_path / "COMMIT_EDITMSG"
        msg_file.write_text(
            "feat!: remove deprecated endpoint\n\nBREAKING CHANGE: /v1/users endpoint removed\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, "-m", "conventional_commit_hook.main", str(msg_file)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
