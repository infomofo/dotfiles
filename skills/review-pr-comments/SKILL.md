---
name: review-pr-comments
description: >-
  Processes review comments on the open PR for the current branch. Fixes real
  issues in code; updates .github/instructions/ to prevent low-quality comments
  from recurring.
when_to_use: >-
  Use when the user says "review PR comments", "look at PR feedback", "review
  copilot comments", or invokes this skill by name. Always invoke this skill
  before manually reading PR comments yourself.
user-invocable: true
allowed-tools: Bash(gh *) Bash(python3 *) Bash(git *) Bash(grep *)
---

# Review PR Comments

Processes review comments on the open PR for the current branch. Fixes real issues in code; improves `.github/instructions/` to prevent low-quality comments from recurring.

**This skill has two hard approval gates:**
1. **Action plan gate** — present the full plan and wait for explicit approval before touching any files.
2. **Commit gate** — show the full diff and ask "Approve to commit?" before committing or pushing. This gate fires every time, even if the user approved the action plan.

## Fetch Comments

Get the PR number first:
```bash
gh pr view --json number,url
```
If no open PR exists for the current branch, tell the user and stop.

Fetch all review threads (paginating past 100 if needed) using GraphQL, retrieving up to 100 comments per thread so human replies to bot comments are visible. Before filtering threads, the script also fetches the PR's deleted files so threads on deleted paths are skipped, and skips resolved threads. Outdated bot threads with no human replies are emitted with an `[OUTDATED-BOT]` marker for silent auto-resolution.

Run the bundled [fetch_threads.py](./fetch_threads.py) script from this skill's base directory. It derives `owner`, `repo`, and `number` from `gh` automatically.

The script prints `owner=... repo=... number=...` on the first line — save those values to substitute into the `{owner}/{repo}/{number}` placeholders used in later commands.

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

**Human replies inside bot-opened threads carry the highest priority.** When a human has replied to a bot thread, treat the human's position as authoritative: if they say the issue is real, fix it even if you would otherwise dismiss the bot comment; if they say it's intentional or fine, surface it as a human dismissal. Always show human replies to the user verbatim in the action plan.

If a comment is stale — the issue was already fixed in a prior commit on this branch — and has no human replies, resolve the thread silently and exclude it from the action plan. If it has human replies, surface those verbatim per the human reply rule above.

Threads prefixed `[OUTDATED-BOT]` are outdated bot-opened threads with no human replies. Do not include them in the action plan. Collect their thread IDs and resolve them silently in the "Resolve Bot Threads" step.

## Evaluate Each Comment

**Before triaging any comment, run this checklist:**

1. **Verify the claim in full file context, not just the diff hunk.** If the comment says "X is not imported", "Y is not loaded", or "Z will not work" — read the complete file, not just the changed lines. Do not accept the claim if `import X`, the CDN link, or the config value appears elsewhere in the file or in another file the diff touches.

2. **Search for the same pattern before accepting any "broken" or "incorrect" claim.** Run `grep -r "flagged-pattern" --include="*.ext" -l` across the codebase. If the same pattern exists in other files and CI is passing, the pattern is established — dismiss the comment. Write the instructions rule as a prerequisite, not a prohibition: "Before flagging X, check whether it already appears elsewhere in the project" — not "do not flag X in file Y". This makes the reviewer do the verification work first.

3. **Require evidence for any remaining "broken" claim.** If the pattern is new or the reviewer still claims breakage after checking, require them to supply all three before the claim is actionable: the specific error it produces, the steps to reproduce it, and the linter rule or CI check that would catch it. Write an instructions update stating these requirements.

4. **Distinguish "not the recommended pattern" from "broken".** A pattern that deviates from a framework's documented ideal but produces correct behavior is not a bug. Only treat something as broken if you can state the specific user-visible failure and the exact inputs that trigger it.

5. **Deduplicate before acting.** If a comment is the third (or fifth, or eighth) thread flagging the same issue in this PR, it is a duplicate. Fix the issue once, resolve all duplicate threads together, and add an instructions rule to prevent recurrence. Do not handle each thread individually.

6. **Check branch context.** On `ui/framework-*` evaluation branches, the goal is assessing UI behavior and developer experience, not production optimization. Do not flag tree-shaking, bundle size, wildcard imports, or "not the recommended pattern" concerns on these branches.

---

**Fix the code if the comment identifies:**
- A real bug, logic error, or security issue
- Invalid markup that affects rendering or accessibility
- Dead code — unused, unreachable, or unwired methods/variables
- A correctness issue with the language/framework (wrong key type, invalid nesting, broken API usage)

**When a comment claims code is broken or has a bug:**
1. Check whether an existing test already asserts on the claimed behavior. If one does, the comment is dismissed as incorrect — update `.github/instructions/` to tell the reviewer to check for existing tests before claiming breakage.
2. If no test covers it and the bug is real, fix the code AND add a test that would have caught it.
3. If no test covers it but the bug claim is wrong, add a test that demonstrates the code works correctly, then dismiss via instructions update (see checklist item 3 for what the rule must require).

**Update `.github/instructions/` if the comment:**
- Is a style preference with no correctness impact
- Recommends patterns inconsistent with how the codebase is already written
- Flags intentional decisions that are consistent throughout the codebase
- Repeats the same point across multiple instances of an established pattern
- Is factually wrong, misreads the diff, or points to a non-existent issue — update instructions to prevent that **class** of comment from recurring, not just the specific instance
- Is too vague to produce an actionable change — update instructions to require specificity
- Flags a pattern already caught by an existing CI or linter check — CI enforcement is sufficient; a prose rule is redundant
- Flags a style, formatting, or linting concern not currently caught by CI — the right fix is adding a CI/linter rule, not a manual documentation rule; update instructions to direct the reviewer to propose a CI addition instead of a code review comment

**Instructions updates must address the root cause, not the symptom.** The fix should eliminate that entire class of comment going forward — not suppress a specific file or pattern instance. Test: would a reviewer with no PR history still make the comment after reading the rule? If yes, the rule is too narrow. Prefer prerequisites ("before flagging X, verify Y") over prohibitions ("do not flag X in file Z").

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

**Wait for explicit user approval before making any changes.** End your response with the explicit question: **"Approve to apply?"** This is Gate 1. It covers only applying the fixes listed above — it does not cover committing or pushing. Do not proceed until the user confirms.

## Apply Fixes

Once approved, apply changes in this order:

1. **Code fixes**: read the file and surrounding context. Apply the minimum surgical change. When addressing a valid comment, consider why it slipped through — then generalize: scan all code being introduced in this PR for the same class of issue and fix every instance in the same pass. Do not patch only the reported line.

   **Every code fix must be accompanied by a test, or an explicit written justification for why a test is not needed.** Acceptable reasons to skip a test: the behavior is untestable in jsdom (e.g. browser lifecycle hooks with no observable side effect), or an existing test already covers the corrected behavior. If you skip a test, state the reason in the action plan and in the commit message. Do not silently omit tests.

   After applying each fix, check for side effects: identify all callers and consumers of the changed code and verify they still behave correctly with the new output. A fix that changes the shape or size of a data structure (e.g., adding entries to an exported array) must be followed by a scan of every place that structure is consumed in the PR diff. This is the most common source of second review cycles — the fix is correct in isolation but breaks a consumer.

2. **Instruction updates**: follow the naming and frontmatter conventions already present in the repo:
   - File names: `<topic>.instructions.md` — e.g. `review.instructions.md`, `vue.instructions.md`, `javascript.instructions.md`
   - Frontmatter: `applyTo:` scoped to the relevant file glob — e.g. `"src/**/*.vue"`, `"**/*.js,**/*.mjs"`, `"**"` for repo-wide
   - Scope `applyTo` to match the type of file the comment was about — do not use `"**"` when a narrower glob fits
   - For review-only rules, add `excludeAgent: "coding-agent"` so they apply to Copilot code review but not the coding agent
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

The goal is: after this push, no new bot comment should appear for code that was already in the diff before this commit.

## ⛔ STOP — Present Changes and Wait for Approval to Commit (Gate 2)

Include proactive self-review findings in the summary, clearly labeled **Proactive (self-review)**, so the user can distinguish them from reactive fixes.

**YOU MUST END YOUR RESPONSE HERE** with the diff summary and the explicit question: **"Approve to commit?"** This is Gate 2. Do not write any further tool calls or prose after asking. Do not commit, push, or resolve threads in this same response. Wait for the user's next message.

Once the user explicitly approves Gate 2 (e.g. "commit it", "yes", "ship it", "y", "approved"), commit all changed source and instructions files together in the *next* response. Write a commit message naming which comments were fixed in code and which were handled by updating instructions. Push to the PR branch. Then in that same response, continue with the remaining steps in order: audit the PR title and description, resolve bot threads, and request re-review.

**Approval covers only the gate it was given for, and only the exact diff shown at that moment.**
- Approving Gate 1 ("Approve to apply?") means: go apply the listed fixes. It is not approval to commit.
- Approving Gate 2 ("Approve to commit?") means: commit exactly the diff shown. If any file changes after Gate 2 approval — for any reason — stop, show the new diff, and ask "Approve to commit?" again.
- Do not carry approval forward across gates or across independent changes.

**This is a hard gate — not a soft suggestion.** Do not treat any response as Gate 2 approval unless it comes *after* you have shown the full diff of changes made and explicitly asked "Approve to commit?".

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

Never resolve threads where the first comment's author is a human. Never resolve a bot-opened thread that has human replies — those require the user's attention.

Also resolve any `[OUTDATED-BOT]` thread IDs from the fetch output — these are outdated bot threads with no human replies and should always be closed silently, regardless of whether their content was acted on.

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
