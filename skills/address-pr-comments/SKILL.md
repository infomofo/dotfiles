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

Fetch all review threads (up to 100) using GraphQL, then filter locally to those that are unresolved and not outdated. Note: if a PR has more than 100 threads, threads beyond the first 100 will be silently skipped — this is acceptable for typical PRs.

```bash
gh api graphql -f query='
query {
  repository(owner: "{owner}", name: "{repo}") {
    pullRequest(number: {number}) {
      reviewThreads(first: 100) {
        nodes {
          id
          isResolved
          isOutdated
          comments(first: 1) {
            nodes {
              path
              line
              body
              author { login __typename }
            }
          }
        }
      }
    }
  }
}' | python3 -c "
import json, sys
data = json.load(sys.stdin)
if 'errors' in data:
    sys.exit('GraphQL errors: ' + json.dumps(data['errors']))
pr = data.get('data', {}).get('repository', {}).get('pullRequest')
if not pr:
    sys.exit('PR not found or insufficient permissions')
threads = pr['reviewThreads']['nodes']
for t in threads:
    if t['isResolved'] or t['isOutdated']:
        continue
    if not t['comments']['nodes']:
        continue
    c = t['comments']['nodes'][0]
    print(f\"[{c['author']['login']} / {c['author']['__typename']}] {c['path']}:{c.get('line')} thread:{t['id']}\")
    print(c['body'][:300])
    print()
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

## Identify and Triage Comments

A comment is agent-sourced when `author.__typename == "Bot"` or the login contains `copilot`, `claude`, `github-advanced-security`, or `dependabot`.

Human comments: fix the issue if it's valid. If not, surface them to the user verbatim without acting.

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

## Plan and Present — Wait for Approval

**Before touching any files**, present the full action plan to the user:

```
## PR Comment Action Plan

**Fix in code:**
- `src/foo.vue` — [one-line description of what and why]

**Update .github/instructions/:**
- `vue.instructions.md` (applyTo: src/**/*.vue) — add rule: [exact rule text]

**Human comments requiring your attention:**
- [verbatim quote, file:line]
```

Only include sections that have content. Omit any section with nothing to report.

Wait for explicit user approval before making any changes. Do not proceed until the user confirms.

## Apply Fixes

Once approved, apply changes in this order:

1. **Code fixes**: read the file and surrounding context, apply the minimum surgical change, do not make unrelated edits.
2. **Instruction updates**: follow the naming and frontmatter conventions already present in the repo:
   - File names: `<topic>.instructions.md` — e.g. `review.instructions.md`, `vue.instructions.md`, `javascript.instructions.md`
   - Frontmatter: `applyTo:` scoped to the relevant file glob — e.g. `"src/**/*.vue"`, `"**/*.js,**/*.mjs"`, `"**"` for repo-wide
   - Scope `applyTo` to match the type of file the comment was about — do not use `"**"` when a narrower glob fits
   - For review-only rules, add `excludeAgent: "cloud-agent"` so they apply to Copilot code review but not the coding agent
   - Rules must be specific and concrete:
     - Good: `- Do not comment on import ordering — the project does not enforce a specific order.`
     - Bad: `- Don't comment on style.`
   - If no `.github/instructions/` directory exists, create one with a scoped `review.instructions.md`.

Run lint and tests to confirm nothing broke.

## Commit and Push

Stage all changed source files and updated/created instructions files together. Write a commit message naming which comments were fixed in code and which were handled by updating instructions. Push to the current branch (the PR branch).

## Resolve Bot Threads

The thread IDs were already fetched above. For each unresolved bot thread that was addressed (fixed in code or handled via instructions), resolve it:

```bash
gh api graphql -f query='
mutation {
  resolveReviewThread(input: { threadId: "{thread_id}" }) {
    thread { isResolved }
  }
}'
```

Never resolve threads where the first comment's author is a human.
