# dotfiles

## Setup

### 1. Clone and initialize submodules

```sh
git clone --recurse-submodules git@github.com:infomofo/dotfiles.git ~/Code/dotfiles
```

Or if already cloned:

```sh
git submodule update --init --recursive
```

### 2. Seed Keychain secrets

The shell config sources `~/.secrets`, which is generated from macOS Keychain during setup.
Seed each secret before running the setup script:

```sh
security add-generic-password -s "FOODIMADE_CF_API_TOKEN" -a "$USER" -w "your-token" -U
security add-generic-password -s "OPENAI_API_KEY" -a "$USER" -w "your-key" -U
```

The login keychain does not sync via iCloud — secrets must be added per machine.

### 3. Set up Google service account key

The shell config expects a Google service account key at `~/.config/foodimade-sa-key.json`.
Download the key from the
[GCP Console](https://console.cloud.google.com/iam-admin/serviceaccounts) (project: foodimade)
and copy it into place:

```sh
mkdir -p ~/.config
cp /path/to/downloaded-key.json ~/.config/foodimade-sa-key.json
chmod 600 ~/.config/foodimade-sa-key.json
```

### 4. Run setup script

```sh
bash ~/Code/dotfiles/setup.sh
```

This symlinks all dotfiles into `$HOME` (backing up any existing files) and hydrates
`~/.secrets` from Keychain.

> **Note:** Only specific Claude Code and Copilot CLI files are symlinked — not the whole
> `~/.claude/` or `~/.copilot/` directories. Both tools store machine-local runtime data
> (history, caches, session state, auth tokens) that should not be shared.

### 5. Install prerequisites

- **Node.js 22+** (required by GitHub Copilot)

### 6. Set up vimwiki (optional)

vimwiki is configured to use an Obsidian vault at `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/vault/`. Make sure this path exists if you use Obsidian, or update the path in `.vim/vimrc`.

## Requirements

- **tmux** (copy-paste works natively on modern macOS, no extra tools needed)
- **Claude Code** (optional — `settings.json` hooks integrate with tmux for window naming)

## To add new vim plugins

```sh
cd ~/Code/dotfiles
git submodule add --depth 1 -- https://github.com/vim-airline/vim-airline.git .vim/pack/plugins/start/vim-airline
git add .gitmodules .vim/pack/plugins/start/vim-airline
```

## To remove a vim plugin

1. Delete the relevant section from `.gitmodules`
2. `git add .gitmodules`
3. Delete the relevant section from `.git/config`
4. `git rm --cached .vim/pack/plugins/start/<plugin-name>`
5. `rm -rf .git/modules/.vim/pack/plugins/start/<plugin-name>`
6. Commit the removal
7. `rm -rf .vim/pack/plugins/start/<plugin-name>`

## To update vim plugins

```sh
git pull --recurse-submodules
```
