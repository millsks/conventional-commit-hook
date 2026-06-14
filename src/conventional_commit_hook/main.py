"""Entry point for the conventional-commit-hook pre-commit hook."""

from __future__ import annotations

import argparse
import pathlib
import sys

import structlog

from conventional_commit_hook.parser import ParseError, parse
from conventional_commit_hook.validator import CONVENTIONAL_TYPES, validate

_log = structlog.get_logger(__name__)


def _configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.KeyValueRenderer(key_order=["log_level", "event"]),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(0),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
    )


def main(argv: list[str] | None = None) -> int:
    """Run the conventional commit validation hook.

    Args:
        argv: Command-line arguments. Defaults to sys.argv[1:].

    Returns:
        Exit code: 0 on success, 1 on validation failure.
    """
    _configure_logging()

    arg_parser = argparse.ArgumentParser(
        prog="conventional-commit-hook",
        description="Validate commit messages against the Conventional Commits specification.",
    )
    arg_parser.add_argument(
        "commit_msg_file",
        type=pathlib.Path,
        help="Path to the file containing the commit message (provided by git via pre-commit)",
    )
    arg_parser.add_argument(
        "--types",
        metavar="TYPE",
        nargs="+",
        default=None,
        help=f"Allowed commit types (default: {sorted(CONVENTIONAL_TYPES)})",
    )
    args = arg_parser.parse_args(argv)
    commit_msg_path: pathlib.Path = args.commit_msg_file

    try:
        raw = commit_msg_path.read_text(encoding="utf-8")
    except OSError as exc:
        _log.error("cannot read commit message file", path=str(commit_msg_path), error=str(exc))
        return 1

    allowed_types: frozenset[str] | None = frozenset(args.types) if args.types else None

    try:
        commit = parse(raw)
    except ParseError as exc:
        _log.error("invalid commit message format", error=str(exc))
        return 1

    errors = validate(commit, allowed_types=allowed_types)
    if errors:
        for error in errors:
            _log.error("commit message validation failed", error=error)
        return 1

    return 0


def entrypoint() -> None:
    """Console script entry point."""
    sys.exit(main())


if __name__ == "__main__":
    entrypoint()
