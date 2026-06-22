---
name: address-pr-comments
description: >-
  Reviews and acts on PR review comments from agent sources (Copilot, Claude, etc.).
  Fetches active comments on the current branch's open PR, critically evaluates each one,
  and either fixes the code or updates .github/instructions/ to improve future reviews,
  reduce token usage, and lower turnaround time. Use when the user says "address PR comments",
  "look at PR feedback", "review copilot comments", or invokes this skill by name.
  Always invoke this skill before manually reading PR comments yourself.
user-invocable: true
---

# Address PR Comments

Processes review comments on the open PR for the current branch. Fixes real issues in code; improves `.github/instructions/` to prevent low-quality comments from recurring.

## Fetch Comments

Get the PR number first:
```bash
gh pr view --json number,url
```
If no open PR exists for the current branch, tell the user and stop.

Fetch active inline comments (stale comments have `position: null` — ignore them):
```bash
gh api repos/{owner}/{repo}/pulls/{number}/comments \
  | python3 -c "
import json, sys
comments = json.load(sys.stdin)
for c in comments:
    if c.get('position') is not None:
        print(c['user']['login'], c['user']['type'], c['path'], c.get('line'), c['body'][:200])
"
```

Also fetch top-level review summaries from bots:
```bash
gh api repos/{owner}/{repo}/pulls/{number}/reviews \
  | python3 -c "
import json, sys
for r in json.load(sys.stdin):
    if r['user']['type'] == 'Bot' and r.get('body'):
        print(r['user']['login'], r['state'], r['body'][:300])
"
```

## Identify Agent Comments

A comment is agent-sourced when `user.type == "Bot"` or the username contains `copilot`, `claude`, `github-advanced-security`, or `dependabot`.

Human comments: if they identify a valid issue, fix it. If not, surface them to the user without acting.

## Evaluate Each Comment

**Fix the code if the comment identifies:**
- A real bug, logic error, or security issue
- Invalid markup that affects rendering or accessibility
- Dead code — unused, unreachable, or unwired methods/variables
- A correctness issue with the language/framework (wrong key type, invalid nesting, broken API usage)

**Update `.github/instructions/` if the comment:**
- Is a style preference with no correctness impact
- Recommends patterns inconsistent with how the codebase is already written
- Flags intentional decisions that are consistent throughout the codebase
- Repeats the same point across multiple instances of an established pattern
- Is factually wrong, misreads the diff, or points to a non-existent issue — update instructions to prevent that class of comment from recurring
- Is too vague to produce an actionable change — update instructions to require specificity

## Fix Code Issues

Read the file and surrounding context. Apply the minimum surgical change. Do not make unrelated edits in the same pass. Run whatever lint/test scripts exist in the repo to confirm nothing broke.

## Update Instructions

Check for `.github/instructions/` in the repo root. Follow the naming conventions already present in the repo:
- File names: `<topic>.instructions.md` — e.g. `review.instructions.md`, `vue.instructions.md`, `javascript.instructions.md`
- Frontmatter: `applyTo:` scoped to the relevant file glob — e.g. `"src/**/*.vue"`, `"**/*.js,**/*.mjs"`, `"**"` for repo-wide
- Scope `applyTo` to match the type of file the comment was about — do not use `"**"` when a narrower glob fits
- Add a specific, concrete rule. Not vague:
  - Good: `- Do not comment on import ordering — the project does not enforce a specific order.`
  - Bad: `- Don't comment on style.`

If no `.github/instructions/` directory exists, create `review.instructions.md` scoped to the type of file the comment was about, not `"**"` unless the rule genuinely applies to all files. For review-only rules, use `excludeAgent: "cloud-agent"` in the frontmatter so the instructions only apply to Copilot code review, not the coding agent:

```markdown
---
applyTo: "src/**/*.vue"
excludeAgent: "cloud-agent"
---
```

## Commit and Push

Stage all changed source files and updated/created instructions files together. Write a commit message naming which comments were fixed in code and which were handled by updating instructions. Push to the current branch (the PR branch).

## Report to User

- Fixed in code: file path + one-line description per comment
- Updated instructions: the rule added and what comment it prevents
- Human comments that need the user's attention: list them verbatim
