# conventional-commit-hook

[![CI](https://github.com/millsks/conventional-commit-hook/actions/workflows/ci.yml/badge.svg)](https://github.com/millsks/conventional-commit-hook/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/millsks/conventional-commit-hook/branch/main/graph/badge.svg)](https://codecov.io/gh/millsks/conventional-commit-hook)
[![PyPI](https://img.shields.io/pypi/v/conventional-commit-hook.svg)](https://pypi.org/project/conventional-commit-hook/)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/conventional-commit-hook.svg)](https://anaconda.org/conda-forge/conventional-commit-hook)
[![Python](https://img.shields.io/pypi/pyversions/conventional-commit-hook.svg)](https://pypi.org/project/conventional-commit-hook/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A [pre-commit](https://pre-commit.com/) hook that validates commit messages against the [Conventional Commits](https://www.conventionalcommits.org/) specification.

## Features

- Validates commit message structure: type, optional scope, optional breaking marker, description
- Enforces all 11 standard Conventional Commit types out of the box
- Custom type overrides via `--types`
- Detects breaking changes from both the `!` header marker and `BREAKING CHANGE` footer
- Strips git-generated comment lines and scissors line before validation
- Silent on success — writes only to stderr on failure, never to stdout
- Single runtime dependency: [structlog](https://www.structlog.org/)

## Installation

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/millsks/conventional-commit-hook
    rev: v0.1.0
    hooks:
      - id: conventional-commit-hook
```

Install the hook:

```sh
pre-commit install --hook-type commit-msg
```

## Usage

The hook runs automatically on `git commit`. It exits 0 (silent) on a valid message, or 1 (error to stderr) on an invalid one.

### Supported commit types

| Type | Purpose |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no logic change |
| `refactor` | Code restructure, no feature or fix |
| `perf` | Performance improvement |
| `test` | Adding or fixing tests |
| `build` | Build system or dependency changes |
| `ci` | CI configuration changes |
| `chore` | Maintenance tasks |
| `revert` | Revert a previous commit |

### Message format

```
<type>[(<scope>)][!]: <description>

[body]

[footer(s)]
```

- **type** — one of the 11 types above (lowercase)
- **scope** — optional, enclosed in parentheses: `fix(auth): …`
- **!** — optional breaking change marker: `feat!: …`
- **description** — required, non-empty, starts immediately after ``: ``
- **body** — optional, separated from the header by a blank line
- **footers** — optional, each on its own line as `Token: value` or `Token #value`; `BREAKING CHANGE: …` marks a breaking release

### Valid examples

```
feat: add user authentication
fix(auth): resolve null pointer on login
feat!: drop Python 2 support
feat(api)!: remove v1 endpoints
docs: update installation instructions
```

With body and footers:

```
feat: add OAuth2 support

Implements the PKCE flow with refresh token rotation.

BREAKING CHANGE: the /auth/token endpoint now requires a code_verifier
Reviewed-by: Alice <alice@example.com>
```

### Invalid examples

```
# Missing type
Add user authentication

# Uppercase type
Feat: add something

# Missing space after colon
feat:add something

# No blank line before body
feat: add login
Body text without a blank line separator
```

### Custom types

Override the allowed type set with `--types`:

```yaml
    hooks:
      - id: conventional-commit-hook
        args: [--types, feat, fix, hotfix, chore]
```

When `--types` is supplied, only those types are accepted. Standard types not listed are rejected.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow.

### Prerequisites

[Pixi](https://pixi.sh) — all other dependencies are managed by Pixi.

### Setup

```sh
git clone https://github.com/millsks/conventional-commit-hook
cd conventional-commit-hook
pixi run bootstrap
```

### Common tasks

| Command | Purpose |
|---|---|
| `pixi run test` | Unit tests only (fast inner loop) |
| `pixi run test-integration` | Integration tests |
| `pixi run cov` | Full suite + coverage gate (≥90%) |
| `pixi run fmt` | Auto-format with ruff |
| `pixi run lint` | Lint with ruff |
| `pixi run check` | Type-check with mypy (strict) |
| `pixi run build` | Build wheel + sdist |
| `pixi run ci` | Full CI gate — must pass before committing |

## License

[MIT](LICENSE)

<br\><br\>

_Inspired by matthorgan's [`pre-commit-conventional-commits`](https://github.com/matthorgan/pre-commit-conventional-commits)._
