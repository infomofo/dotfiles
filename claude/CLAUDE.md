# Global Claude Code Instructions

## CI Requirements

Before creating or updating a PR, run the project's lint and format checks and fix any issues before pushing. Check the Makefile, CI config, or README for the correct commands.

## Testing Requirements

- A PR that modifies logic must always include a test demonstrating the change is applied. This makes it easier for reviewers to verify the code is functional and correct.
- When adding or updating tests, follow the existing test patterns in the project.

## Git Conventions

- Never force push. Always push new commits instead.
- Only amend commits if explicitly asked to. On PR review feedback, push new commits to preserve review history.
- Branch names: `$USER/<short-description-of-change>`
- When an instruction is ambiguous, ask for clarification before taking any destructive or hard-to-reverse action.

## Integrity

- Never fabricate URLs, citations, or factual claims. If you can't verify something, say so — don't present it as fact.
- When citing sources, include the direct URL so the user can verify.
- Never confidently assert something when uncertain. If a search comes up empty, say so — don't declare it doesn't exist.
- Stay within scope. Only change files directly related to the task. No drive-by improvements.

## Communication

- Always search from the repo root, not just the current working directory.
- Never suggest merging PRs. Just push commits and let the user handle merging via GitHub UI.
- Don't echo back the user's request. Just do the work.
