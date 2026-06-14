# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`conventional-commit-hook` is a pre-commit hook that enforces [Conventional Commits](https://www.conventionalcommits.org/) standards on commit messages. It is a Python package published to PyPI and used via [pre-commit](https://pre-commit.com/).

The global `~/.claude/CLAUDE.md` defines all toolchain, coding standards, test requirements, git workflow, and CI harness rules. This file covers only project-specific details.

## Commands

```bash
pixi run bootstrap           # Install git hooks (run once after clone)
pixi run test                # Unit tests only (fast inner loop)
pixi run test-integration    # Integration tests (subprocess-based)
pixi run cov                 # Full test suite with coverage gate (>=90%)
pixi run fmt                 # Auto-format with ruff
pixi run lint                # Lint with ruff
pixi run check               # Type-check with mypy (strict)
pixi run build               # Build wheel + sdist with hatch
pixi run check-package       # Verify dist/ with twine
pixi run build-conda         # Build conda package from recipe/
pixi run changelog           # Regenerate CHANGELOG.md with git-cliff
pixi run ci                  # Full gate: pre-commit + build + check + lint + cov
```

To run a single test file:

```bash
pixi run pytest tests/unit/test_parser.py -v
```

To run a single test by name:

```bash
pixi run pytest tests/unit/test_parser.py::TestHeaderParsing::test_minimal_valid_message -v
```

## Architecture

The package has three modules with a strict one-way dependency chain:

```text
parser.py -> (no internal deps)
validator.py -> parser.py
main.py -> parser.py + validator.py
```

**[src/conventional_commit_hook/parser.py](src/conventional_commit_hook/parser.py)**

- `ParseError` — raised for structurally invalid messages
- `CommitMessage` — dataclass holding all parsed fields; `is_breaking` property combines `breaking` (header `!`) and `has_breaking_footer`
- `parse(raw: str) -> CommitMessage` — strips git comments/scissors, splits into header/body/footer paragraphs, returns a typed result or raises `ParseError`
- Header regex enforces lowercase type, optional parenthesised scope, optional `!`, literal `: `, non-empty description starting with a non-space character
- Footer detection: a paragraph is a footer block if its first line matches `TOKEN(: |#)value`; `BREAKING CHANGE` and `BREAKING-CHANGE` are both recognised

**[src/conventional_commit_hook/validator.py](src/conventional_commit_hook/validator.py)**

- `CONVENTIONAL_TYPES` — the 11 standard type values (`feat`, `fix`, `docs`, etc.)
- `validate(commit, allowed_types=None) -> list[str]` — returns error strings; empty list = valid; callers supply custom types via `--types` CLI arg

**[src/conventional_commit_hook/main.py](src/conventional_commit_hook/main.py)**

- `main(argv)` — parses CLI args, reads the commit file, calls `parse()` then `validate()`, logs errors to stderr via structlog key=value format, returns exit code 0/1
- `entrypoint()` — thin wrapper that calls `sys.exit(main())`; registered as the `conventional-commit-hook` console script

## Pre-commit Hook Usage

Users add to their `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/millsks/conventional-commit-hook
    rev: v0.1.0
    hooks:
      - id: conventional-commit-hook
```

The `--types` arg allows overriding the allowed type set:

```yaml
    hooks:
      - id: conventional-commit-hook
        args: [--types, feat, fix, hotfix]
```

## Distribution

- **PyPI** (wheel + sdist): built with `hatch`, published via the `publish.yml` workflow on GitHub release
- **Conda** (noarch): built from `recipe/recipe.yaml` with rattler-build via `pixi run build-conda`

## Key Constraints

- All log output uses structlog (key=value format to stderr) — never `print()` or stdlib `logging`
- The hook must be silent on success (no stdout/stderr output on exit 0)
- Integration tests use `subprocess` with `python -m conventional_commit_hook.main` to avoid PATH dependency on the installed script in CI
