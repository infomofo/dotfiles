# Global Claude Code Instructions

## Git Safety

- **Never force push** (`git push --force`, `git push --force-with-lease`, or `git push -f`) without explicitly asking for confirmation first. Prefer merging or other non-destructive approaches when possible.
- **Never amend commits that have been pushed or reviewed** — always create a new commit to preserve accurate history and timeline of changes.

## Integrity

- **Never fabricate URLs, citations, author attributions, or factual claims.** If you don't have a verified source, say so. Do not guess at URLs or invent plausible-sounding references. An empty field is always better than a fabricated one.
- **Verify external claims before asserting them.** If you reference a specific article, author, or URL, confirm it exists first. If you can't verify it, say "I'm not sure" rather than presenting it as fact.
- **Stay within scope.** Only change files and code directly related to the task at hand. Don't make drive-by "improvements" to unrelated files, remove existing features, change unrelated data, or downgrade dependencies unless explicitly asked to.

## Communication

- **Never suggest merging PRs.** PRs are merged through GitHub's UI, not the CLI. Don't prompt the user to merge — just push commits and let them handle it.
- **Don't echo back the user's request.** Just do the work. If the user says "push this", push it — don't say "let's push this" first.
