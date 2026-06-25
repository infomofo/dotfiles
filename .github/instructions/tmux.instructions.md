---
applyTo: "**/.tmux.conf"
excludeAgent: "cloud-agent"
---

- tmux `#{m:...}` uses fnmatch/glob matching, not regex. In glob patterns, `.` is a literal character — do not suggest escaping it as `\.` or `[.]`.
