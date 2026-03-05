# Global Claude Code Instructions

## Verify Before Acting

- Never fabricate URLs, citations, commands, CLI flags, or any factual claim. If you can't verify it, say so.
- Investigate before proposing. Read the current state (configs, files, logs, errors) before suggesting any fix.
- Before suggesting any command or config change, verify it first — read the config, run a help command, or check the docs.
- Solve root causes, not symptoms. Don't offer workarounds unless explicitly asked for a temporary fix.
- When you don't know something, say "I don't know" and investigate. Uncertainty is fine; false confidence wastes time.
- When an instruction is ambiguous, ask for clarification before acting.
- Stay within scope. Only change files directly related to the task. No drive-by improvements.
- When a change involves choosing between multiple valid options, present the options with tradeoffs and let the user decide before writing the code. Do not pick a default and push it — pause and ask.

## Before Pushing

- **Before pushing ANY commit** (including merge commits), run the project's test/lint/compilation checks locally and confirm they pass. Check the Makefile, CI config, or README for the correct commands. Never push a commit you haven't verified locally.
- If a check fails due to an auth or environment issue (e.g., `invalid_grant`, expired credentials), try to fix it yourself first. For GCP, run `gcloud auth application-default login` directly. Only stop and ask the user if the self-fix doesn't work.

## Testing

- PRs that modify logic must include a test demonstrating the change.
- Follow existing test patterns. Cover core behavior, boundary conditions, and non-obvious nuances. Avoid redundant cases; keep tests compact and purposeful.

## Git Conventions

- Never force push. Always push new commits.
- **Never push directly to main or master.** Always use a feature branch and PR, even for cherry-picks. The only exception is if the user explicitly says to push to main.
- Only amend commits if explicitly asked. On PR review feedback, push new commits to preserve review history.
- Branch names: `$USER/<short-description-of-change>`
- **Never push commits or create PRs without explicit approval.** After committing locally, stop and let the user review the diff.
- **After resolving merge conflicts**, verify the resolved files are correct and run checks before committing. Don't blindly accept `--theirs` or `--ours`.

## Convention Matching

Before writing any new code or files, read 2-3 existing examples of the same type and match their structure, formatting, and style exactly. For structured files (YAML, schemas), replicate every field sibling entries use. Treat existing files as the spec.

## Code Style

- Extract common patterns (DRY). If the same expression appears in multiple branches with one token different, factor out the shared structure.
- SQL: List columns explicitly — avoid `SELECT *` and `SELECT table.*`. Exception: unwieldy column lists.

## Tool Preferences

- Prefer CLI tools (`acli`, `bq`, `gh`, etc.) over MCP tools. CLI text output is far more token-efficient than MCP JSON responses.
- Use `--fields` / format flags to limit output to only what's needed.
- Only use `--json` when structured data is required for further processing.

## Jira (acli)

- View: `acli jira workitem view <KEY>`
- Search: `acli jira workitem search --jql "<query>"`
- Create: `acli jira workitem create --project <KEY> --type <type> --summary "<text>"`
- Edit: `acli jira workitem edit --key <KEY> --summary "<text>"`
- Transition: `acli jira workitem transition --key <KEY> --status "<status>"`
- Comment: `acli jira workitem comment create --key <KEY> --body "<text>"`
- Limit output: `--fields "key,summary,status"`, `--csv` for tabular data

## PR Reviews

- When reviewing PR comments, only look at **unresolved/open** threads by default. Ignore resolved comments unless explicitly asked to review them.
  - To filter by resolution status, use the GraphQL API: `gh api graphql -f query='{ repository(owner: "...", name: "...") { pullRequest(number: N) { reviewThreads(first: 50) { nodes { isResolved comments(first: 10) { nodes { author { login } body path line } } } } } } }' --jq '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false) | ...'`. The REST endpoint `pulls/{id}/comments` does **not** expose resolution status — never use it for PR reviews.

## Communication

- Search from the repo root, not just the current working directory.
- Don't echo back the user's request. Just do the work.
- Don't suggest follow-up actions or ask "would you like me to..." — just finish.
- Never suggest merging PRs. Push commits and let the user handle merging.

## GitHub Identity

- **NEVER post as the user on GitHub.** This includes PR comments, review comments, review submissions, issue comments, and any other content attributed to the user's identity. These are personal speech. Always present proposed replies in chat and let the user post them.
- Acceptable actions that don't impersonate: creating PRs (`gh pr create`), updating PR descriptions, and authoring commit messages — these are workflow artifacts, not personal communication.

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
