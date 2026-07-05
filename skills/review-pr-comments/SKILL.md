---
name: review-pr-comments
description: >-
  Reviews and acts on PR review comments from agent sources (Copilot, Claude, etc.).
  Fetches active comments on the current branch's open PR, critically evaluates each one,
  and either fixes the code or updates .github/instructions/ to improve future reviews,
  reduce token usage, and lower turnaround time. Use when the user says "review PR comments",
  "look at PR feedback", "review copilot comments", or invokes this skill by name.
  Always invoke this skill before manually reading PR comments yourself.
  NOTE: This skill has two explicit approval gates — one before applying any fixes,
  one before committing. Do not commit or push without explicit user approval.
  Once the user approves to commit, commit immediately — do not ask a third time.
user-invocable: true
---

# Review PR Comments

Processes review comments on the open PR for the current branch. Fixes real issues in code; improves `.github/instructions/` to prevent low-quality comments from recurring.

## Fetch Comments

Get the PR number first:
```bash
gh pr view --json number,url
```
If no open PR exists for the current branch, tell the user and stop.

Fetch all review threads (up to 100) using GraphQL, retrieving only the first comment of each thread (sufficient for triage). Before filtering threads, also fetch the PR's deleted files so threads on deleted paths can be skipped — those comments are stale by definition.

Substitute `{owner}` and `{repo}` from the current repository (e.g., via `gh repo view --json owner,name`) and `{number}` from the PR number fetched above.

First, get the list of deleted files in the PR:
```bash
gh api repos/{owner}/{repo}/pulls/{number}/files \
  | python3 -c "
import json, sys
files = json.load(sys.stdin)
deleted = {f['filename'] for f in files if f.get('status') == 'removed'}
print('\n'.join(sorted(deleted)))
"
```

Then fetch threads, skipping any whose path is in the deleted files set:

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

# Pass deleted_files as a comma-separated env var, or leave empty
import os
deleted = set(os.environ.get('DELETED_FILES', '').split(',')) - {''}

threads = pr.get('reviewThreads', {}).get('nodes', [])
for t in threads:
    if not t:
        continue
    if t.get('isResolved'):
        continue
    comments = t.get('comments', {}).get('nodes') or []
    if not comments:
        continue
    c = comments[0]
    path = c.get('path') or ''
    if path in deleted:
        continue  # thread is on a deleted file — skip, stale by definition
    # isOutdated means the line shifted after a new commit, not that the issue is gone.
    # Still triage these — the code may still have the problem.
    author = c.get('author') or {}
    print(f\"[{author.get('login', 'unknown')} / {author.get('__typename', 'unknown')}] {path}:{c.get('line')} thread:{t.get('id')}\")
    print(c.get('body', '')[:300])
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

A comment is agent-sourced when `author.__typename == "Bot"` (GraphQL) or `user.type == "Bot"` (REST). These are different fields in different API responses — apply the correct check for each source.

Human comments: fix the issue if it's valid. If not, surface them to the user verbatim without acting.

## Evaluate Each Comment

**Fix the code if the comment identifies:**
- A real bug, logic error, or security issue
- Invalid markup that affects rendering or accessibility
- Dead code — unused, unreachable, or unwired methods/variables
- A correctness issue with the language/framework (wrong key type, invalid nesting, broken API usage)

**When a comment claims code is broken or has a bug:**
1. Check whether an existing test already asserts on the claimed behavior. If one does, the comment is dismissed as incorrect — update `.github/instructions/` to tell the reviewer to check for existing tests before claiming breakage.
2. If no test covers it and the bug is real, fix the code AND add a test that would have caught it.
3. If no test covers it but the bug claim is wrong, add a test that demonstrates the code works correctly, then dismiss via instructions update.

**Update `.github/instructions/` if the comment:**
- Is a style preference with no correctness impact
- Recommends patterns inconsistent with how the codebase is already written
- Flags intentional decisions that are consistent throughout the codebase
- Repeats the same point across multiple instances of an established pattern
- Is factually wrong, misreads the diff, or points to a non-existent issue — update instructions to prevent that class of comment from recurring
- Is too vague to produce an actionable change — update instructions to require specificity

**A comment can require both a code fix and an instructions update.** For example, a comment may correctly identify one real issue while also making a factually wrong claim (e.g. flagging valid syntax as an error). In that case: fix the real issue in code AND add an instructions rule to suppress the wrong claim in future reviews.

## Plan and Present — Wait for Approval to Apply

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

**Wait for explicit user approval before making any changes.** This approval only covers applying the fixes — it does not cover committing or pushing. Do not proceed until the user confirms.

## Apply Fixes

Once approved, apply changes in this order:

1. **Code fixes**: read the file and surrounding context. Apply the minimum surgical change. When addressing a valid comment, consider why it slipped through — then generalize: scan all code being introduced in this PR for the same class of issue and fix every instance in the same pass. Do not patch only the reported line.

   **Every code fix must be accompanied by a test, or an explicit written justification for why a test is not needed.** Acceptable reasons to skip a test: the behavior is untestable in jsdom (e.g. browser lifecycle hooks with no observable side effect), or an existing test already covers the corrected behavior. If you skip a test, state the reason in the action plan and in the commit message. Do not silently omit tests.

   After applying each fix, check for side effects: identify all callers and consumers of the changed code and verify they still behave correctly with the new output. A fix that changes the shape or size of a data structure (e.g., adding entries to an exported array) must be followed by a scan of every place that structure is consumed in the PR diff. This is the most common source of second review cycles — the fix is correct in isolation but breaks a consumer.

   When editing the embedded Python snippets in this file, verify all of these defensive patterns are present before committing:
   - `errors` key checked in GraphQL response before traversing `data`
   - All nested dict access uses `.get()` (e.g., `pr.get('reviewThreads', {}).get('nodes', [])`)
   - Null thread nodes guarded: `if not t: continue`
   - `isResolved`/`isOutdated` accessed via `.get()`
   - Null `author` guarded: `author = c.get('author') or {}`
   - Empty `nodes` list guarded before indexing
   - `body`/`path`/`line` accessed via `.get()` with safe defaults
2. **Instruction updates**: follow the naming and frontmatter conventions already present in the repo:
   - File names: `<topic>.instructions.md` — e.g. `review.instructions.md`, `vue.instructions.md`, `javascript.instructions.md`
   - Frontmatter: `applyTo:` scoped to the relevant file glob — e.g. `"src/**/*.vue"`, `"**/*.js,**/*.mjs"`, `"**"` for repo-wide
   - Scope `applyTo` to match the type of file the comment was about — do not use `"**"` when a narrower glob fits
   - For review-only rules, add `excludeAgent: "cloud-agent"` so they apply to Copilot code review but not the coding agent
   - Rules must be specific and concrete:
     - Good: `- Do not comment on import ordering — the project does not enforce a specific order.`
     - Bad: `- Don't comment on style.`
   - If no `.github/instructions/` directory exists, create one with a scoped `review.instructions.md`.
3. **Run lint and tests** after ALL changes (code fixes + instruction
   updates) are applied. Do not proceed to the next step until they
   pass. If any file was modified since the last test run, rerun.

4. **Accuracy audit of changed code and surrounding context.** For every file modified in this skill run, read the current state of the file and check:
   - Inline comments and doc comments that reference the changed code: do they still describe what the code actually does?
   - Comments that reference line numbers, method names, variable names, or behavior that was altered: update them to match reality.
   - Any test descriptions (`it(...)`, `describe(...)`, assertion messages) that describe the behavior under test: confirm they still match what the code does.
   - Any README or `.github/instructions/` content that documents the changed behavior: verify it is still accurate and update if not.
   - Dead comments: comments that described a previous approach and no longer apply. Remove them.

   This step is about internal consistency. It is not a code review. Do not introduce new logic — only fix stale prose and comments.

## Self-Review Pass — Anticipate the Next Cycle

After all reactive fixes are applied and tests pass, perform a pre-flight self-review of the **full PR diff** to catch anything a future bot review would flag, before the push triggers another cycle.

```bash
gh pr view --json baseRefName --jq '.baseRefName'
# then:
git diff origin/<base>...HEAD
```

Load every file in `.github/instructions/` and match each file's `applyTo` glob against the changed files in the diff. For each changed file, apply the rules from every matching instructions file as if you are the reviewer.

For each potential finding, apply the same triage logic as the **Evaluate Each Comment** section above.

**Mandatory proactive checks** — run these explicitly on the full diff, every time:

1. **Em-dashes.** Run `grep -rn " — " <all files touched by the diff>`. Fix every instance found. This is the single most common source of repeat bot comments. Do not rely on memory or the reviewer to catch them.

2. **Clickable elements without keyboard accessibility.** For every element introduced in the diff that has a click handler, verify it is keyboard reachable and has a visible or programmatic label. The specific requirements vary by framework — check the project's existing conventions for how interactive non-button elements are made accessible (e.g., native button, role, tabindex, framework-specific props). Flag every element that diverges from that pattern and fix all instances in the same pass.

3. **Lint with a clean cache.** Before presenting the final diff, run the project's lint command with any caches cleared if the project uses a build-tool-integrated linter. Stale caches from other branches can produce false positives or suppress real errors.

4. **Conflict resolution completeness.** If this skill run involved resolving merge conflicts, run lint immediately after resolution before doing anything else. Conflict markers can leave structurally broken templates that pass a visual check but fail the parser.

5. **Duplicate comment deduplication.** When the same logical issue is flagged in multiple threads (e.g., em-dashes in three files), treat them as a single fix item. Fix all instances in one pass and resolve all related threads together. Do not address one thread and leave identical threads open.

The goal is: after this push, no new bot comment should appear for code that was already in the diff before this commit.

## ⛔ STOP — Present Changes and Wait for Approval to Commit

Include proactive self-review findings in the summary, clearly labeled **Proactive (self-review)**, so the user can distinguish them from reactive fixes.

**YOU MUST END YOUR RESPONSE HERE** with the diff summary and the explicit question: "Approve to commit?" Do not write any further tool calls or prose after asking. Do not commit, push, or resolve threads in this same response. Wait for the user's next message.

Once the user explicitly approves (e.g. "commit it", "yes", "ship it", "y", "approved"), commit all changed source and instructions files together in the *next* response. Write a commit message naming which comments were fixed in code and which were handled by updating instructions. Push to the PR branch. Do NOT ask for approval again after the user has already approved — if they said "y" or equivalent in response to "Approve to commit?", that IS the approval; proceed immediately with the commit in that same response.

**This is a hard gate — not a soft suggestion.** Do not treat the user approving the *action plan* as approval to commit. Do not treat "yes", "go ahead", "defer it", or any other mid-flow response as commit approval unless it comes *after* you have shown the full diff of changes made and explicitly asked "Approve to commit?". If you skip this gate, you have violated the skill contract. However: once the user says "y" or equivalent after being shown "Approve to commit?", that is final — do not ask a third time.

## Audit PR Title and Description

Before requesting re-review, fetch the current PR title and body and check them against the actual state of the diff:

```bash
gh pr view --json title,body --jq '"Title: " + .title + "\n\nBody:\n" + .body'
```

Compare each claim in the title and body against `git diff origin/<base>...HEAD`. Flag any:
- Features or behaviors claimed that are no longer present or were changed
- Implementation details (component names, method names, file paths) that were renamed or removed
- Scope descriptions that no longer match the actual files changed

Update the PR title and/or body if inaccuracies are found:
```bash
gh pr edit --title "Accurate title" --body "Updated description"
```

Do this step silently — only surface changes to the user if the title or body required correction.

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

## Request Re-review

After resolving threads, re-request a Copilot review via GraphQL. The REST API and `gh pr edit --add-reviewer` don't support bots, but the GraphQL `requestReviews` mutation has a `botIds` field that does — including re-requesting after a bot has already reviewed.

Step 1 — get the PR node ID:
```bash
gh api graphql -f query='
query {
  repository(owner: "{owner}", name: "{repo}") {
    pullRequest(number: {number}) { id }
  }
}'
```

Step 2 — request the review:
```bash
gh api graphql -f query='
mutation {
  requestReviews(input: {
    pullRequestId: "{pr_node_id}",
    botIds: ["BOT_kgDOCnlnWA"]
  }) {
    pullRequest {
      reviewRequests(first: 100) {
        nodes { requestedReviewer { ... on Bot { login } } }
      }
    }
  }
}'
```

`BOT_kgDOCnlnWA` is the node ID for `copilot-pull-request-reviewer` on github.com. If it ever needs to be re-derived: `gh api /users/copilot-pull-request-reviewer --jq .node_id`. If the mutation returns the bot login in `reviewRequests`, the re-request succeeded.
