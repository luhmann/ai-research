# Quick Start Guide

Get up and running with the ZSH Functions Library in 5 minutes!

## Step 1: Install (30 seconds)

Add this line to your `~/.zshrc`:

```zsh
source /path/to/zsh-functions/init.zsh
```

Then reload your shell:

```zsh
source ~/.zshrc
```

## Step 2: Try It Out (2 minutes)

```zsh
# Show all commands
zf-help

# List all available functions
zf-list

# Try an example function
mkcd test-directory
# (creates directory and cds into it)

# Create a backup of a file
echo "test" > test.txt
backup-file test.txt
ls -la test.txt*
```

## Step 3: Discover Functions (1 minute)

```zsh
# Search for git-related functions
zf-search git

# If you have fzf installed:
zf-browse
# (opens interactive fuzzy finder)
```

## Step 4: Add Your Own (2 minutes)

```zsh
# Create a new function
zf-add my-helper dev

# This opens your editor with a template
# Edit it, save, and reload:
source ~/.zshrc

# Now use it:
my-helper
```

## That's It!

You're now ready to organize and discover your zsh functions efficiently.

### Key Commands to Remember

- `zfb` - Browse functions (interactive)
- `zfl` - List all functions
- `zfs keyword` - Search for keyword
- `zfa name category` - Add new function

### Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Browse example functions in `functions/` for inspiration
- Add your frequently-used shell commands as functions
- Share your useful functions with your team

### Optional: Install fzf

For the best experience with `zf-browse`:

```bash
# macOS
brew install fzf

# Ubuntu/Debian
sudo apt install fzf

# Arch Linux
sudo pacman -S fzf
```

---

**Need help?** Run `zf-help` or `zfh` anytime!
