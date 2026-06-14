"""Unit tests for the commit message parser."""

from __future__ import annotations

import pytest

from conventional_commit_hook.parser import CommitMessage, ParseError, parse


class TestHeaderParsing:
    """Tests for the commit header (first line) parser."""

    def test_minimal_valid_message(self) -> None:
        result = parse("feat: add user authentication")
        assert result.type == "feat"
        assert result.scope is None
        assert result.breaking is False
        assert result.description == "add user authentication"
        assert result.body is None
        assert result.footers == []
        assert result.has_breaking_footer is False

    def test_with_scope(self) -> None:
        result = parse("fix(auth): resolve null pointer on login")
        assert result.type == "fix"
        assert result.scope == "auth"
        assert result.description == "resolve null pointer on login"

    def test_breaking_change_marker(self) -> None:
        result = parse("feat!: drop Python 2 support")
        assert result.type == "feat"
        assert result.breaking is True
        assert result.is_breaking is True

    def test_scope_and_breaking_marker(self) -> None:
        result = parse("feat(api)!: remove v1 endpoints")
        assert result.type == "feat"
        assert result.scope == "api"
        assert result.breaking is True

    def test_all_standard_types_are_valid(self) -> None:
        types = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "build", "ci", "chore", "revert"]
        for t in types:
            result = parse(f"{t}: some description")
            assert result.type == t

    def test_single_char_description(self) -> None:
        result = parse("fix: x")
        assert result.description == "x"

    def test_description_with_special_characters(self) -> None:
        result = parse("feat: add OAuth2 support (RFC 6749)")
        assert result.description == "add OAuth2 support (RFC 6749)"


class TestHeaderParseErrors:
    """Tests for invalid commit headers."""

    def test_empty_message_raises(self) -> None:
        with pytest.raises(ParseError, match="empty"):
            parse("")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(ParseError, match="empty"):
            parse("   \n  \n")

    def test_missing_colon_space_raises(self) -> None:
        with pytest.raises(ParseError, match="Header does not follow"):
            parse("feat add something")

    def test_colon_without_space_raises(self) -> None:
        with pytest.raises(ParseError, match="Header does not follow"):
            parse("feat:add something")

    def test_uppercase_type_raises(self) -> None:
        with pytest.raises(ParseError, match="Header does not follow"):
            parse("Feat: add something")

    def test_empty_description_raises(self) -> None:
        with pytest.raises(ParseError, match="Header does not follow"):
            parse("feat: ")

    def test_missing_blank_line_before_body_raises(self) -> None:
        msg = "feat: add login\nThis is the body without blank line"
        with pytest.raises(ParseError, match="blank line"):
            parse(msg)

    def test_scope_with_parens_raises(self) -> None:
        with pytest.raises(ParseError, match="Header does not follow"):
            parse("feat((nested)): something")


class TestBodyParsing:
    """Tests for commit body parsing."""

    def test_message_with_body(self) -> None:
        msg = "feat: add login\n\nThis adds a login form with OAuth2 support."
        result = parse(msg)
        assert result.body == "This adds a login form with OAuth2 support."

    def test_multi_paragraph_body(self) -> None:
        msg = "fix: resolve timeout\n\nFirst paragraph.\n\nSecond paragraph."
        result = parse(msg)
        assert result.body == "First paragraph.\n\nSecond paragraph."

    def test_body_with_trailing_newline(self) -> None:
        msg = "feat: add login\n\nSome body text.\n"
        result = parse(msg)
        assert result.body == "Some body text."


class TestFooterParsing:
    """Tests for commit footer parsing."""

    def test_reviewed_by_footer(self) -> None:
        msg = "feat: add login\n\nReviewed-by: Alice <alice@example.com>"
        result = parse(msg)
        assert len(result.footers) == 1
        assert result.footers[0][0] == "Reviewed-by"

    def test_breaking_change_footer(self) -> None:
        msg = "feat: new api\n\nBREAKING CHANGE: environment variables now take precedence"
        result = parse(msg)
        assert result.has_breaking_footer is True
        assert result.is_breaking is True

    def test_breaking_change_hyphen_synonym(self) -> None:
        msg = "feat: new api\n\nBREAKING-CHANGE: environment variables now take precedence"
        result = parse(msg)
        assert result.has_breaking_footer is True

    def test_hash_separator_footer(self) -> None:
        msg = "fix: resolve issue\n\nFixes #123"
        result = parse(msg)
        assert len(result.footers) == 1
        assert result.footers[0][0] == "Fixes"
        assert result.footers[0][1] == "123"

    def test_multiple_footers(self) -> None:
        msg = "feat: add login\n\nReviewed-by: Alice\nCo-authored-by: Bob <bob@example.com>"
        result = parse(msg)
        assert len(result.footers) == 2

    def test_body_and_footers(self) -> None:
        msg = (
            "feat: add login\n\n"
            "Adds a login form with OAuth2 support.\n\n"
            "Reviewed-by: Alice\n"
            "BREAKING CHANGE: old /login endpoint removed"
        )
        result = parse(msg)
        assert result.body == "Adds a login form with OAuth2 support."
        assert result.has_breaking_footer is True
        assert len(result.footers) == 2


class TestGitCommentStripping:
    """Tests for stripping git-generated comment lines."""

    def test_strips_comment_lines(self) -> None:
        msg = "feat: add login\n# Please enter the commit message\n# Changes to be committed"
        result = parse(msg)
        assert result.type == "feat"

    def test_strips_git_scissors(self) -> None:
        msg = (
            "feat: add login\n\n"
            "# ------------------------ >8 ------------------------\n"
            "diff --git a/file.py b/file.py\n"
            "+added line"
        )
        result = parse(msg)
        assert result.body is None

    def test_preserves_body_before_scissors(self) -> None:
        msg = (
            "feat: add login\n\n"
            "This is the body.\n"
            "# ------------------------ >8 ------------------------\n"
            "diff --git a/file.py b/file.py"
        )
        result = parse(msg)
        assert result.body == "This is the body."

    def test_comment_only_message_raises(self) -> None:
        msg = "# Please enter the commit message for your changes.\n# Lines starting with '#' will be ignored."
        with pytest.raises(ParseError, match="empty"):
            parse(msg)


class TestIsBreaking:
    """Tests for the is_breaking property."""

    def test_not_breaking_by_default(self) -> None:
        result = parse("feat: add something")
        assert result.is_breaking is False

    def test_breaking_via_marker(self) -> None:
        result = parse("feat!: remove endpoint")
        assert result.is_breaking is True

    def test_breaking_via_footer(self) -> None:
        result = parse("feat: new api\n\nBREAKING CHANGE: old api removed")
        assert result.is_breaking is True

    def test_commit_message_dataclass(self) -> None:
        msg = CommitMessage(type="feat", scope=None, breaking=False, description="test")
        assert msg.is_breaking is False
        assert msg.body is None
        assert msg.footers == []
        assert msg.has_breaking_footer is False
