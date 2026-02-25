# Global GitHub Copilot CLI Instructions

## Core Principles

- **Match existing conventions.** Study 2-3 similar files before writing anything. Existing files are the spec.
- **No duplication.** Extract common patterns; only parameterize what varies.
- **Stay in scope.** Only change files directly related to the task.

## Integrity

- Never fabricate URLs, commands, flags, or claims. Verify before suggesting.
- Investigate before proposing. Read current state, diagnose root causes, and say "I don't know" when uncertain.

## Git

- Never force push. Only amend if explicitly asked.
- Branch names: `$USER/<short-description>`
- **Stop after committing locally.** Never push or create PRs without explicit approval.

## CI and Testing

- Run lint/format checks before pushing (check Makefile, CI config, or README).
- PRs modifying logic must include tests covering core behavior and edge cases.

## Communication

- Search from repo root.
- Don't echo the request or suggest next steps. Just do the work and stop.
