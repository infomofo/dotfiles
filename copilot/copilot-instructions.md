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

## Writing in the User's Voice

When generating prose content in the user's voice (notes, journal entries, wiki articles):

### Banned structural patterns
- **No em-dashes.** Never use — in generated text. Use a comma, period, or rewrite the sentence.
- **No contrast framing.** "not X but Y", "less X more Y", "X rather than Y". Just say the thing directly.
- **No signposting openers.** Never start a sentence with "It's worth noting that", "It's important to note that", "Notably,", "That being said,", "To be clear,"
- **No transition stacking.** Avoid starting sentences with "However,", "Additionally,", "Furthermore,", "Moreover,". These are paragraph filler.
- **No summary closers.** Never write "In conclusion,", "In summary,", "To summarize," or any equivalent.
- **No "not only X, but also Y"** parallel structure.
- **No "this highlights the importance of..."** or "this means that..." as sentence openers.

### Banned words
These are statistically anomalous in AI output and are instant tells:
delve, tapestry, landscape (in metaphorical use), nuanced, pivotal, robust, intricate, comprehensive (as a filler adjective), vital, transformative, dynamic, realm, embark, vibrant

### Prose habits to avoid
- Hedging every opinion: "some might say", "arguably", "one could argue". Take a position or say nothing.
- Generic examples ("a business might...") instead of specific real ones.
- Over-balanced "both sides" framing that avoids committing to a view.
- Restating the same point rephrased in the next sentence.
- Match the terse, personal, first-person style of existing notes.

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
