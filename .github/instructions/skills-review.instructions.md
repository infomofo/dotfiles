---
applyTo: "skills/**/*.md"
excludeAgent: "cloud-agent"
---

- Embedded code snippets in skill files are illustrative. Do not raise a comment about a missing defensive check unless the code would crash on a plausible real-world input given the described usage context.
- Before claiming a code snippet has a syntax error or structural defect (e.g., unbalanced braces, missing closing tokens), verify the claim by carefully reading the full snippet. Do not raise a comment if the code is correct.
- Do not flag hardcoded identifiers when the surrounding text explains what they refer to and documents how to re-derive them if needed.
- Do not suggest replacing author-type checks with an explicit allowlist when the surrounding text explains the convention is intentional.
- Before flagging a variable, placeholder, or frontmatter field in a skill file as undefined, missing, or unsupported, verify whether it is a platform-provided built-in or a convention documented in the skill. If context explains what it provides, do not flag it as a user error.
- Before flagging a command as incompatible with a platform, verify the claim against that platform's actual version. "GNU compatible" labels, man pages, and version-specific docs are authoritative — do not assume incompatibility based on general platform reputation.
- Before flagging a command invocation as malformed based on argument ordering, verify that specific tool's documented parsing behavior. Do not assert a universal rule about where options may or may not appear.
- Referencing bundled skill resource scripts via relative markdown links follows the convention documented in the skill platform documentation. Do not flag the absence of a separate shell invocation command.
