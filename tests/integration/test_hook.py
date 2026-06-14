"""Integration tests: run the installed console script via subprocess."""

from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest


def _run(
    tmp_path: pathlib.Path,
    message: str,
    extra_args: list[str] | None = None,
) -> subprocess.CompletedProcess[str]:
    msg_file = tmp_path / "COMMIT_EDITMSG"
    msg_file.write_text(message, encoding="utf-8")
    return subprocess.run(
        [sys.executable, "-m", "conventional_commit_hook.main", str(msg_file)] + (extra_args or []),
        capture_output=True,
        text=True,
    )


_VALID = [
    pytest.param("feat: add user authentication", id="minimal-valid"),
    pytest.param("fix(auth): resolve null pointer on login", id="with-scope"),
    pytest.param("feat!: drop Python 2 support", id="breaking-marker"),
    pytest.param("feat(api)!: remove v1 endpoints", id="scope-and-breaking-marker"),
    pytest.param("chore: update dependencies", id="type-chore"),
    pytest.param("ci: add coverage step", id="type-ci"),
    pytest.param("docs: update README", id="type-docs"),
    pytest.param("style: reformat with black", id="type-style"),
    pytest.param("refactor: extract auth module", id="type-refactor"),
    pytest.param("perf: cache DB results", id="type-perf"),
    pytest.param("test: add parser unit tests", id="type-test"),
    pytest.param("build: upgrade hatchling", id="type-build"),
    pytest.param("revert: revert feat: add login", id="type-revert"),
    pytest.param("feat: add login\n\nAdds OAuth2 flow with PKCE support.", id="with-body"),
    pytest.param("fix: resolve timeout\n\nFirst para.\n\nSecond para.", id="multi-paragraph-body"),
    pytest.param("feat: new api\n\nBREAKING CHANGE: /v1 endpoint removed", id="breaking-change-footer"),
    pytest.param("feat: new api\n\nBREAKING-CHANGE: /v1 endpoint removed", id="breaking-change-hyphen-footer"),
    pytest.param("feat: add login\n\nReviewed-by: Alice <alice@example.com>", id="reviewed-by-footer"),
    pytest.param("feat: add login\n\nReviewed-by: Alice\nCo-authored-by: Bob <bob@example.com>", id="multiple-footers"),
    pytest.param("fix: resolve issue\n\nFixes #123", id="hash-footer"),
    pytest.param(
        "feat: add login\n\nAdds OAuth2 flow.\n\nReviewed-by: Alice\nBREAKING CHANGE: old /login removed",
        id="body-and-footer",
    ),
    pytest.param(
        "feat: add login\n# Please enter the commit message\n# Changes to be committed", id="git-comments-stripped"
    ),
    pytest.param(
        "feat: add login\n\n# ------------------------ >8 ------------------------\ndiff --git a/file.py b/file.py\n+added line",
        id="git-scissors-stripped",
    ),
    pytest.param(
        "feat: add login\n\nThis is the body.\n# ------------------------ >8 ------------------------\ndiff --git a/file.py",
        id="body-preserved-before-scissors",
    ),
    pytest.param("feat: add OAuth2 support (RFC 6749)", id="special-chars-in-description"),
]

_INVALID = [
    pytest.param("This is not a conventional commit", id="no-type-or-colon"),
    pytest.param("Feat: add something", id="uppercase-type"),
    pytest.param("Fix: add something", id="mixed-case-type"),
    pytest.param("feat:add something", id="missing-space-after-colon"),
    pytest.param("feat: ", id="empty-description"),
    pytest.param("", id="empty-message"),
    pytest.param("   \n  \n", id="whitespace-only"),
    pytest.param("feat: add login\nBody without blank line", id="no-blank-line-before-body"),
    pytest.param("unknown: add something", id="unknown-type"),
    pytest.param("wip: half-done feature", id="wip-not-in-spec"),
    pytest.param("feat((nested)): something", id="nested-parens-in-scope"),
    pytest.param("# Please enter the commit message.\n# Lines starting with # ignored.", id="comment-only-message"),
    pytest.param("feat:", id="type-only-no-description"),
    pytest.param("Add user authentication", id="imperative-without-type"),
]


@pytest.mark.integration
class TestValidMessages:
    @pytest.mark.parametrize("message", _VALID)
    def test_exits_zero_with_no_stdout(self, tmp_path: pathlib.Path, message: str) -> None:
        result = _run(tmp_path, message)
        assert result.returncode == 0
        assert result.stdout == ""


@pytest.mark.integration
class TestInvalidMessages:
    @pytest.mark.parametrize("message", _INVALID)
    def test_exits_one_with_stderr(self, tmp_path: pathlib.Path, message: str) -> None:
        result = _run(tmp_path, message)
        assert result.returncode == 1
        assert result.stderr


@pytest.mark.integration
class TestCustomTypes:
    def test_custom_type_accepted_with_flag(self, tmp_path: pathlib.Path) -> None:
        result = _run(tmp_path, "hotfix: patch critical crash", extra_args=["--types", "hotfix", "feat"])
        assert result.returncode == 0
        assert result.stdout == ""

    def test_custom_type_rejected_without_flag(self, tmp_path: pathlib.Path) -> None:
        result = _run(tmp_path, "hotfix: patch critical crash")
        assert result.returncode == 1
        assert result.stderr


@pytest.mark.integration
class TestOutputBehavior:
    def test_error_goes_to_stderr_not_stdout(self, tmp_path: pathlib.Path) -> None:
        result = _run(tmp_path, "bad message format")
        assert result.returncode == 1
        assert result.stderr
        assert result.stdout == ""

    def test_missing_file_exits_one(self, tmp_path: pathlib.Path) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "conventional_commit_hook.main", str(tmp_path / "nonexistent.txt")],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
