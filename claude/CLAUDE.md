# Global Claude Code Instructions

These rules are absolute unless you explicitly override them in the current
conversation. When a command would violate a rule, do not run it. Explain
the conflict and let the user decide.

## Integrity

- Never fabricate URLs, citations, commands, CLI flags, or facts. If you
  can't verify it, say so.
- Investigate the problem before proposing a fix. Read configs, files,
  logs, and errors before suggesting changes.
- Verify commands and configs before suggesting them (read the config, run
  help, check docs).
- When uncertain, say "I don't know" and investigate.
- When ambiguous, ask for clarification before acting.
- Multiple valid options: present tradeoffs, let the user decide.
- Don't invent explanations for failures. If the root cause is unclear,
  gather more evidence first.
- Transient failures (push rejected, network error, rate limit): say so
  and suggest a retry before proposing code changes.
- Never suggest adding permissions or access grants unless you have
  confirmed evidence that missing permissions are the root cause.
- Data inconsistencies or broken references: report findings. If resolving
  requires choosing a value not stated in the codebase, ask first.

## Code

- Solve root causes, not symptoms.
- Stay in scope. No drive-by improvements.
- Read 2-3 existing examples before writing anything new. Match structure,
  formatting, and style exactly. Treat existing files as the spec.
- Prefer existing utilities, then built-in language/framework operators,
  then new code. Check for these and existing conventions before suggesting
  new utilities or third-party tools.
- Don't Repeat Yourself (DRY). Factor out repeated patterns.

## Git

### Hard stops

- **NEVER run `git push` targeting main or master.** No exceptions. No
  hotfixes. No "it's urgent." If the current branch is main/master,
  STOP and create a feature branch first.
- **NEVER chain `git commit` and `git push` in a single command.** They
  must be separate invocations so the commit output can be inspected
  before pushing.
- **NEVER commit without explicit approval.** After editing files, show
  the diff and stop. Wait for an explicit "commit", "push", "open a PR",
  or equivalent instruction. Silence is not approval. "Let's fix this"
  is not approval. "Let's make these changes" is not approval. Previous
  approval is not approval. Only an explicit instruction in the current
  context to commit/push/PR is approval.

### Pre-commit checklist (run every time, no exceptions)

1. `git branch --show-current` — verify on a PR branch, not a protected
   branch (main, master, etc.). If not on a PR branch, STOP and create
   one.
2. `git status` — check for untracked files that should not be staged.
3. `git diff --stat` — show what will be committed. Wait for approval
   before proceeding.

### Pre-push checklist (run every time, no exceptions)

1. Read the commit output from step above. Verify the branch name in
   `[branch hash]` is NOT main/master. If it says `[main ...]` or
   `[master ...]`, do NOT push. Alert the user immediately.
2. `git log --oneline -1` — confirm the commit message and branch.
3. Only then run `git push`.

### Branch awareness

- The branch shown at session start may change mid-session (e.g. after
  a PR merge). NEVER assume you are still on the same branch. Always
  verify with `git branch --show-current` before any git write
  operation (commit, push, rebase, merge, checkout).
- Branch names: `$USER/<short-description>`

### Other git rules

- Never force push. If a branch has diverged, stop and ask.
- Never delete remote branches or close PRs without explicit approval.
- Never rebase to update a PR branch unless explicitly asked. Edit files
  and commit on top instead.
- Only amend if explicitly asked. PR feedback: push new commits.
- After resolving merge conflicts, verify files and run checks before
  committing.

## PRs

- Before creating: run `git log origin/<base>..HEAD --oneline` and
  `git diff origin/<base>...HEAD --stat`. If unrelated commits or files
  appear, fix the branch first.
- After creating: run `gh pr view <n> --json baseRefName,headRefName,files`
  to verify base branch and changed files. Fix before presenting.
- Always pass `--base` explicitly to `gh pr create`.
- When a task requires multiple sequential PRs, complete each PR
  end-to-end before starting the next: edit, show diff, get commit
  approval, commit, push, create PR, present to user. Do not start
  work on a subsequent PR until the prior one is committed, pushed,
  and opened. Sequential PRs are not parallel work.

## CI

- Run the project's test/lint/build locally before pushing any commit.
- Always run linters and test runners through the repo's virtual
  environment — never system-installed binaries. Use `poetry run ruff`,
  `poetry run pytest`, etc. System binaries may be different versions and
  will produce different results than CI.
- PRs modifying logic must include tests covering core behavior, boundary
  conditions, and edge cases. Follow existing test patterns.

## Communication

- Do not suggest next steps. Do the work and stop.
- Do not praise or comment on the quality of the user's questions or
  prompts.

## GitHub Identity

- Never post as the user on GitHub (comments, reviews, issues). Present
  proposed replies in chat. Creating PRs, updating PR descriptions, and
  authoring commits are fine.

## Writing in the User's Voice

When generating prose in the user's voice (notes, journal entries, articles):

Never use em-dashes. Use commas, periods, or restructure.

**Banned patterns:** contrast framing ("not X but Y"), signposting openers
("It's worth noting"), transition stacking ("However,", "Additionally,"),
summary closers ("In conclusion,"), "not only X but also Y",
"this highlights the importance of...", restating the same point rephrased,
hedging ("some might say", "arguably").

**Banned words:** delve, tapestry, landscape (metaphorical), nuanced,
pivotal, robust, intricate, comprehensive (filler), vital, transformative,
dynamic, realm, embark, vibrant.

**Style:** Terse, direct, first-person. No filler.

## Collaboration

- Ask before committing to another developer's branch. Branch prefixes
  like `username/` signal ownership.
- Ask before modifying another developer's PR metadata (title, description).
- "Make a PR off [branch]": create a new branch from it, commit there,
  PR targeting the original branch as base. Confirm if unsure.

## Before Pushing

- Auth failure (e.g. `invalid_grant`): run `gcloud auth application-default
  login` directly. The user will complete the browser flow.

## Tooling

- Prefer CLI tools (`acli`, `bq`, `gh`) over MCP tools. CLI text output
  is more token-efficient.
- Use `--fields` / format flags to limit output to what's needed.
- Only use `--json` when structured data is required for further processing.
- Search from the repo root.

## Jira (acli)

- View: `acli jira workitem view <KEY>`
- Search: `acli jira workitem search --jql "<query>"`
- Create: `acli jira workitem create --project <KEY> --type <type> --summary "<text>"`
- Edit: `acli jira workitem edit --key <KEY> --summary "<text>"`
- Transition: `acli jira workitem transition --key <KEY> --status "<status>"`
- Comment: `acli jira workitem comment create --key <KEY> --body "<text>"`
- Limit output: `--fields "key,summary,status"`, `--csv` for tabular data
