---
applyTo: "skills/**/*.md"
excludeAgent: "cloud-agent"
---

- Embedded code snippets in skill files are illustrative. Do not raise a comment about a missing defensive check unless the code would crash on a plausible real-world input given the described usage context.
- Before claiming a code snippet has a syntax error or structural defect (e.g., unbalanced braces, missing closing tokens), verify the claim by carefully reading the full snippet. Do not raise a comment if the code is correct.
- Do not flag hardcoded bot node IDs (e.g., `BOT_kgDOCnlnWA`) when the surrounding text explains what the ID refers to and documents how to re-derive it if needed.
- Do not suggest replacing `!= 'Bot'` checks on GitHub GraphQL `__typename` fields with an explicit allowlist. The convention in this codebase is that `'Bot'` identifies all automated actors; any non-Bot author is treated as human. This is intentional.
