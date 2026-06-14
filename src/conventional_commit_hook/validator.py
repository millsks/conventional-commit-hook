"""Validation logic for parsed Conventional Commits messages."""

from __future__ import annotations

from conventional_commit_hook.parser import CommitMessage

CONVENTIONAL_TYPES: frozenset[str] = frozenset(
    {
        "build",
        "chore",
        "ci",
        "docs",
        "feat",
        "fix",
        "perf",
        "refactor",
        "revert",
        "style",
        "test",
    }
)


def validate(
    commit: CommitMessage,
    allowed_types: frozenset[str] | None = None,
) -> list[str]:
    """Validate a parsed commit message and return a list of error messages.

    Args:
        commit: A parsed CommitMessage to validate.
        allowed_types: Set of allowed commit type strings. Defaults to CONVENTIONAL_TYPES.

    Returns:
        A (possibly empty) list of human-readable error strings. An empty list means the
        commit message is valid.
    """
    errors: list[str] = []
    types = allowed_types if allowed_types is not None else CONVENTIONAL_TYPES

    if commit.type not in types:
        errors.append(
            f"Unknown type {commit.type!r}. Allowed types: {sorted(types)}\n"
            f"  See https://www.conventionalcommits.org for the specification."
        )

    if not commit.description or not commit.description.strip():
        errors.append("Description must not be empty or whitespace-only")
    elif commit.description != commit.description.strip():
        errors.append(f"Description must not have leading or trailing whitespace: {commit.description!r}")

    return errors
