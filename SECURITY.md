# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 0.1.x   | Yes       |

Older versions receive no security fixes. Please upgrade to the latest release.

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Send an email to [millsks@gmail.com](mailto:millsks@gmail.com) with:

- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested mitigations

You should receive a response within 48 hours. If the issue is confirmed, a patch will be released as soon as possible and you will be credited in the release notes (unless you prefer to remain anonymous).

## Scope

`conventional-commit-hook` reads a single local file (the commit message) and writes to stderr. It makes no network requests, spawns no subprocesses, and holds no credentials. The attack surface is intentionally minimal.

Vulnerabilities in third-party dependencies (structlog, pre-commit) should be reported to those projects directly.
