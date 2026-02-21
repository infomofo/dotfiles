# Global Claude Code Instructions

## Git Safety

- **Never force push** (`git push --force`, `git push --force-with-lease`, or `git push -f`) without explicitly asking for confirmation first. Prefer merging or other non-destructive approaches when possible.
- **Never amend commits that have been pushed or reviewed** — always create a new commit to preserve accurate history and timeline of changes.

## Communication

- **Never suggest merging PRs.** PRs are merged through GitHub's UI, not the CLI. Don't prompt the user to merge — just push commits and let them handle it.
- **Don't echo back the user's request.** Just do the work. If the user says "push this", push it — don't say "let's push this" first.
