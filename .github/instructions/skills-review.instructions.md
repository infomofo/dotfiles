---
applyTo: "skills/**/*.md"
excludeAgent: "cloud-agent"
---

- Embedded code snippets in skill files are illustrative. Do not raise a comment about a missing defensive check unless the code would crash on a plausible real-world input given the described usage context.
- Before claiming a code snippet has a syntax error or structural defect (e.g., unbalanced braces, missing closing tokens), verify the claim by carefully reading the full snippet. Do not raise a comment if the code is correct.
- Do not flag hardcoded identifiers when the surrounding text explains what they refer to and documents how to re-derive them if needed.
- Do not suggest replacing author-type checks with an explicit allowlist when the surrounding text explains the convention is intentional.
- Before flagging a variable, placeholder, or frontmatter field in a skill file as undefined, missing, or unsupported, verify whether it is a platform-provided built-in or a convention documented in the skill. If context explains what it provides, do not flag it as a user error.
- Before flagging a shell command as broken due to a seemingly missing argument, verify the command's actual default behavior rather than assuming it fails.
- Before flagging a command invocation as malformed based on argument ordering, verify the tool's actual parsing behavior. Option flags starting with `-` are parsed as options regardless of their position relative to the pattern or other operands — do not assume they are treated as filenames.
- Referencing scripts via relative markdown links is the established pattern for bundled skill resources. Do not flag the absence of a separate shell invocation command.
