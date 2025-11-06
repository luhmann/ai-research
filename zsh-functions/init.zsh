#!/usr/bin/env zsh
# ==============================================================================
# ZSH Functions Library - Main Initialization Script
# ==============================================================================
#
# This script initializes the ZSH functions library, providing:
# - Organized function management with categories
# - Fuzzy search and discovery via fzf
# - Easy function browsing by description and keywords
#
# Usage:
#   Add to your ~/.zshrc:
#   source /path/to/zsh-functions/init.zsh

# Get the directory where this script is located
ZSH_FUNCTIONS_DIR="${${(%):-%x}:A:h}"

# Add function directories to fpath for autoloading
fpath=(
  "$ZSH_FUNCTIONS_DIR/core"
  "$ZSH_FUNCTIONS_DIR/functions"/*(/N)
  $fpath
)

# Autoload core management functions
autoload -Uz zf-browse zf-add zf-list zf-help zf-search zf-tv-setup

# Autoload all user functions from category directories
local func_file
for func_file in $ZSH_FUNCTIONS_DIR/functions/**/*(.N); do
  autoload -Uz ${func_file:t}
done

# Export environment variables for use by core functions
export ZSH_FUNCTIONS_DIR
export ZSH_FUNCTIONS_CATEGORIES=(git text file docker dev system network)

# Optional: Create convenient aliases
alias zfb='zf-browse'
alias zfa='zf-add'
alias zfl='zf-list'
alias zfh='zf-help'
alias zfs='zf-search'

# Print initialization message
if [[ -n "$ZSH_FUNCTIONS_VERBOSE" ]]; then
  echo "✓ ZSH Functions Library loaded from: $ZSH_FUNCTIONS_DIR"
  echo "  Run 'zf-help' or 'zfh' for usage information"
fi
