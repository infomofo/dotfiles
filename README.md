# dotfiles

## Setup

Run `git submodule update --init`

Symlink `.vim` to `~/.vim` with `ln -s .vim ~/.vim`

Symlink `.tmux.conf` to `~/.tmux.conf` with `ln -s .tmux.conf ~/.tmux.conf`. To get copy-paste working from vim within tmux make sure you also `brew install reattach-to-user-namespace`.

Symlink your vimiki folder to `~/vimwiki` or Sync it from resilio sync

## Link vimrc to .ideavimrc

```sh
ln -s ~/.vim/vimrc ~/.ideavimrc
```

## To add new git modules

```sh
cd ~/Code/dotfiles
git submodule add --depth 1 -- https://github.com/vim-airline/vim-airline.git .vim/pack/plugins/start/vim-airline
git add .gitmodules .vim/pack/plugins/start/vim-airline
```

## To remove a gitmodule

1. Delete the relevant section from the .gitmodules file
2. `git add .gitmodules`
3. Delete the relevant section from .git/config
4. Run `git rm --cached <path_to_submodule>` (no trailing slash
4. Run `rm -rf .git/modules/<path_to_submodule>` (no trailing slash
5. Commit `git commit -m "Removed submodule"
6. Delete the now untacked submodule files `rm -rf <path to submodule>`

## To update git submodules

```sh
git pull --recurse-submodules
```
