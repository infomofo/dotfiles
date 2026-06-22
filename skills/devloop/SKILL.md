---
name: devloop
description: >-
  Web dev server workflow for UI/styling/layout work. Use when the user says "devloop" or
  when a plan includes visual verification URLs. Checks for a running dev server, starts one
  if needed, iterates with hot-reload, and cleanly shuts down on approval.
user-invocable: true
---

# DevLoop — Web Dev Server Workflow

For UI/styling/layout work where visual verification matters.

**When to start:** (1) The user says "devloop" or "let's devloop this", OR (2) the approved plan includes a DevLoop/verification section with URLs to check. In case (2), start automatically after implementing — don't wait to be asked. Running tests and builds alone is not sufficient for UI work; the user needs to visually verify in a browser.

## Spin Up

Check the project's dev port for an existing server:
```bash
lsof -i :<port> -t
```
If a server is already running, reuse it. Otherwise start the project's dev command as a background task. Find the right command and port from `package.json`, `README`, or `AGENTS.md` — common examples:
- `npm run dev` / `yarn dev` (port 3000, 5173, etc.)
- `npm run develop` / `yarn develop` (Gatsby, port 8000)
- `npm start` / `yarn start`

## Iterate

Make small, incremental changes. Most dev servers hot-reload for template/style/component changes. Config files (e.g., `gatsby-node.js`, `vite.config.ts`, `.eleventy.js`) typically require a server restart.

Tell the user which URL to check and what changed. Wait for feedback before the next iteration.

## Ship It

When the user approves (e.g. "commit", "ship it", "looks good"):
1. Run the project's test and build commands
2. Stop the dev server: `lsof -i :<port> -t | xargs kill` or stop the background task
3. Commit and push (or create PR if requested)
4. If the user corrected a pattern during the loop, update `AGENTS.md`
