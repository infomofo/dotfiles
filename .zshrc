# History
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000
setopt SHARE_HISTORY          # share history across all tmux panes/tabs
setopt HIST_IGNORE_ALL_DUPS   # deduplicate older entries
setopt HIST_REDUCE_BLANKS     # trim whitespace
setopt APPEND_HISTORY         # append, don't overwrite

# NVM
export NVM_DIR="${XDG_CONFIG_HOME:-$HOME}/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

# mise
command -v mise &>/dev/null && eval "$(mise activate zsh)"
