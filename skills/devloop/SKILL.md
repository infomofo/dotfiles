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

Check for an existing server first:
```bash
lsof -i :<port> -t
```
If running, reuse it. Otherwise, **always start with `detach: true`** so the server survives across tool calls, test runs, and session activity:

```bash
# Start detached, log to a temp file for debugging
<dev-command> > /tmp/dev-server.log 2>&1
```

Use `mode: "async"` with `detach: true`. Log output to `/tmp/<project>-dev.log` so you can inspect it later.

Find the right command and port from `package.json`, `README`, or `AGENTS.md` — common examples:
- `npm run dev` / `yarn dev` (port 3000, 5173, etc.)
- `npm run develop` / `yarn develop` (Gatsby, port 8000)
- `npm start` / `yarn start`
- `yarn serve` / `npm run serve` (Vue CLI, port 8080)

After starting, wait ~20s then verify with:
```bash
lsof -i :<port> -t && echo "running" || echo "dead"
```

## Keep the Server Alive

**Before telling the user to verify**, always confirm the server is still up:
```bash
lsof -i :<port> -t && echo "running" || echo "dead"
```

**Common things that kill the server:**
- Running `yarn test` / `npm test` / any sync build command in the same session — these can reclaim async shell resources
- Installing packages (`yarn add`, `npm install`) — can disrupt the process
- The shell session timing out or being stopped via `stop_bash`
- Non-detached async processes are killed when the session ends

**If the server died**, check the log before restarting:
```bash
cat /tmp/<project>-dev.log | tail -30
```
Then restart with `detach: true` again.

## Iterate

Make small, incremental changes. Most dev servers hot-reload for template/style/component changes. Config files (e.g., `gatsby-node.js`, `vite.config.ts`, `.eleventy.js`, `vue.config.js`) typically require a server restart.

After each change:
1. Confirm server is up (`lsof -i :<port> -t`)
2. Tell the user the URL and exactly what changed
3. Wait for feedback before the next iteration

## Ship It

When the user approves (e.g. "commit", "ship it", "looks good"):
1. Run the project's test and build commands
2. Stop the dev server: `lsof -i :<port> -t | xargs kill`
3. Commit and push (or create PR if requested)
4. If the user corrected a pattern during the loop, update `AGENTS.md`
