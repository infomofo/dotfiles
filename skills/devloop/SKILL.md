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

Check for an existing server first. **Two steps — both required:**

```bash
# 1. Find the correct port from vite.config.js / next.config.js / package.json / README
#    Never use a port from memory or prior instructions without verifying against the config.

# 2. Find the PID of any process listening on that port
lsof -i :<port> -sTCP:LISTEN -t
```

If something is already on the port, confirm it is the project's dev server (not an unrelated process). `lsof` can return multiple PIDs — check each one. Use `-ww` to prevent truncation of long commands:
```bash
ps -ww -p <pid> -o command=
```

If it is the correct server, reuse it. Otherwise, **always start with `detach: true`** so the server survives across tool calls, test runs, and session activity:

```bash
# Command to pass to the bash tool with mode: "async", detach: true
<dev-command> > /tmp/<project>-dev.log 2>&1
```

Use `mode: "async"` with `detach: true` in the tool invocation (not in the bash command itself). Log output to `/tmp/<project>-dev.log` so you can inspect it later.

Find the right command from `package.json`, `README`, or `AGENTS.md`. Find the port from `package.json`, `vite.config.js`, `next.config.js`, or `README` — not from `AGENTS.md` (it may be stale). Common examples:
- `npm run dev` / `yarn dev` (port 3000, 5173, etc.)
- `npm run develop` / `yarn develop` (Gatsby, port 8000)
- `npm start` / `yarn start`
- `yarn serve` / `npm run serve` (Vue CLI, port 8080)

After starting, wait ~20s then verify with:
```bash
lsof -i :<port> -sTCP:LISTEN -t && echo "running" || echo "dead"
```

## Keep the Server Alive

**Before telling the user to verify**, always confirm the server is still up:
```bash
lsof -i :<port> -sTCP:LISTEN -t && echo "running" || echo "dead"
```

**Common things that kill the server:**
- Running `yarn test` / `npm test` / any sync build command in the same session — these can reclaim async shell resources
- Installing packages (`yarn add`, `npm install`) — can disrupt the process
- The shell session timing out or being stopped via `stop_bash`
- Non-detached async processes are killed when the session ends

**If the server died**, check the log before restarting:
```bash
tail -30 /tmp/<project>-dev.log
```
Then restart with `detach: true` again.

## Iterate

Make small, incremental changes. Most dev servers hot-reload for template/style/component changes. Config files (e.g., `gatsby-node.js`, `vite.config.ts`, `.eleventy.js`, `vue.config.js`) typically require a server restart.

After each change:
1. Confirm server is up (`lsof -i :<port> -sTCP:LISTEN -t`)
2. Tell the user the URL and exactly what changed
3. Wait for feedback before the next iteration

## Ship It

When the user approves (e.g. "commit", "ship it", "looks good"):
1. Run the project's test and build commands
2. Stop the dev server — verify the PID is the dev server before killing:
   ```bash
   lsof -i :<port> -sTCP:LISTEN -t | xargs -I{} ps -ww -p {} -o command=
   # Confirm it's your dev server, then:
   lsof -i :<port> -sTCP:LISTEN -t | xargs kill
   ```
3. Commit and push (or create PR if requested)
4. If the user corrected a pattern during the loop, update `AGENTS.md`
