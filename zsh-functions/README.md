# ZSH Functions Library

A modern, organized system for managing and discovering zsh shell functions with fuzzy search, categorization, and keyword-based discovery.

## 🎯 Features

- **📁 Organized by Category** - Functions grouped into logical categories (git, file, text, dev, etc.)
- **🔍 Fuzzy Search** - Interactive fzf-powered browser to find functions by name, description, or keywords
- **🏷️ Metadata System** - Rich function metadata including descriptions, keywords, usage examples
- **⚡ Auto-loading** - Efficient lazy-loading using zsh's native autoload mechanism
- **🛠️ Easy Management** - Simple commands to add, list, search, and browse functions
- **📝 Template-based** - Consistent function format with scaffolding tool

## 🚀 Quick Start

### Installation

1. **Clone or download this repository**

2. **Add to your `~/.zshrc`:**
   ```zsh
   source /path/to/zsh-functions/init.zsh
   ```

3. **Reload your shell:**
   ```zsh
   source ~/.zshrc
   ```

4. **Optional: Install fzf for interactive browsing**
   ```bash
   # macOS
   brew install fzf

   # Ubuntu/Debian
   apt install fzf

   # Or see: https://github.com/junegunn/fzf#installation
   ```

### First Steps

```zsh
# Show help
zf-help

# List all available functions
zf-list

# Browse functions interactively (requires fzf)
zf-browse

# Search for functions containing "git"
zf-search git
```

## 📚 Core Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `zf-browse [query]` | `zfb` | Interactive fuzzy search with fzf |
| `zf-list [category]` | `zfl` | List all functions or filter by category |
| `zf-search <keyword>` | `zfs` | Search functions by keyword (grep-based) |
| `zf-add <name> <cat>` | `zfa` | Create a new function from template |
| `zf-help` | `zfh` | Show detailed help information |

## 🎨 Usage Examples

### Browse Functions Interactively

```zsh
# Open interactive browser
zf-browse

# Pre-filter by search term
zf-browse commit
zfb git
```

The interactive browser shows:
- Function names and categories
- Descriptions and metadata
- Live preview of function source code
- Fuzzy matching on all text

### List Functions

```zsh
# List all functions grouped by category
zf-list

# List only git-related functions
zf-list git

# List text processing functions
zfl text
```

### Search Functions

```zsh
# Search for functions related to "commit"
zf-search commit

# Search for "backup" functions
zfs backup

# Search for "json" utilities
zf-search json
```

### Create New Functions

```zsh
# Create a new git helper function
zf-add my-git-helper git

# Create a text processing function
zfa process-log text

# Create a function in a new category
zf-add deploy-prod deployment
```

## 📂 Directory Structure

```
zsh-functions/
├── README.md              # This file
├── init.zsh               # Main initialization script
├── core/                  # Core management functions
│   ├── zf-browse          # Interactive fzf browser
│   ├── zf-list            # List functions
│   ├── zf-search          # Keyword search
│   ├── zf-add             # Create new functions
│   └── zf-help            # Help system
├── functions/             # User functions organized by category
│   ├── git/              # Git and VCS helpers
│   │   ├── git-quick-commit
│   │   └── git-branch-clean
│   ├── text/             # Text processing
│   │   ├── extract-emails
│   │   └── count-lines
│   ├── file/             # File operations
│   │   ├── mkcd
│   │   └── backup-file
│   ├── dev/              # Development tools
│   │   ├── port-check
│   │   └── json-pretty
│   ├── docker/           # Container tools
│   ├── system/           # System administration
│   └── network/          # Network utilities
└── templates/            # (Future: function templates)
```

## 🏷️ Function Format

Each function file follows a standard format with metadata:

```zsh
#!/usr/bin/env zsh
# @name: function_name
# @description: Brief description of what this function does
# @category: category_name
# @keywords: keyword1, keyword2, keyword3
# @usage: function_name [arguments]
# @example: function_name arg1 arg2

function_name() {
  # Implementation here
}

# Execute if run directly
if [[ "${(%):-%x}" == "${0}" ]]; then
  function_name "$@"
fi
```

### Metadata Fields

- **@name** - Function name (should match filename)
- **@description** - Brief description for search and discovery
- **@category** - Category for organization (git, file, text, etc.)
- **@keywords** - Comma-separated keywords for searchability
- **@usage** - Usage syntax
- **@example** - Example invocation

## 🎓 Included Example Functions

### Git Functions

- **git-quick-commit** - Stage all changes and commit with a message
- **git-branch-clean** - Delete local branches merged to main/master

### Text Functions

- **extract-emails** - Extract email addresses from text or files
- **count-lines** - Count lines in files with statistics

### File Functions

- **mkcd** - Create a directory and cd into it
- **backup-file** - Create timestamped backup copies

### Dev Functions

- **port-check** - Check if a port is in use
- **json-pretty** - Pretty-print JSON with jq or python

## 🔧 Customization

### Add Custom Categories

Simply create functions in new category directories:

```zsh
zf-add my-function new-category
```

The system will automatically create the category and include it in searches.

### Verbose Loading

Show initialization message on shell startup:

```zsh
export ZSH_FUNCTIONS_VERBOSE=1
source /path/to/zsh-functions/init.zsh
```

### Custom Aliases

The init script creates default aliases, but you can add your own:

```zsh
alias zff='zf-search'  # Custom search alias
alias zfg='zf-list git'  # Quick git function list
```

## 🐛 Troubleshooting

### Functions not found after adding new ones

Reload your shell or manually autoload:

```zsh
source ~/.zshrc
# or
autoload -Uz function_name
```

### fzf not working

Install fzf using your package manager:
```zsh
brew install fzf  # macOS
apt install fzf   # Linux
```

Or use the grep-based search instead:
```zsh
zf-search keyword
```

### Function not appearing in browser

Ensure the function file:
1. Has the correct metadata headers (@name, @description, etc.)
2. Is in a category directory under `functions/`
3. Is executable: `chmod +x functions/category/function-name`

## 💡 Best Practices

1. **Use descriptive names** - Make function names clear and intuitive
2. **Add rich metadata** - Good descriptions and keywords improve discoverability
3. **Include examples** - Show how to use the function in the @example field
4. **One function per file** - Keep functions focused and modular
5. **Test before committing** - Verify functions work as expected
6. **Document edge cases** - Add comments for complex logic

## 🤝 Contributing

To add your own functions:

1. Use `zf-add` to create a new function from template
2. Edit the function to implement your logic
3. Update the metadata (description, keywords, etc.)
4. Test the function
5. Done! It's automatically available after reload

## 📖 Additional Resources

- [ZSH Functions Documentation](https://zsh.sourceforge.io/Doc/Release/Functions.html)
- [fzf GitHub Repository](https://github.com/junegunn/fzf)
- [Mastering ZSH](https://github.com/rothgar/mastering-zsh)

## 📄 License

This library structure is provided as-is for personal and educational use. Individual functions may have their own licenses.

---

**Made with ❤️ for productive shell users**

Run `zf-help` or `zfh` for quick reference anytime!
