# Television Integration Analysis

This document analyzes integrating [Television](https://github.com/alexpasmantier/television) as an alternative or complement to the current fzf-based implementation.

## What is Television?

Television is a modern, Rust-based fuzzy finder TUI (Terminal User Interface) with a channel-based architecture. Unlike traditional fuzzy finders, it structures data sources as "channels" with built-in preview support.

**Key Features:**
- Fast, asynchronous I/O with multithreading
- Built-in preview system (no external scripts needed)
- Channel-based architecture for different data sources
- Custom "cable channels" via TOML configuration
- Shell integration for context-aware suggestions
- Modern UI with extensive theming and customization

## Custom Channel Configuration

Television allows creating custom channels via TOML files in `~/.config/television/cable/`:

```toml
[metadata]
name = "zsh-functions"
description = "Browse ZSH functions library"
requirements = ["grep", "bat"]

[source]
command = "find $ZSH_FUNCTIONS_DIR/functions -type f -exec sh -c 'name=$(basename {}); desc=$(grep \"^# @description:\" {} | sed \"s/^# @description: *//\"); cat=$(basename $(dirname {})); printf \"%-20s %-12s %s\\n\" \"$name\" \"[$cat]\" \"$desc\"' \\;"

[preview]
command = "bat --color=always --style=numbers --theme=base16 '{}'"
```

## Comparison: Television vs. fzf

### Performance

| Aspect | Television | fzf |
|--------|-----------|-----|
| **Speed** | Very fast (Rust + async I/O) | Very fast (Go) |
| **Memory** | Efficient multithreading | Efficient |
| **Startup** | Slightly slower (Rust binary) | Very fast |
| **Large datasets** | Excellent (async processing) | Excellent |

**Verdict:** Both are excellent performers. Television has modern async architecture, fzf is battle-tested.

### User Experience

| Aspect | Television | fzf |
|--------|-----------|-----|
| **Preview** | Built-in, seamless | Requires configuration |
| **Interface** | Modern, themed | Simple, functional |
| **Customization** | Extensive (colors, layout, keys) | Good (mostly functional) |
| **Learning curve** | Moderate (TOML config) | Low (CLI flags) |
| **Documentation** | Growing | Extensive |

**Verdict:** Television offers more polish out-of-the-box, fzf is simpler and more established.

### Integration Complexity

| Aspect | Television | fzf |
|--------|-----------|-----|
| **Installation** | Cargo or binary download | Package managers everywhere |
| **Configuration** | TOML files in config directory | CLI flags or env vars |
| **Portability** | Requires Rust toolchain or binary | Widely available |
| **Shell integration** | Built-in support | Manual keybindings |
| **Extensibility** | Channel-based (structured) | Pipe-based (flexible) |

**Verdict:** fzf is more portable and easier to install; television offers better structure.

## Advantages of Television Integration

### ✅ Pros

1. **Better Default Preview**
   - Built-in syntax highlighting with bat integration
   - No need for complex preview scripts
   - Smoother preview scrolling and navigation

2. **Structured Channel System**
   - Clean separation of different function categories as channels
   - Each category could be its own channel (git-functions, text-functions, etc.)
   - Metadata-driven configuration

3. **Superior UI/UX**
   - Modern, polished interface
   - Better theming options
   - More intuitive keybindings
   - Status bar, help panel, etc.

4. **Shell Integration**
   - Auto-trigger channels based on shell context
   - Example: typing `git checkout` could auto-open git-functions channel
   - Smart command completion

5. **Future-Proof**
   - Active development
   - Modern codebase (Rust)
   - Growing community

6. **Channel-Based Organization**
   - Natural fit for categorized functions
   - Each category = one channel
   - Easy to browse by domain

### ❌ Cons

1. **Additional Dependency**
   - Requires installing television (not as ubiquitous as fzf)
   - Larger binary size (Rust)
   - May require Cargo for installation on some systems

2. **Smaller User Base**
   - Newer tool (2024), less battle-tested
   - Fewer community resources
   - Potential for breaking changes

3. **Configuration Complexity**
   - TOML configuration files (more to learn)
   - Multiple files for multiple channels
   - More moving parts

4. **Installation Barriers**
   - Not available in all package managers yet
   - Some users may not have Rust toolchain
   - Requires extra setup step

5. **Compatibility Concerns**
   - Requires relatively modern terminal
   - May not work in all environments (older systems)
   - Different keybindings than fzf (muscle memory)

6. **Over-Engineering Risk**
   - May be overkill for simple function browsing
   - Adds complexity for marginal benefit
   - Steeper learning curve for users

## Integration Options

### Option 1: Replace fzf with Television (Full Migration)

**Implementation:**
- Replace `zf-browse` with television-based implementation
- Create cable channels for each function category
- Remove fzf dependency

**Pros:**
- Single, unified interface
- Leverage all television features
- Simpler codebase (no fallback logic)

**Cons:**
- Breaks existing fzf users' workflows
- Higher installation barrier
- Less portable

### Option 2: Dual Support (Both fzf and Television)

**Implementation:**
- Keep existing `zf-browse` (fzf)
- Add new `zf-tv` command for television
- Auto-detect which is available
- Use television if both are installed

**Pros:**
- Best of both worlds
- Users choose their preference
- Gradual migration path
- Maximum compatibility

**Cons:**
- More code to maintain
- Duplicate functionality
- Configuration complexity
- Testing burden

### Option 3: Television as Optional Enhancement

**Implementation:**
- Keep fzf as primary/required tool
- Add optional television integration for advanced users
- Provide setup scripts to generate cable channels
- Documentation for both approaches

**Pros:**
- Low risk (fzf remains default)
- Allows power users to leverage television
- Demonstrates best practices for both tools
- No breaking changes

**Cons:**
- Fragmented user experience
- Maintenance overhead
- Documentation complexity

### Option 4: Television-First, fzf Fallback

**Implementation:**
- Make television the primary interface
- Fall back to fzf if television not installed
- Generate cable channels automatically
- Provide easy television installation guide

**Pros:**
- Encourages modern tooling
- Better UX for new users
- Still works everywhere (via fallback)
- Future-focused

**Cons:**
- Installation friction for new users
- Extra complexity in implementation
- Two codepaths to maintain

## Example Implementation: Television Channel

Here's what a zsh-functions television channel would look like:

**File:** `~/.config/television/cable/zsh-functions-channels.toml`

```toml
# All functions in one channel
[[cable_channel]]
[metadata]
name = "zsh-functions"
description = "Search all ZSH functions by name, category, or description"
requirements = ["bat"]

[source]
command = '''
for func_file in $ZSH_FUNCTIONS_DIR/functions/**/*(.N); do
  func_name="${func_file:t}"
  category="${${func_file:h}:t}"
  description=$(grep "^# @description:" "$func_file" | head -1 | sed 's/^# @description: *//')
  keywords=$(grep "^# @keywords:" "$func_file" | head -1 | sed 's/^# @keywords: *//')
  printf "%s|%s|%s|%s|%s\n" "$func_name" "$category" "$description" "$keywords" "$func_file"
done
'''

[preview]
command = "bat --color=always --style=full --theme=base16 {4}"

# Git functions only
[[cable_channel]]
[metadata]
name = "git-functions"
description = "Browse Git-related ZSH functions"
requirements = ["bat"]

[source]
command = '''
for func_file in $ZSH_FUNCTIONS_DIR/functions/git/*(.N); do
  func_name="${func_file:t}"
  description=$(grep "^# @description:" "$func_file" | head -1 | sed 's/^# @description: *//')
  printf "%-25s %s\n" "$func_name" "$description"
done
'''

[preview]
command = "bat --color=always --style=full {0} 2>/dev/null || bat --color=always $ZSH_FUNCTIONS_DIR/functions/git/{0}"
```

**Usage:**
```bash
# Browse all functions
tv zsh-functions

# Browse only git functions
tv git-functions

# With shell integration, auto-suggest:
# User types: git<space>
# → Television automatically shows git-functions channel
```

## Recommendation

### 🎯 Recommended Approach: **Option 3 - Television as Optional Enhancement**

**Rationale:**

1. **Low Risk, High Value**
   - Keep fzf as the reliable, portable default
   - Television becomes a power-user feature
   - No breaking changes to existing functionality

2. **Progressive Enhancement**
   - Users can try television without commitment
   - Easy to fall back if issues arise
   - Demonstrates both tools' capabilities

3. **Practical Implementation**
   - Add `zf-tv-setup` command to generate cable channels
   - Document both approaches clearly
   - Let users choose based on their needs

4. **Maintenance Balance**
   - Primary code uses fzf (simple, stable)
   - Television integration is declarative (TOML files)
   - Minimal ongoing maintenance burden

### Implementation Steps

1. **Create television channel generator**
   - Add `zf-tv-setup` command
   - Generates cable channel files automatically
   - Checks for television installation

2. **Add documentation**
   - Section in README about television
   - Comparison guide (this document)
   - Installation instructions

3. **Provide example channels**
   - Pre-configured TOML files in `television/` directory
   - One channel per category + all-functions channel
   - Copy script for easy setup

4. **Optional: Add detection**
   - Check if television is installed
   - Show tip about television enhancement
   - Don't force or require it

### Code Example

```bash
# zf-tv-setup command
zf-tv-setup() {
  if ! command -v tv &> /dev/null; then
    echo "Television is not installed."
    echo "Install it with:"
    echo "  cargo install television"
    echo "  # or download from https://github.com/alexpasmantier/television"
    return 1
  fi

  local tv_config="$HOME/.config/television/cable"
  mkdir -p "$tv_config"

  echo "Generating television channels for ZSH functions..."
  # Generate channel files
  # ...

  echo "✓ Television channels created in $tv_config"
  echo ""
  echo "Usage:"
  echo "  tv zsh-functions     - Browse all functions"
  echo "  tv git-functions     - Browse git functions"
  echo "  tv <category>-functions - Browse specific category"
}
```

## Conclusion

Television is an excellent modern fuzzy finder with superior UI/UX and structure. However, for the ZSH Functions Library:

- **fzf should remain the default** (ubiquity, simplicity, stability)
- **Television should be an optional enhancement** (better UX for power users)
- **Provide easy setup** (auto-generate channels, clear docs)
- **Document both approaches** (let users choose)

This approach maximizes accessibility while demonstrating cutting-edge tooling for those who want it.

---

**Next Steps:**

1. Review this analysis
2. Decide on integration approach
3. If approved, implement television support as optional feature
4. Test and document both workflows
