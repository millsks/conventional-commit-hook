# Contributing to conventional-commit-hook

Thank you for taking the time to contribute.

## Prerequisites

[Pixi](https://pixi.sh) is the only prerequisite. It manages Python, all dependencies, and every development task.

## Setup

```sh
git clone https://github.com/millsks/conventional-commit-hook
cd conventional-commit-hook
pixi run bootstrap   # installs git hooks
```

## Branch naming

| Change type | Prefix | Example |
|---|---|---|
| New feature | `feature/` | `feature/add-scope-validation` |
| Bug fix | `bugfix/` | `bugfix/empty-description-crash` |
| Hotfix | `hotfix/` | `hotfix/incorrect-exit-code` |

Never commit directly to `main`.

## Commit messages

This project uses [Conventional Commits](https://www.conventionalcommits.org/) — enforced by the hook itself. Every commit must follow the format:

```
<type>(<scope>): <description>
```

The pre-commit hook will reject any commit that does not conform.

## Development workflow

Run these frequently while writing code:

```sh
pixi run test        # unit tests after every meaningful change
pixi run fmt         # auto-format before staging
pixi run lint        # surface ruff issues early
pixi run check       # surface mypy issues early
```

Run the integration tests when touching the parser, validator, or CLI entry point:

```sh
pixi run test-integration
```

## CI gate

`pixi run ci` is the required final step before every commit:

```sh
pixi run ci
```

It runs pre-commit hooks, builds the package, type-checks, lints, and runs the full test suite with the coverage gate (≥90%). The gate must exit 0. Do not use `--no-verify` to bypass it.

## Test requirements

Every code change must include a corresponding test:

- **New behaviour** — add at least one test that exercises it directly
- **Bug fix** — add a test that would have caught the bug
- **Modified behaviour** — update any tests covering the changed path

Unit tests go in `tests/unit/`, integration tests in `tests/integration/`. The coverage gate is enforced by `pixi run cov`.

## Code style

- Line length: 120
- Type hints required on all public signatures
- Google-style docstrings on all public functions and classes
- No `print()` anywhere — use structlog
- No bare `except:` — always catch specific exception types
- mypy strict mode must pass

## Submitting a pull request

1. Open a PR against `main`
2. Fill in the pull request template
3. Ensure `pixi run ci` passes locally before requesting review
4. Keep each PR focused on a single concern
5. Delete the branch after it is merged

## Reporting issues

Use the [issue templates](https://github.com/millsks/conventional-commit-hook/issues/new/choose) for bug reports and feature requests.
