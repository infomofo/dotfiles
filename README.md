# dotfiles

## Setup

Run `git submodule update --init`

Symlink `.vim` to `~/.vim`.

Symlink .jrnl_config to `~/`. Make sure that `~/Journal` is your shared `jrnl`
repository.

Symlink your vimiki folder to `~/vimwiki`

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
