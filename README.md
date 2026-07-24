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
Seed each secret before running the setup script. The secret names are
defined in the `secrets` array in `setup.sh`.

```sh
security add-generic-password -s "<SECRET_NAME>" -a "$USER" -w "<value>" -U
```

The login keychain does not sync via iCloud, so secrets must be added per machine.

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
> `~/.copilot/skills` and `~/.claude/skills` are the exception: both are symlinked to
> `skills/` in this repo so shared skills are available on every machine.

The setup script also symlinks `tuicr.config.toml` to `~/.config/tuicr/config.toml`.

### 5. Install prerequisites

- **Node.js 22+** (required by GitHub Copilot)

### 6. Set up vimwiki (optional)

vimwiki is configured to use an Obsidian vault at `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/vault/`. Make sure this path exists if you use Obsidian, or update the path in `.vim/vimrc`.

## Requirements

- **tmux** (copy-paste works natively on modern macOS, no extra tools needed)
- **Claude Code** (optional — `settings.json` hooks integrate with tmux for window naming)

## Copilot CLI / Claude Code Skills

Shared skills live in `skills/`. Each skill is a directory containing a `SKILL.md` with YAML frontmatter (`name`, `description`) and instructions for the agent.

`~/.copilot/skills` and `~/.claude/skills` are both symlinked to `skills/` by `setup.sh`, so all skills are available in every project automatically for both tools.

### Installing a skill without cloning this repo

Pick the destination that matches your tool (`~/.claude/skills` for Claude Code, `~/.copilot/skills` for GitHub Copilot CLI).

**Option 1 — curl (individual files)**

Each skill is a directory. Use the GitHub API to download each file:

```sh
SKILL=review-pr-comments
DEST=~/.claude/skills/$SKILL
mkdir -p "$DEST"

# List files in the skill directory, then download each one
curl -fsSL "https://api.github.com/repos/infomofo/dotfiles/contents/skills/$SKILL" \
  | python3 -c "import sys,json; [print(f['download_url']) for f in json.load(sys.stdin) if f.get('download_url')]" \
  | while read url; do
      filename=$(basename "$url")
      curl -fsSL "$url" -o "$DEST/$filename"
    done
```

Replace `SKILL=review-pr-comments` with any skill name from the table below. If you don't have Python 3, use the sparse clone method instead.

**Option 2 — sparse clone**

```sh
SKILL=review-pr-comments
git clone --depth 1 --filter=blob:none --sparse https://github.com/infomofo/dotfiles.git /tmp/dotfiles-skills
git -C /tmp/dotfiles-skills sparse-checkout set "skills/$SKILL"
cp -r "/tmp/dotfiles-skills/skills/$SKILL" ~/.claude/skills/
rm -rf /tmp/dotfiles-skills
```

Replace `SKILL=review-pr-comments` with any skill name from the table below.

### To add a new skill

```sh
mkdir skills/<skill-name>
# create skills/<skill-name>/SKILL.md with frontmatter and instructions
git add skills/<skill-name>
```

### Current skills

| Skill | Description |
|-------|-------------|
| `devloop` | Web dev server workflow for visual/UI verification |
| `review-pr-comments` | Reviews and acts on automated PR review comments |

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
