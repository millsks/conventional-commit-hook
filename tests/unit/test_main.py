"""Unit tests for the CLI entry point."""

from __future__ import annotations

import pathlib

import pytest

from conventional_commit_hook.main import main


class TestMainReturnCodes:
    """Tests for main() return codes with various commit messages."""

    def test_valid_commit_returns_zero(self, tmp_path: pathlib.Path) -> None:
        msg_file = tmp_path / "COMMIT_EDITMSG"
        msg_file.write_text("feat: add user login\n", encoding="utf-8")
        assert main([str(msg_file)]) == 0

    def test_invalid_format_returns_one(self, tmp_path: pathlib.Path) -> None:
        msg_file = tmp_path / "COMMIT_EDITMSG"
        msg_file.write_text("This is not a conventional commit\n", encoding="utf-8")
        assert main([str(msg_file)]) == 1

    def test_unknown_type_returns_one(self, tmp_path: pathlib.Path) -> None:
        msg_file = tmp_path / "COMMIT_EDITMSG"
        msg_file.write_text("unknown: do something\n", encoding="utf-8")
        assert main([str(msg_file)]) == 1

    def test_missing_file_returns_one(self, tmp_path: pathlib.Path) -> None:
        missing = tmp_path / "nonexistent.txt"
        assert main([str(missing)]) == 1

    def test_empty_file_returns_one(self, tmp_path: pathlib.Path) -> None:
        msg_file = tmp_path / "COMMIT_EDITMSG"
        msg_file.write_text("", encoding="utf-8")
        assert main([str(msg_file)]) == 1

    def test_commit_with_body_returns_zero(self, tmp_path: pathlib.Path) -> None:
        msg_file = tmp_path / "COMMIT_EDITMSG"
        msg_file.write_text(
            "feat(auth): add OAuth2 login\n\nAdds OAuth2 flow with PKCE support.\n",
            encoding="utf-8",
        )
        assert main([str(msg_file)]) == 0

    def test_breaking_change_commit_returns_zero(self, tmp_path: pathlib.Path) -> None:
        msg_file = tmp_path / "COMMIT_EDITMSG"
        msg_file.write_text("feat!: remove legacy API\n", encoding="utf-8")
        assert main([str(msg_file)]) == 0

    def test_breaking_change_footer_returns_zero(self, tmp_path: pathlib.Path) -> None:
        msg_file = tmp_path / "COMMIT_EDITMSG"
        msg_file.write_text(
            "feat: new config format\n\nBREAKING CHANGE: config file format changed\n",
            encoding="utf-8",
        )
        assert main([str(msg_file)]) == 0


class TestCustomTypes:
    """Tests for the --types argument."""

    def test_custom_type_passes_when_allowed(self, tmp_path: pathlib.Path) -> None:
        msg_file = tmp_path / "COMMIT_EDITMSG"
        msg_file.write_text("hotfix: resolve critical bug\n", encoding="utf-8")
        assert main([str(msg_file), "--types", "hotfix", "feat", "fix"]) == 0

    def test_conventional_type_fails_when_not_in_custom_list(self, tmp_path: pathlib.Path) -> None:
        msg_file = tmp_path / "COMMIT_EDITMSG"
        msg_file.write_text("chore: update deps\n", encoding="utf-8")
        assert main([str(msg_file), "--types", "feat", "fix"]) == 1

    def test_default_types_used_when_no_types_arg(self, tmp_path: pathlib.Path) -> None:
        msg_file = tmp_path / "COMMIT_EDITMSG"
        msg_file.write_text("chore: update deps\n", encoding="utf-8")
        assert main([str(msg_file)]) == 0


class TestGitCommentHandling:
    """Tests for git comment stripping in main."""

    def test_message_with_git_comments_passes(self, tmp_path: pathlib.Path) -> None:
        msg_file = tmp_path / "COMMIT_EDITMSG"
        msg_file.write_text(
            "feat: add login\n# Please enter the commit message.\n# Changes to be committed:\n#\tnew file: login.py\n",
            encoding="utf-8",
        )
        assert main([str(msg_file)]) == 0

    def test_comment_only_message_returns_one(self, tmp_path: pathlib.Path) -> None:
        msg_file = tmp_path / "COMMIT_EDITMSG"
        msg_file.write_text(
            "# Please enter the commit message.\n# Lines starting with '#' will be ignored.\n",
            encoding="utf-8",
        )
        assert main([str(msg_file)]) == 1


@pytest.mark.parametrize(
    "message",
    [
        "feat: add something",
        "fix(api): correct response code",
        "docs: update readme",
        "chore(deps): bump ruff to 0.5.0",
        "feat!: remove old endpoint",
        "refactor(core): simplify parser logic",
    ],
)
def test_valid_messages(tmp_path: pathlib.Path, message: str) -> None:
    """A collection of valid messages should all return 0."""
    msg_file = tmp_path / "COMMIT_EDITMSG"
    msg_file.write_text(message + "\n", encoding="utf-8")
    assert main([str(msg_file)]) == 0


@pytest.mark.parametrize(
    "message",
    [
        "Add something",
        "feat :add something",
        "FEAT: add something",
        "feat(scope: missing closing paren",
        "feat: ",
    ],
)
def test_invalid_messages(tmp_path: pathlib.Path, message: str) -> None:
    """A collection of invalid messages should all return 1."""
    msg_file = tmp_path / "COMMIT_EDITMSG"
    msg_file.write_text(message + "\n", encoding="utf-8")
    assert main([str(msg_file)]) == 1
