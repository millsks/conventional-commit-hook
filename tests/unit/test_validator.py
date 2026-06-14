"""Unit tests for the commit message validator."""

from __future__ import annotations

import pytest

from conventional_commit_hook.parser import CommitMessage
from conventional_commit_hook.validator import CONVENTIONAL_TYPES, validate


def _commit(
    type: str = "feat",
    scope: str | None = None,
    breaking: bool = False,
    description: str = "add something",
) -> CommitMessage:
    return CommitMessage(type=type, scope=scope, breaking=breaking, description=description)


class TestValidTypes:
    """Tests that all conventional types pass validation."""

    @pytest.mark.parametrize("commit_type", sorted(CONVENTIONAL_TYPES))
    def test_all_conventional_types_pass(self, commit_type: str) -> None:
        errors = validate(_commit(type=commit_type))
        assert errors == []

    def test_unknown_type_fails(self) -> None:
        errors = validate(_commit(type="unknown"))
        assert len(errors) == 1
        assert "Unknown type" in errors[0]
        assert "'unknown'" in errors[0]

    def test_custom_allowed_types(self) -> None:
        custom_types = frozenset({"feat", "fix", "hotfix"})
        assert validate(_commit(type="hotfix"), allowed_types=custom_types) == []
        errors = validate(_commit(type="chore"), allowed_types=custom_types)
        assert len(errors) == 1

    def test_custom_types_replaces_defaults(self) -> None:
        # 'chore' is in defaults but not in custom_types — should fail
        errors = validate(_commit(type="chore"), allowed_types=frozenset({"feat"}))
        assert len(errors) == 1

    def test_error_includes_allowed_types_list(self) -> None:
        errors = validate(_commit(type="bad"), allowed_types=frozenset({"feat", "fix"}))
        assert "feat" in errors[0]
        assert "fix" in errors[0]


class TestDescription:
    """Tests for description validation."""

    def test_normal_description_passes(self) -> None:
        errors = validate(_commit(description="add user authentication"))
        assert errors == []

    def test_trailing_whitespace_fails(self) -> None:
        errors = validate(_commit(description="add something  "))
        assert any("whitespace" in e for e in errors)

    def test_leading_whitespace_fails(self) -> None:
        errors = validate(_commit(description="  add something"))
        assert any("whitespace" in e for e in errors)

    def test_whitespace_only_description_fails(self) -> None:
        errors = validate(_commit(description="   "))
        assert any("empty" in e or "whitespace" in e for e in errors)


class TestMultipleErrors:
    """Tests that multiple errors are returned together."""

    def test_bad_type_and_bad_description_returns_two_errors(self) -> None:
        errors = validate(_commit(type="bad", description="   "))
        assert len(errors) == 2


class TestConventionalTypesConstant:
    """Tests for the CONVENTIONAL_TYPES constant."""

    def test_required_types_present(self) -> None:
        assert "feat" in CONVENTIONAL_TYPES
        assert "fix" in CONVENTIONAL_TYPES

    def test_is_frozenset(self) -> None:
        assert isinstance(CONVENTIONAL_TYPES, frozenset)
