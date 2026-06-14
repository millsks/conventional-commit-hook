"""Conventional Commits message parser."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Matches the commit header: type[(scope)][!]: description
_HEADER_RE = re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[^()]+)\))?(?P<breaking>!)?:\ (?P<description>\S.*)$")

# Matches a footer token line: TOKEN(: |<space>#)value
_FOOTER_TOKEN_RE = re.compile(r"^(?P<token>BREAKING[- ]CHANGE|[A-Za-z0-9][A-Za-z0-9-]*)(?::\ |\ #)")

# Matches the git "scissors" line that separates the message from the diff
_GIT_SCISSORS_RE = re.compile(r"^# -+ >8 -+$")


class ParseError(ValueError):
    """Raised when a commit message cannot be parsed as a Conventional Commit."""


@dataclass
class CommitMessage:
    """A parsed Conventional Commits message."""

    type: str
    scope: str | None
    breaking: bool
    description: str
    body: str | None = None
    footers: list[tuple[str, str]] = field(default_factory=list)
    has_breaking_footer: bool = False

    @property
    def is_breaking(self) -> bool:
        """Return True if this commit is a breaking change."""
        return self.breaking or self.has_breaking_footer


def parse(raw: str) -> CommitMessage:
    """Parse a raw commit message string into a CommitMessage.

    Args:
        raw: The raw commit message text, as provided by git/pre-commit.

    Returns:
        A parsed CommitMessage.

    Raises:
        ParseError: If the message does not conform to the Conventional Commits spec.
    """
    cleaned = _strip_git_comments(raw).strip()
    if not cleaned:
        raise ParseError("Commit message is empty")

    lines = cleaned.splitlines()
    header_match = _HEADER_RE.match(lines[0])
    if not header_match:
        raise ParseError(
            f"Header does not follow '<type>[(<scope>)][!]: <description>' format.\n"
            f"  Got:      {lines[0]!r}\n"
            f"  Expected: feat(scope)!: description"
        )

    commit_type = header_match.group("type")
    scope = header_match.group("scope")
    breaking = header_match.group("breaking") is not None
    description = header_match.group("description")

    body: str | None = None
    footers: list[tuple[str, str]] = []
    has_breaking_footer = False

    if len(lines) > 1:
        if lines[1] != "":
            raise ParseError(f"A blank line must separate the header from the body/footer.\n  Line 2: {lines[1]!r}")

        rest = lines[2:]
        if rest:
            paragraphs = _split_paragraphs(rest)
            footer_start = _find_footer_start(paragraphs)

            body_paras = paragraphs[:footer_start]
            footer_paras = paragraphs[footer_start:]

            if body_paras:
                body = "\n\n".join("\n".join(p) for p in body_paras)

            for para in footer_paras:
                for token, value in _parse_footer_paragraph(para):
                    footers.append((token, value))
                    if token.upper().replace("-", " ") == "BREAKING CHANGE":
                        has_breaking_footer = True

    return CommitMessage(
        type=commit_type,
        scope=scope,
        breaking=breaking,
        description=description,
        body=body,
        footers=footers,
        has_breaking_footer=has_breaking_footer,
    )


def _strip_git_comments(raw: str) -> str:
    """Remove git-generated comment lines and everything after the scissors marker."""
    lines: list[str] = []
    for line in raw.splitlines():
        if _GIT_SCISSORS_RE.match(line):
            break
        if not line.startswith("#"):
            lines.append(line)
    return "\n".join(lines)


def _split_paragraphs(lines: list[str]) -> list[list[str]]:
    """Split a list of lines into paragraphs separated by blank lines."""
    paragraphs: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if line == "":
            if current:
                paragraphs.append(current)
                current = []
        else:
            current.append(line)
    if current:
        paragraphs.append(current)
    return paragraphs


def _find_footer_start(paragraphs: list[list[str]]) -> int:
    """Return the index of the first paragraph that belongs to the footer section."""
    idx = len(paragraphs)
    for i in range(len(paragraphs) - 1, -1, -1):
        if _is_footer_paragraph(paragraphs[i]):
            idx = i
        else:
            break
    return idx


def _is_footer_paragraph(para: list[str]) -> bool:
    """Return True if the paragraph's first line is a valid footer token."""
    return bool(para) and bool(_FOOTER_TOKEN_RE.match(para[0]))


def _parse_footer_paragraph(para: list[str]) -> list[tuple[str, str]]:
    """Parse a footer paragraph into (token, value) pairs."""
    result: list[tuple[str, str]] = []
    current_token: str | None = None
    current_value_parts: list[str] = []

    for line in para:
        match = _FOOTER_TOKEN_RE.match(line)
        if match:
            if current_token is not None:
                result.append((current_token, "\n".join(current_value_parts)))
            current_token = match.group("token")
            current_value_parts = [line[match.end() :]]
        elif current_token is not None:
            current_value_parts.append(line)

    if current_token is not None:
        result.append((current_token, "\n".join(current_value_parts)))

    return result
