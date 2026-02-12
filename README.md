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

### 2. Create symlinks

```sh
ln -s ~/Code/dotfiles/.vim ~/.vim
ln -s ~/Code/dotfiles/.tmux.conf ~/.tmux.conf
ln -s ~/.vim/vimrc ~/.ideavimrc  # optional, for IntelliJ IDEA
```

### 3. Install prerequisites

- **Node.js 22+** (required by GitHub Copilot)

### 4. Set up GitHub Copilot

Open vim and run:

```
:Copilot setup
```

Follow the prompts to authenticate with your GitHub account. Verify with `:Copilot status`.

If you use a Node.js version manager (nvm, nodenv, etc.), you may need to add this to `.vim/vimrc`:

```vim
let g:copilot_node_command = '/path/to/node'
```

### 5. Set up vimwiki (optional)

vimwiki is configured to use an Obsidian vault at `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/vault/`. Make sure this path exists if you use Obsidian, or update the path in `.vim/vimrc`.

## Requirements

- **Vim 9.0.0185+** (for copilot.vim)
- **Node.js 22+** (for copilot.vim)
- **tmux** (copy-paste works natively on modern macOS, no extra tools needed)

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
