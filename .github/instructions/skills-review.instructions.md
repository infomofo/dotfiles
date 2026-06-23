---
applyTo: "skills/**/*.md"
excludeAgent: "cloud-agent"
---

- Do not raise multiple separate comments for the same category of defensive coding gap (e.g., missing `.get()` guards, null checks, empty list guards) across consecutive review cycles. If a pattern of missing defensive checks exists, surface all instances in a single comment rather than one per review.
- Embedded code snippets in skill files are illustrative. Do not raise a comment about a missing defensive check unless the code would crash on a plausible real-world input given the described usage context.
