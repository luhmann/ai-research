# Deep Research Agent Architecture

## Overview
A controllable research agent built on Claude Agent SDK that provides explicit control over research phases, unlike ChatGPT Deep Research which operates autonomously for 5-30 minutes.

## Key Differentiators from ChatGPT Deep Research

| Feature | ChatGPT Deep Research | Our POC |
|---------|----------------------|---------|
| **Control** | Autonomous, runs 5-30 min | Phase-by-phase user control |
| **Phases** | Need alignment → execution (black box) | 4 explicit, controllable phases |
| **Intervention** | Only at start | Between any phase |
| **Customization** | Limited | Research depth, sources, output format |
| **State** | No persistence | Save/resume research sessions |
| **Transparency** | Post-research summary | Real-time progress per phase |

## Architecture: Four-Phase Research Loop

### Phase 1: Query Planning & Clarification
**Purpose**: Understand and structure the research query
- Parse user's research question
- Generate clarifying questions
- Break down into sub-questions
- Create research plan with:
  - Research questions to answer
  - Potential sources to explore
  - Success criteria
- **User Control**: Approve, modify, or restart planning

### Phase 2: Information Gathering
**Purpose**: Collect relevant information from multiple sources
- Execute web searches based on research plan
- Use parallel subagents for different research angles
- Extract and store relevant information
- Track sources and citations
- **User Control**:
  - Pause/resume gathering
  - Add specific sources to explore
  - Adjust search depth
  - Real-time progress monitoring

### Phase 3: Analysis & Synthesis
**Purpose**: Process and connect the gathered information
- Cross-reference multiple sources
- Identify contradictions and reconcile
- Extract key themes and patterns
- Generate insights
- Build knowledge graph of connections
- **User Control**:
  - Review intermediate findings
  - Request deeper analysis on specific topics
  - Add new research questions based on findings

### Phase 4: Report Generation
**Purpose**: Create structured output from research
- Organize findings into coherent structure
- Add citations for all claims
- Format according to user preferences
- Generate executive summary
- **User Control**:
  - Choose output format (markdown, JSON, structured)
  - Specify report sections
  - Adjust detail level
  - Regenerate with different focus

## Technical Implementation

### Core Components

```
deep-research-agent/
├── agent.py              # Main ResearchAgent orchestrator
├── phases/
│   ├── __init__.py
│   ├── planning.py       # Phase 1: Query planning
│   ├── gathering.py      # Phase 2: Information gathering
│   ├── analysis.py       # Phase 3: Analysis & synthesis
│   └── reporting.py      # Phase 4: Report generation
├── tools/
│   ├── __init__.py
│   ├── web_search.py     # Web search tool
│   ├── document.py       # Document processing
│   └── citation.py       # Citation management
├── state.py              # State management & persistence
├── config.py             # Configuration options
└── examples/
    └── basic_research.py # Example usage
```

### Claude Agent SDK Integration

**Agent Loop Pattern**:
1. **Gather Context**: Each phase gathers relevant context
2. **Take Action**: Execute phase-specific tasks with tools
3. **Verify Work**: Validate phase outputs
4. **Repeat**: User decides to continue or adjust

**Key SDK Features Used**:
- `query()` for one-shot research tasks
- `ClaudeSDKClient` for multi-phase interactive sessions
- Custom tools via in-process MCP servers
- Hooks for phase transition validation
- Context compaction for long research sessions

## Configuration Options

### Research Depth
- **Quick** (1-3 min): 5-10 sources, basic analysis
- **Medium** (5-10 min): 20-30 sources, moderate analysis
- **Deep** (15-30 min): 50+ sources, comprehensive analysis

### Output Formats
- Markdown report with citations
- JSON structured data
- Executive summary only
- Full research dossier

### Source Types
- Web search (default)
- Academic papers
- News articles
- Documentation sites
- Custom source lists

## State Management

Research sessions are saved with:
- Phase completion status
- Gathered information
- Intermediate analysis
- User modifications
- Timestamp tracking

This allows:
- Resume interrupted research
- Iterate on previous research
- Branch research directions
- Compare different approaches

## Usage Patterns

### Pattern 1: Fully Automated
Run all phases sequentially with default settings
```python
agent = ResearchAgent()
result = await agent.research("topic", auto_advance=True)
```

### Pattern 2: Phase-by-Phase Control
Review and approve each phase
```python
agent = ResearchAgent()
plan = await agent.phase_1_planning("topic")
# User reviews plan
gathered = await agent.phase_2_gathering(plan)
# User checks progress
analysis = await agent.phase_3_analysis(gathered)
# User reviews findings
report = await agent.phase_4_reporting(analysis)
```

### Pattern 3: Interactive Mode
Real-time interaction during research
```python
agent = ResearchAgent(interactive=True)
async for update in agent.research_stream("topic"):
    print(update.phase, update.status, update.data)
    if update.requires_input:
        response = input(update.prompt)
        await agent.provide_input(response)
```

## Advantages Over ChatGPT Deep Research

1. **Transparency**: See exactly what's happening at each step
2. **Control**: Intervene and adjust at any point
3. **Flexibility**: Customize depth, sources, and output
4. **Reproducibility**: Save and replay research sessions
5. **Extensibility**: Add custom tools and sources via MCP
6. **Cost Efficiency**: Stop research when you have enough information

## Future Enhancements

- Multi-agent collaboration for parallel research
- Visual research graph/mind map
- Automated fact-checking with source reliability scoring
- Integration with document databases (PDFs, papers)
- Research session sharing and collaboration
- API for programmatic research
