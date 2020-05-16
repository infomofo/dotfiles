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
git submodule add https://github.com/vim-airline/vim-airline.git .vim/pack/plugins/start/vim-airline
git add .gitmodules .vim/pack/plugins/start/vim-airline
```

## To update git submodules

```sh
git pull --recurse-submodules
```
