# Homebrew
eval "$(/opt/homebrew/bin/brew shellenv)"

# PATH
export PATH="$HOME/.local/bin:$PATH"

# SSH agent
eval "$(ssh-agent -s)" > /dev/null 2>&1
ssh-add --apple-use-keychain ~/.ssh/id_ed25519 2>/dev/null

# Project config (non-secret)
export FOODIMADE_GOOGLE_SA_KEY="$HOME/.config/foodimade-sa-key.json"
export FOODIMADE_GA4_PROPERTY_ID='400002279'

# Secrets — hydrated into ~/.secrets during initial setup
# shellcheck source=/dev/null
[[ -f "$HOME/.secrets" ]] && source "$HOME/.secrets"
