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
- **Never push directly to the default branch (main/master).** Always create a feature branch for PRs.
- **Stop after committing locally.** Never push or create PRs without explicit approval.

## CI and Testing

- Run lint/format checks before pushing (check Makefile, CI config, or README).
- PRs modifying logic must include tests covering core behavior and edge cases.

## Communication

- Search from repo root.
- **Never echo the request, summarize what you did, or suggest next steps.** Just do the work and stop.
- After completing a task, stop. Do not add "You may want to..." or similar.

## DevLoop (Local Dev Server Workflow)

For UI, styling, or layout work where visual verification matters. Automated tests alone are not sufficient for visual/UX changes.

**When to start:**
1. The human says something like "let's devloop this" or "let's devloop on this", OR
2. The approved plan includes a DevLoop/verification section with URLs to check — start **automatically** after implementing, don't wait to be asked

**Spin Up:**
- Check for an existing dev server on the expected port (e.g., `lsof -i :<port> -t`)
- If already running with the same framework, reuse it
- Otherwise, start the dev server as a background/async process

**Iterate:**
- Make small, incremental changes
- Most frameworks hot-reload; config files typically require a server restart
- Tell the human which URL to check and what changed
- Wait for feedback before the next iteration

**Ship It:** When the human approves (e.g., "commit", "ship it", "looks good"):
1. Run tests and build to verify everything works
2. Stop the dev server (kill the process or stop the async task)
3. Commit (and push/PR only if explicitly requested)
4. If the human corrected a pattern during the loop, update AGENTS.md
