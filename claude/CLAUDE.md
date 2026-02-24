# Global Claude Code Instructions

## CI Requirements

Before creating or updating a PR, run the project's lint and format checks and fix any issues before pushing. Check the Makefile, CI config, or README for the correct commands.

## Testing Requirements

- A PR that modifies logic must always include a test demonstrating the change is applied. This makes it easier for reviewers to verify the code is functional and correct.
- When adding or updating tests, follow the existing test patterns in the project.
- Tests should demonstrate that business logic and edge cases work correctly — focus on what a PR reviewer needs to see to gain confidence. Cover the core behavior, ranking/tiebreaking, boundary conditions, and any non-obvious nuances. Avoid redundant cases that test the same thing twice; keep tests compact and purposeful.

## Git Conventions

- Never force push. Always push new commits instead.
- Only amend commits if explicitly asked to. On PR review feedback, push new commits to preserve review history.
- Branch names: `$USER/<short-description-of-change>`
- When an instruction is ambiguous, ask for clarification before acting. Don't assume — wrong guesses waste time even if they're reversible.
- **Never push commits or create PRs without explicit approval.** After committing locally, stop and let the user review the diff before pushing. The user will tell you when to push and create the PR.

## Convention Matching

Before writing any new code or files, study the existing codebase conventions and match them exactly:

- **New entries in structured files** (YAML configs, source definitions, schema files): Audit sibling entries and replicate every field they use — descriptions, metadata tags, annotations, etc. If every existing entry has a field, the new entry must too.
- **New files** (models, tests, macros, configs): Read 2-3 existing files of the same type in the same repo and match their structure, field ordering, formatting, and style. A new YAML model should look like the other YAML models; a new test file should match the test conventions.
- **New code** (SQL, Python, etc.): Follow the patterns established in surrounding files — naming conventions, comment style, whitespace, import ordering, etc.

Treat existing files as the spec. When in doubt, match what's already there rather than inventing a new pattern.

## DRY (Don't Repeat Yourself)

- Extract common patterns and only parameterize the parts that actually vary. If the same expression appears in multiple branches with only one token different, factor out the shared structure and vary only that token.

## SQL Style

- Avoid `SELECT *` and `SELECT table.*`. List columns explicitly so the query is self-documenting and resilient to upstream schema changes. Exception: when the column list is so large it would be unwieldy.

## Integrity

- Never fabricate URLs, citations, commands, CLI flags, tool features, API names, or any other factual claim. This includes things "remembered" from training data — those hallucinate just as often as web searches. If you can't verify something exists, say so.
- When citing sources, include the direct URL so the user can verify.
- Before suggesting any command, config change, or tool usage you aren't certain about, verify it first — read the actual config, run a help command, or check the docs. Never propose a fix you haven't confirmed will work.
- Stay within scope. Only change files directly related to the task. No drive-by improvements.

## Problem Solving

- Investigate before proposing. Read the current state (configs, files, logs, error messages) before suggesting any fix. Never propose changes to a system you haven't inspected.
- Solve root causes, not symptoms. When something is broken, diagnose why — don't offer workarounds or quick patches unless explicitly asked for a temporary fix.
- When you don't know something, say "I don't know" and investigate. Don't guess, don't bluff, don't suggest things that might work. Uncertainty is fine; false confidence wastes time.

## Communication

- Always search from the repo root, not just the current working directory.
- Never suggest merging PRs. Just push commits and let the user handle merging via GitHub UI.
- Don't echo back the user's request. Just do the work.
- Don't suggest follow-up actions or ask "would you like me to..." at the end of responses. Just finish and let the user direct next steps.
