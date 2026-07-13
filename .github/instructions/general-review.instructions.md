---
applyTo: "**"
---

# General Code Review Instructions

## Before You Start: Understand CI Coverage

Before reviewing any file, identify what linters, formatters, type checkers, and tests run in CI for that file type. Read the CI config and Makefile (or equivalent). Anything CI already enforces is out of scope for your review. Do not speculate about whether code violates a rule that CI would catch. If CI passes, the code satisfies those checks.

## Scope

Only comment on lines that were **added or modified** in the pull request diff. Do not comment on pre-existing code that appears in the diff context but was not changed. If a function signature, type annotation, or variable was not touched by the PR, it is out of scope. File a separate issue instead of blocking the current PR.

## What to Comment On / What to Never Comment On

### Comment on

- Bugs, logic errors, or incorrect behavior
- Data loss or data corruption risks
- Missing dependencies between resources or tasks
- Security vulnerabilities
- Missing test coverage for changed behavior

### Never comment on

- **Formatting, whitespace, or trailing commas** -- CI handles this
- **Variable or parameter naming** that follows existing conventions in the codebase
- **Cosmetic renames** on working code
- **Test data values** unless they cause test failures
- **Magic numbers** that are standard in the domain (e.g., HTTP status codes, common thresholds)
- **Auto-generated file content** such as lockfiles, compiled output, or CI-generated artifacts
- **Descriptions or comments** -- do not suggest rewording unless factually incorrect
- **PR metadata** (titles, descriptions, commit messages)
- **Tests for unchanged behavior** -- only flag missing tests for behavior that was added or modified in the PR
- **Tests for simple configuration values** (e.g., timeouts, delays, thresholds, feature flags) -- only request tests for behavioral logic
- **Hypothetical edge cases in heuristics** -- if code describes an approximate rule, do not list theoretical counterexamples. Only comment if the heuristic is wrong in the common case for this codebase.
- **Refactoring suggestions** without a clear bug or maintainability problem
- **Docstrings or comments** on self-documenting code

## Before Posting a Comment

Every gate must pass. If any fails, do not post.

1. **90% confident it is a real defect.** A bug, data loss risk, security vulnerability, or incorrect behavior. Design preferences, portability suggestions, and hypothetical concerns are not defects.
2. **Not already caught by CI.** If CI enforces the rule (per the coverage you identified before starting), do not comment. If you believe CI missed something, propose an improvement to CI, not a code comment.
3. **Verified the claim.** Search the codebase for the same pattern; if it exists elsewhere and works, it is not a bug. Check runtime, platform, and tool docs. Read the full file context, not just the diff hunk. Confirm variables and config fields are not platform-provided built-ins before flagging them as undefined.
4. **Evidence or CI proposal.** Show proof (failing test, doc citation, reproduction steps) or propose a concrete linter rule, test, or CI step that would catch this class of issue. No unsupported "this looks wrong."
5. **Not a nitpick.** "Will this break, lose data, or produce wrong results, or am I suggesting a different way to express the same correct idea?" If the latter, do not post.
6. **Not a duplicate.** One comment at the most relevant location. List other occurrences in that comment.

## Comment Format

1. Problem (1 sentence)
2. Why it matters
3. Suggested fix
4. Suggested test or linter rule that would prevent this class of issue from reaching the PR phase

Concise. No praise, no filler.
