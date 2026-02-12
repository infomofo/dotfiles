# Dotfiles Repository - Agent Instructions

## Repository Overview

Personal dotfiles for vim, tmux, and SSH configuration. Symlinked into `~` for use.

## Structure

```
.vim/vimrc          - Vim configuration
.vim/pack/plugins/start/  - Vim plugins (git submodules)
.vim/bin/           - Utility scripts
.vim/after/         - Vim after-load config (syntax overrides)
.tmux.conf          - Tmux configuration
.ssh/config         - SSH configuration template
```

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
| copilot.vim | GitHub Copilot AI completions |
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
- **.gitignore**: Only `.vim/.netrwhist` is ignored. Keep it minimal.

## Things to Avoid

- Don't add plugin managers (vim-plug, Vundle, etc.) - native vim packages + submodules are used.
- Don't add shell configs (zshrc, bashrc) - those are managed separately.
- Don't modify `.git/config` submodule entries directly; use `git submodule` commands.
- Don't use SSH URLs for submodules.
