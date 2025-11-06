# Television Integration for ZSH Functions Library

This directory contains [Television](https://github.com/alexpasmantier/television) integration for the ZSH Functions Library.

## What is Television?

Television is a modern, fast fuzzy finder built in Rust with:
- Beautiful TUI with built-in preview
- Channel-based architecture for different data sources
- Extensive customization and theming
- Smart shell integration

## Why Television?

While the library includes **fzf-based browsing** (which works great!), Television offers:

- 🎨 **Superior UI** - Modern interface with better theming
- 👀 **Built-in Preview** - Seamless syntax highlighting (no scripts needed)
- 📺 **Channel System** - Browse by category with dedicated channels
- 🔧 **Shell Integration** - Context-aware suggestions
- ⚡ **Performance** - Async I/O and multithreading

## Installation

### Quick Setup

```bash
# 1. Install television
cargo install television
# or download from: https://github.com/alexpasmantier/television/releases

# 2. Run the setup command
zf-tv-setup
```

That's it! The setup command will:
- Check if television is installed
- Create the cable configuration directory
- Install ZSH function channels
- Verify your environment

### Manual Setup

If you prefer manual installation:

```bash
# 1. Install television (see above)

# 2. Create television config directory
mkdir -p ~/.config/television/cable

# 3. Copy the channel configuration
cp zsh-functions-channels.toml ~/.config/television/cable/

# 4. Ensure ZSH_FUNCTIONS_DIR is set (should be automatic if you sourced init.zsh)
echo $ZSH_FUNCTIONS_DIR
```

## Usage

### Browse Functions by Channel

```bash
# All functions across all categories
tv zsh-functions

# Git functions only
tv git-functions

# Text processing functions
tv text-functions

# File operation functions
tv file-functions

# Development tools
tv dev-functions

# Recently modified functions
tv recent-functions
```

### Comparison with fzf Browser

Both tools work great! Choose based on your needs:

| Feature | `zf-browse` (fzf) | `tv zsh-functions` |
|---------|-------------------|---------------------|
| **Installation** | Easy (widely available) | Requires extra step |
| **Preview** | Good (configured) | Excellent (built-in) |
| **Interface** | Simple, functional | Modern, polished |
| **Speed** | Very fast | Very fast |
| **Portability** | Excellent | Good |
| **Categories** | Filtered view | Dedicated channels |
| **Customization** | Good | Extensive |

**Recommendation:**
- Use `zf-browse` for simplicity and portability
- Use `tv zsh-functions` for the best UX and features

## Available Channels

### `zsh-functions`
Browse **all functions** across all categories with full metadata.

**Output format:**
```
function-name    [category]  Description here             | keywords | /path/to/file
```

**Preview:** Full function source with syntax highlighting

---

### `git-functions`
Browse **Git and version control** helper functions.

**Examples:**
- `git-quick-commit` - Quick staging and committing
- `git-branch-clean` - Clean up merged branches

---

### `text-functions`
Browse **text processing** utilities.

**Examples:**
- `extract-emails` - Extract emails from text
- `count-lines` - Count lines with statistics

---

### `file-functions`
Browse **file operations** and management tools.

**Examples:**
- `mkcd` - Create directory and cd into it
- `backup-file` - Create timestamped backups

---

### `dev-functions`
Browse **development tools** and utilities.

**Examples:**
- `port-check` - Check if port is in use
- `json-pretty` - Pretty-print JSON

---

### `recent-functions`
Browse **recently modified** functions (useful when developing new functions).

## Customization

### Edit Channel Configuration

```bash
# Open the channel config in your editor
$EDITOR ~/.config/television/cable/zsh-functions-channels.toml
```

You can customize:
- Source command formatting
- Preview command and styling
- Metadata and descriptions
- Add new channels for custom categories

### Add Shell Integration

Television supports context-aware channel triggering. Add to your `~/.config/television/config.toml`:

```toml
[remote_control]
[remote_control.channel_triggers]
# Auto-open git-functions when typing git commands
"git checkout" = ["git-functions"]
"git branch" = ["git-functions"]

# Auto-open file-functions for file operations
"cd" = ["file-functions"]
```

### Theming

Television supports extensive theming. See [Television documentation](https://alexpasmantier.github.io/television/docs/) for details.

## Troubleshooting

### "tv: command not found"

Install television:
```bash
cargo install television
# or download binary from GitHub releases
```

### "ZSH_FUNCTIONS_DIR not set"

Make sure you've sourced the ZSH Functions Library init script:
```bash
source /path/to/zsh-functions/init.zsh
```

### Channels not appearing

Re-run the setup:
```bash
zf-tv-setup --force
```

### Preview not showing / no syntax highlighting

Install `bat` for better previews:
```bash
brew install bat  # macOS
apt install bat   # Ubuntu/Debian
```

## Updating

When the ZSH Functions Library updates channel configurations:

```bash
# Re-run setup to update (will prompt before overwriting)
zf-tv-setup

# Force update without prompting
zf-tv-setup --force
```

## Learn More

- **Television Project:** https://github.com/alexpasmantier/television
- **Television Docs:** https://alexpasmantier.github.io/television/docs/
- **Cable Channels Guide:** https://github.com/alexpasmantier/television/wiki/Cable-channels
- **Integration Analysis:** See `TELEVISION_INTEGRATION.md` in the library root

## Feedback

Television integration is optional and complementary to the fzf-based browser. Both tools are excellent - use whichever fits your workflow better!

If you have suggestions for improving the television integration, please open an issue or submit a PR.

---

**Happy function browsing! 📺✨**
