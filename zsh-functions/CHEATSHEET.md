# ZSH Functions Library - Quick Reference

One-page cheatsheet for daily use.

---

## 🚀 Core Commands

| Command | Alias | What it does |
|---------|-------|--------------|
| `zf-help` | `zfh` | Show help |
| `zf-list` | `zfl` | List all functions |
| `zf-list git` | `zfl git` | List git functions only |
| `zf-browse` | `zfb` | Interactive search (fzf) |
| `zf-browse git` | `zfb git` | Search starting with "git" |
| `zf-search commit` | `zfs commit` | Find functions with "commit" |
| `zf-add myhelper git` | `zfa myhelper git` | Create new function |
| `zf-tv-setup` | - | Setup Television integration |

---

## 🔍 Discovery Methods

### 1. Interactive Fuzzy Search (Recommended)
```bash
zf-browse              # Browse all, type to filter
zfb docker            # Pre-filter by "docker"
```
**Best for:** Exploring, visual browsing

### 2. List by Category
```bash
zf-list               # All functions
zfl git               # Git functions only
zfl text              # Text functions only
```
**Best for:** Seeing what's in each category

### 3. Keyword Search
```bash
zf-search backup      # Find "backup" anywhere
zfs port              # Find "port" functions
```
**Best for:** Finding specific keywords

### 4. Television (Optional)
```bash
tv zsh-functions      # All functions
tv git-functions      # Git only
tv dev-functions      # Dev tools only
```
**Best for:** Premium UX, category browsing

---

## 📝 Creating Functions

### Quick Creation
```bash
zf-add my-function category-name
# Opens editor with template
# Edit, save, reload shell
```

### Function Template
```zsh
#!/usr/bin/env zsh
# @name: function-name
# @description: What it does
# @category: category-name
# @keywords: keyword1, keyword2
# @usage: function-name [args]
# @example: function-name arg1

function-name() {
  # Your code here
}
```

### Categories
- `git` - Git/VCS helpers
- `text` - Text processing
- `file` - File operations
- `dev` - Development tools
- `docker` - Container tools
- `system` - System admin
- `network` - Network utilities
- *or create your own!*

---

## 🎯 Common Workflows

### "I need to do X but forgot the function..."
```bash
zf-browse              # Visual search
zfs <keyword>          # Quick keyword search
```

### "What functions do I have?"
```bash
zfl                    # List all
zfl git                # List by category
```

### "I want to create a helper for..."
```bash
zfa my-helper category
# Edit in $EDITOR
source ~/.zshrc        # Reload
my-helper             # Use it!
```

### "I want the premium experience"
```bash
cargo install television  # Install TV
zf-tv-setup              # Setup integration
tv zsh-functions         # Beautiful browsing
```

---

## 📦 Included Example Functions

### Git Functions
```bash
git-quick-commit "message"   # Stage all & commit
git-branch-clean            # Delete merged branches
```

### Text Functions
```bash
extract-emails file.txt     # Extract all emails
count-lines *.txt          # Count with stats
```

### File Functions
```bash
mkcd new-directory         # Make dir & cd into it
backup-file config.json    # Timestamped backup
```

### Dev Functions
```bash
port-check 3000            # Check if port in use
json-pretty data.json      # Pretty-print JSON
```

---

## ⚙️ Configuration

### Installation
```bash
# Add to ~/.zshrc:
source /path/to/zsh-functions/init.zsh

# Reload:
source ~/.zshrc
```

### Verbose Mode
```bash
# Add before sourcing init.zsh:
export ZSH_FUNCTIONS_VERBOSE=1
```

### Dependencies
- **Required:** zsh (duh!)
- **Optional:** fzf (for zf-browse)
- **Optional:** television (for tv channels)
- **Optional:** bat (for better previews)

---

## 🐛 Troubleshooting

### "Function not found after creating"
```bash
source ~/.zshrc        # Reload shell
# or
autoload -Uz function-name
```

### "zf-browse doesn't work"
```bash
# Install fzf:
brew install fzf      # macOS
apt install fzf       # Linux

# or use grep-based search:
zf-search keyword
```

### "Functions not showing up"
```bash
echo $ZSH_FUNCTIONS_DIR   # Should be set
ls $ZSH_FUNCTIONS_DIR     # Should exist
zfl                       # Try listing
```

### "Television channels not working"
```bash
zf-tv-setup              # Re-run setup
echo $ZSH_FUNCTIONS_DIR  # Verify env var
```

---

## 💡 Pro Tips

### Tip 1: Use Aliases
```bash
zfb                    # Instead of zf-browse
zfl git                # Instead of zf-list git
zfs commit             # Instead of zf-search commit
```

### Tip 2: Pre-filter Searches
```bash
zfb git                # Start with "git" filter
zfb docker            # Start with "docker" filter
```

### Tip 3: Chain Functions
```bash
mkcd my-project && git init
backup-file .env && vim .env
```

### Tip 4: Favorite Categories
```bash
# Create quick aliases for categories you use:
alias zfg='zfl git'
alias zfd='zfl dev'
```

### Tip 5: Quick Edit in Browse
```bash
# In zf-browse, select function and note the path
# Then:
vim /path/shown/in/preview
```

---

## 🎨 fzf vs Television

### Use fzf (`zf-browse`) when:
- ✅ You want simplicity
- ✅ You're on any system
- ✅ You prefer lightweight tools
- ✅ You don't want extra dependencies

### Use Television (`tv`) when:
- ✅ You want beautiful UI
- ✅ You have it installed
- ✅ You browse by category often
- ✅ You appreciate polish

**Both are great! Use what fits your style.**

---

## 📚 Documentation

### Quick Start
- `QUICKSTART.md` - 5-minute guide

### Detailed
- `README.md` - Full documentation
- `zf-help` - Built-in help

### Advanced
- `TELEVISION_INTEGRATION.md` - TV vs fzf analysis
- `television/README.md` - TV setup guide
- `ENHANCEMENTS.md` - Future features

### Reference
- `CHEATSHEET.md` - This file!
- `PROJECT_SUMMARY.md` - Complete overview

---

## 🎯 Quick Decision Tree

```
Need to find a function?
├─ Know rough name/keyword?
│  ├─ Yes → zf-search <keyword>
│  └─ No → zf-browse (visual search)
│
Need to see what's available?
├─ Want specific category?
│  ├─ Yes → zf-list <category>
│  └─ No → zf-list (all functions)
│
Want to create new function?
└─ zf-add <name> <category>

Want better UX?
└─ Install television → zf-tv-setup → tv zsh-functions
```

---

## 🔗 Quick Links

- **GitHub:** [Television](https://github.com/alexpasmantier/television)
- **fzf:** [junegunn/fzf](https://github.com/junegunn/fzf)
- **bat:** [sharkdp/bat](https://github.com/sharkdp/bat)

---

## 🎓 Learning Path

### Day 1
1. Install library
2. Run `zf-list` to see functions
3. Try an example function
4. Run `zf-browse` to explore

### Week 1
1. Create your first function with `zf-add`
2. Try different search methods
3. Organize by categories
4. Read function metadata

### Month 1
1. Build your personal function library
2. Try television integration
3. Customize for your workflow
4. Share with team

---

## ⌨️ Keyboard Shortcuts

### In fzf (zf-browse):
- `↑↓` - Navigate
- `Enter` - Select
- `Esc` - Exit
- `Ctrl+C` - Cancel
- Type to filter

### In Television (tv):
- `↑↓` - Navigate
- `Enter` - Select
- `Esc` - Exit
- `PageUp/PageDown` - Scroll preview
- Type to filter

---

## 🏆 Best Practices

1. **Use descriptive names** - `git-quick-commit` not `gqc`
2. **Add good metadata** - Rich descriptions and keywords
3. **Include examples** - Show how to use in @example
4. **One function per file** - Keep focused
5. **Test before saving** - Make sure it works
6. **Document edge cases** - Add comments for tricky parts
7. **Use categories** - Organize logically
8. **Keep it simple** - Functions should do one thing well

---

## 💬 Getting Help

```bash
zf-help                # Built-in help
zfh                    # Same, shorter

# Browse all functions to learn:
zf-browse

# Read a function to understand:
cat $ZSH_FUNCTIONS_DIR/functions/git/git-quick-commit
```

---

**Print this cheatsheet or keep it handy for quick reference! 📋**

**Happy function browsing! 🚀**
