# Deep Research Agent POC

A controllable research agent built with the **Claude Agent SDK** that provides explicit control over research phases, inspired by ChatGPT Deep Research but with better user control and transparency.

## Overview

This Proof of Concept (POC) demonstrates how to build a research agent that:

- ✅ Breaks research into **4 controllable phases**
- ✅ Allows **user intervention** between any phase
- ✅ Provides **real-time transparency** into the research process
- ✅ Supports **customizable depth** (quick, medium, deep)
- ✅ Enables **pause/resume** functionality
- ✅ Offers **multiple output formats** (Markdown, JSON, etc.)
- ✅ Tracks **citations** and **source reliability**
- ✅ Identifies **contradictions** in sources

## Key Advantages Over ChatGPT Deep Research

| Feature | ChatGPT Deep Research | This POC |
|---------|----------------------|----------|
| **Control** | Autonomous (5-30 min, no control) | Phase-by-phase user control |
| **Intervention** | Only at start | Between any phase |
| **Transparency** | Summary after completion | Real-time progress updates |
| **Customization** | Limited | Depth, sources, output format |
| **State** | No persistence | Save/resume research sessions |
| **Flexibility** | Fixed workflow | Skip/repeat/modify phases |

## Architecture

### Four-Phase Research Loop

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: PLANNING & CLARIFICATION                          │
│  • Analyze query                                             │
│  • Generate research questions                              │
│  • Create research plan                                     │
│  → User can approve/modify plan                             │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: INFORMATION GATHERING                             │
│  • Execute web searches                                      │
│  • Collect sources                                           │
│  • Track progress                                            │
│  → User can pause/adjust depth                              │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: ANALYSIS & SYNTHESIS                              │
│  • Cross-reference sources                                   │
│  • Identify contradictions                                   │
│  • Extract insights                                          │
│  → User can review findings                                 │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: REPORT GENERATION                                 │
│  • Structure findings                                        │
│  • Add citations                                             │
│  • Format output                                             │
│  → User controls format/sections                            │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Setup

```bash
# Clone or download this POC
cd deep-research-agent

# Install dependencies
pip install -r requirements.txt

# (Optional) Set up Anthropic API key for production use
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Quick Start

### 1. Fully Automated Research

Run all phases automatically:

```python
import asyncio
from agent import ResearchAgent
from config import ResearchConfig, ResearchDepth

async def main():
    config = ResearchConfig(
        depth=ResearchDepth.MEDIUM,
        auto_advance=True,
        output_format=OutputFormat.MARKDOWN
    )

    agent = ResearchAgent(config)
    result = await agent.research(
        "What are the key differences between transformers and RNNs?"
    )

    print(result['final_report'])

asyncio.run(main())
```

### 2. Phase-by-Phase Control

Control each phase manually:

```python
import asyncio
from agent import ResearchAgent
from state import ResearchState

async def main():
    agent = ResearchAgent()
    state = ResearchState("How does quantum computing work?")

    # Phase 1: Planning
    planning = await agent.phase_1_planning(state)
    # Review and modify plan here...

    # Phase 2: Gathering
    gathering = await agent.phase_2_gathering(state)
    # Review sources here...

    # Phase 3: Analysis
    analysis = await agent.phase_3_analysis(state)
    # Review findings here...

    # Phase 4: Reporting
    report = await agent.phase_4_reporting(state, analysis)

    print(state.final_report)

asyncio.run(main())
```

### 3. Streaming Updates

Get real-time updates as research progresses:

```python
import asyncio
from agent import ResearchAgent

async def main():
    agent = ResearchAgent()

    async for update in agent.research_stream("What is machine learning?"):
        if update['type'] == 'phase_started':
            print(f"Starting phase: {update['phase']}")
        elif update['type'] == 'phase_completed':
            print(f"Completed phase: {update['phase']}")
        elif update['type'] == 'completed':
            print(f"Final report:\n{update['final_report']}")

asyncio.run(main())
```

## Configuration Options

### Research Depth

```python
from config import ResearchDepth

# Quick research (1-3 min, 5-10 sources)
depth=ResearchDepth.QUICK

# Medium research (5-10 min, 20-30 sources)
depth=ResearchDepth.MEDIUM

# Deep research (15-30+ min, 50+ sources)
depth=ResearchDepth.DEEP
```

### Output Formats

```python
from config import OutputFormat

# Markdown report (default)
output_format=OutputFormat.MARKDOWN

# Structured JSON
output_format=OutputFormat.JSON

# Executive summary only
output_format=OutputFormat.SUMMARY

# Complete research dossier
output_format=OutputFormat.FULL_DOSSIER
```

### Full Configuration

```python
from config import ResearchConfig, ResearchDepth, OutputFormat, SourceType

config = ResearchConfig(
    # Research parameters
    depth=ResearchDepth.DEEP,
    max_sources=100,
    max_time_minutes=30,

    # Source configuration
    source_types=[SourceType.WEB, SourceType.ACADEMIC],
    exclude_domains=["spam.com"],

    # Output configuration
    output_format=OutputFormat.FULL_DOSSIER,
    include_citations=True,
    include_contradictions=True,

    # Phase control
    auto_advance=False,
    require_approval=True,
    interactive=True,

    # Advanced options
    use_subagents=True,
    max_subagents=5,
    save_intermediate_results=True
)
```

## Usage Examples

See `examples/basic_research.py` for comprehensive examples including:

1. Fully automated research
2. Phase-by-phase control
3. Streaming updates
4. Custom configuration
5. Convenience functions
6. Resume saved sessions

Run examples:

```bash
python examples/basic_research.py
```

## Project Structure

```
deep-research-agent/
├── agent.py              # Main ResearchAgent orchestrator
├── config.py             # Configuration options
├── state.py              # State management & persistence
├── phases/
│   ├── planning.py       # Phase 1: Query planning
│   ├── gathering.py      # Phase 2: Information gathering
│   ├── analysis.py       # Phase 3: Analysis & synthesis
│   └── reporting.py      # Phase 4: Report generation
├── tools/
│   ├── web_search.py     # Web search tool
│   ├── document.py       # Document processing
│   └── citation.py       # Citation management
├── examples/
│   └── basic_research.py # Usage examples
├── README.md             # This file
├── ARCHITECTURE.md       # Detailed architecture documentation
└── requirements.txt      # Python dependencies
```

## Key Features

### 1. Phase Control

Unlike ChatGPT Deep Research which runs autonomously, this POC gives you control:

- **Review** the research plan before gathering starts
- **Pause** gathering to add specific sources
- **Review** findings before generating the report
- **Modify** output format or sections

### 2. State Persistence

Research sessions are automatically saved:

```python
# List all sessions
sessions = ResearchAgent.list_sessions()

# Resume a session
agent = ResearchAgent()
result = await agent.research(query, session_id="research_20250102_123456_1234")

# Check progress
progress = agent.get_progress(session_id)
```

### 3. Real-Time Transparency

See exactly what's happening:

- Progress bars during gathering
- Source counts and quality metrics
- Confidence scores for findings
- Contradictions and limitations

### 4. Flexible Output

Choose your output format:

- **Markdown**: Full report with formatting
- **JSON**: Structured data for programmatic use
- **Summary**: Executive summary only
- **Dossier**: Complete research package with appendices

## Claude Agent SDK Integration

This POC is built on the Claude Agent SDK and demonstrates:

- **Agent Loop**: Gather context → Take action → Verify → Repeat
- **Custom Tools**: Web search, document processing, citations
- **Hooks**: Phase transition validation
- **Compaction**: Context management for long research
- **Subagents**: Parallel research workers

### Key SDK Patterns Used

```python
# Query function for one-shot tasks
from claude_agent_sdk import query

async for message in query(prompt="Research question"):
    print(message)

# ClaudeSDKClient for interactive sessions
from claude_agent_sdk import ClaudeSDKClient

client = ClaudeSDKClient(tools=[web_search_tool])
response = await client.chat("Continue research...")

# Custom tools via MCP
from claude_agent_sdk import tool

@tool("search", "Search the web", {"query": str})
async def search(args):
    return {"content": [...]}
```

## Production Enhancements

This is a POC. For production use, consider:

1. **Actual Search APIs**: Integrate with Google, Bing, or specialized APIs
2. **Real NLP**: Use Claude or other LLMs for analysis instead of heuristics
3. **Caching**: Cache search results to avoid duplicate queries
4. **Rate Limiting**: Implement proper rate limiting for APIs
5. **Error Handling**: More robust error handling and retries
6. **Monitoring**: Add metrics and logging
7. **UI**: Build a web interface for better user experience
8. **Collaboration**: Multi-user research sessions
9. **Fact Checking**: Integrate with fact-checking databases
10. **Source Quality**: Advanced source reliability scoring

## Comparison: ChatGPT Deep Research vs This POC

### ChatGPT Deep Research

**Pros:**
- Fully autonomous
- Uses o3 model for reasoning
- Very comprehensive (can take 30+ minutes)

**Cons:**
- No control once started
- Black box during execution
- Can't pause or modify mid-research
- Limited customization
- No state persistence
- Can't iterate on results

### This POC

**Pros:**
- Complete phase control
- Real-time transparency
- Pause/resume/modify anytime
- Fully customizable
- State persistence
- Iterative refinement
- Open source and extensible

**Cons:**
- Requires more user involvement
- Less automated than Deep Research
- POC status (not production-ready)

## License

This is a Proof of Concept for educational purposes. Use and modify as needed for your research applications.

## Contributing

This is a POC, but improvements are welcome! Areas for enhancement:

- Integration with real search APIs
- Better NLP and analysis using Claude
- Web UI for interactive research
- Advanced visualization (knowledge graphs)
- Multi-agent collaboration
- Real-time fact-checking

## Resources

- [Claude Agent SDK Documentation](https://docs.claude.com/en/api/agent-sdk/overview)
- [Building Agents with Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)
- [ChatGPT Deep Research](https://openai.com/index/introducing-deep-research/)

## Support

For questions or issues:
1. Check the `ARCHITECTURE.md` for detailed design documentation
2. Review examples in `examples/basic_research.py`
3. See the [Claude Agent SDK docs](https://docs.claude.com/en/api/agent-sdk/overview)

---

**Built with Claude Agent SDK** | **Inspired by ChatGPT Deep Research** | **Enhanced with User Control**
