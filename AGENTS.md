# Dotfiles Repository - Agent Instructions

## Repository Overview

Personal dotfiles for vim, tmux, and SSH configuration. Symlinked into `~` for use.

## Structure

```
.zprofile                 - Zsh login shell config (PATH, env vars, sources ~/.secrets)
.zshrc                    - Zsh interactive shell config (NVM init)
.vim/vimrc                - Vim configuration
.vim/pack/plugins/start/  - Vim plugins (git submodules)
.vim/bin/                 - Utility scripts
.vim/after/               - Vim after-load config (syntax overrides)
.tmux.conf                - Tmux configuration
.ssh/config               - SSH configuration template
claude/settings.json      - Claude Code global settings (hooks for tmux integration)
claude/CLAUDE.md          - Claude Code global instructions (behavior preferences)
.claude/settings.local.json - Claude Code project-level permissions (this repo only)
skills/                   - Shared agent skills (symlinked from ~/.copilot/skills and ~/.claude/skills)
setup.sh                  - Symlinks dotfiles into $HOME and hydrates ~/.secrets from Keychain
```

### Claude Code file layout

Files in `claude/` (no dot) are **global** config — symlinked into `~/.claude/` on each machine. Files in `.claude/` (with dot) are **project-level** settings scoped to this repo.

`settings.json`, `CLAUDE.md`, and `skills/` are shared. Machine-local files like `settings.local.json`, `history.jsonl`, caches, and session state stay in `~/.claude/` untracked.

### Syncing Claude and Copilot instructions

`claude/CLAUDE.md` and `copilot/copilot-instructions.md` share most of their content. Claude is used for work (teamwork, GCP projects), Copilot is used for personal projects.

When asked to sync changes between these files:

- **Do sync:** Integrity rules, Code practices, Git rules, PR rules, CI rules, Communication, GitHub Identity, Writing in the User's Voice, and formatting conventions (line wrapping, whitespace).
- **Do not sync:** Sections specific to teamwork or work infrastructure. These exist only in the Claude file and should stay that way:
  - Branch names convention (`$USER/<short-description>`)
  - Collaboration section
  - GCP Authentication section
  - Tooling section (Copilot has `Search from the repo root` under Code instead)
  - Jira (acli) section

### Skills

Shared agent skills live in `skills/`. Each skill is a subdirectory with a `SKILL.md` file containing YAML frontmatter and instructions. `setup.sh` symlinks `skills/` into both `~/.copilot/skills` and `~/.claude/skills` so they are available to both GitHub Copilot CLI and Claude Code on every machine.

To add a skill: create `skills/<name>/SKILL.md` and commit it.

## Vim Plugin Management

All vim plugins live in `.vim/pack/plugins/start/` and **must** be managed as git submodules.

### Adding a plugin

```sh
git submodule add --depth 1 -- <https-url> .vim/pack/plugins/start/<plugin-name>
git add .gitmodules .vim/pack/plugins/start/<plugin-name>
```

- Always use `--depth 1` to keep the clone shallow.
- Always use HTTPS URLs (not SSH) for submodule URLs so anyone can clone.
- Never clone a plugin directly into the directory; it must be a submodule.

### Removing a plugin

1. Delete the relevant section from `.gitmodules`
2. `git add .gitmodules`
3. Delete the relevant section from `.git/config`
4. `git rm --cached .vim/pack/plugins/start/<plugin-name>`
5. `rm -rf .git/modules/.vim/pack/plugins/start/<plugin-name>`
6. Commit the removal
7. `rm -rf .vim/pack/plugins/start/<plugin-name>`

### Updating plugins

```sh
git pull --recurse-submodules
```

## Current Plugins

| Plugin | Purpose |
|--------|---------|
| editorconfig-vim | EditorConfig support |
| vim-emoji-ab | Emoji abbreviations in markdown/mail |
| vim-polyglot | Syntax highlighting for 100+ languages |
| vim-prettier | Prettier code formatting |
| vimwiki | Wiki/notes integration (synced with Obsidian) |

## Conventions

- **No file bloat**: Don't create unnecessary files. This is a minimal dotfiles repo.
- **Symlinks**: Config files are symlinked from this repo into `~`. Don't assume they're at `~` directly.
- **vimrc style**: Settings use inline comments for explanation. Keep it flat and simple - no plugin managers, no complex abstractions.
- **tmux**: Uses vi keybindings and integrates with macOS clipboard natively (pbcopy/pbpaste). No extra tools needed on modern macOS.
- **Claude Code**: Global config lives in `claude/` (not `.claude/`). Only share files that are portable across machines — no auth tokens, local permissions, or runtime state.

## Things to Avoid

- Don't add plugin managers (vim-plug, Vundle, etc.) - native vim packages + submodules are used.
- Shell config (`.zprofile`, `.zshrc`) lives in this repo. Secrets go in `~/.secrets` (not tracked).
- Don't modify `.git/config` submodule entries directly; use `git submodule` commands.
- Don't use SSH URLs for submodules.
