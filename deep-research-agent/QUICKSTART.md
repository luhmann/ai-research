# Quick Start Guide

Get started with the Deep Research Agent in 5 minutes!

## Installation

```bash
cd deep-research-agent
pip install -r requirements.txt
```

## Your First Research

### Option 1: Run Example (Easiest)

```bash
python examples/basic_research.py
```

This will run Example 2 (phase-by-phase control) and show you how the agent works.

### Option 2: Python Script

Create a file `my_research.py`:

```python
import asyncio
from agent import ResearchAgent
from config import ResearchConfig, ResearchDepth, OutputFormat

async def main():
    # Configure the agent
    config = ResearchConfig(
        depth=ResearchDepth.QUICK,      # Quick research for testing
        auto_advance=True,               # Run all phases automatically
        output_format=OutputFormat.MARKDOWN
    )

    # Create agent
    agent = ResearchAgent(config)

    # Research!
    result = await agent.research(
        "What is the Claude Agent SDK and how does it work?"
    )

    # Display results
    print("\n" + "="*70)
    print("RESEARCH RESULTS")
    print("="*70 + "\n")
    print(result['final_report'])
    print(f"\n\nCompleted in {result['total_time_seconds']:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
python my_research.py
```

## What You'll See

The agent will:

1. **📋 Plan** - Analyze your query and create a research plan
2. **🔍 Gather** - Search for and collect relevant sources
3. **🧠 Analyze** - Cross-reference sources and extract insights
4. **📝 Report** - Generate a formatted report with citations

## Control Levels

### Level 1: Fully Automatic (Fastest)

```python
from agent import quick_research

summary = await quick_research("Your question here")
print(summary)
```

### Level 2: Configure & Go

```python
from agent import ResearchAgent
from config import DEEP_RESEARCH

agent = ResearchAgent(DEEP_RESEARCH)
result = await agent.research("Your question here")
```

### Level 3: Full Control (Most Flexible)

```python
from agent import ResearchAgent
from state import ResearchState

agent = ResearchAgent()
state = ResearchState("Your question here")

# Run each phase when YOU want
planning = await agent.phase_1_planning(state)
# Review plan, modify if needed
gathering = await agent.phase_2_gathering(state)
# Review sources
analysis = await agent.phase_3_analysis(state)
# Review findings
report = await agent.phase_4_reporting(state, analysis)
```

## Configuration Quick Reference

### Research Depth

```python
from config import ResearchDepth

ResearchDepth.QUICK   # 1-3 min, 10 sources
ResearchDepth.MEDIUM  # 5-10 min, 30 sources
ResearchDepth.DEEP    # 15-30 min, 100 sources
```

### Output Format

```python
from config import OutputFormat

OutputFormat.SUMMARY       # Executive summary only
OutputFormat.MARKDOWN      # Full markdown report
OutputFormat.JSON          # Structured JSON data
OutputFormat.FULL_DOSSIER  # Complete research package
```

### Common Configurations

```python
from config import ResearchConfig, ResearchDepth, OutputFormat

# Quick research for testing
config = ResearchConfig(
    depth=ResearchDepth.QUICK,
    auto_advance=True
)

# Interactive research with control
config = ResearchConfig(
    depth=ResearchDepth.MEDIUM,
    auto_advance=False,
    require_approval=True,
    interactive=True
)

# Deep comprehensive research
config = ResearchConfig(
    depth=ResearchDepth.DEEP,
    output_format=OutputFormat.FULL_DOSSIER,
    include_citations=True,
    include_contradictions=True
)
```

## Viewing Results

### Saved Sessions

Research sessions are automatically saved:

```python
from agent import ResearchAgent

# List all sessions
sessions = ResearchAgent.list_sessions()
for session in sessions:
    print(f"{session['session_id']}: {session['query']}")
    print(f"  Progress: {session['progress_percent']:.0f}%")

# Resume a session
agent = ResearchAgent()
result = await agent.research(
    query="...",
    session_id=sessions[0]['session_id']
)
```

Sessions are saved in `./research_sessions/` as JSON files.

### Progress Tracking

```python
from agent import ResearchAgent

# Check progress of a running session
agent = ResearchAgent()
progress = agent.get_progress(session_id="research_20250102_123456_1234")

print(f"Progress: {progress['progress_percent']:.0f}%")
print(f"Current phase: {progress['current_phase']}")
print(f"Sources gathered: {progress['sources_gathered']}")
```

## Streaming Updates

For real-time updates:

```python
from agent import ResearchAgent

agent = ResearchAgent()

async for update in agent.research_stream("Your question"):
    if update['type'] == 'phase_started':
        print(f"▶ Starting: {update['phase']}")

    elif update['type'] == 'phase_completed':
        print(f"✓ Completed: {update['phase']}")

    elif update['type'] == 'completed':
        print(f"\nFinal Report:\n{update['final_report']}")
```

## Common Use Cases

### Use Case 1: Quick Fact Check

```python
from agent import quick_research

summary = await quick_research("Is climate change real?")
```

### Use Case 2: Compare Options

```python
from agent import ResearchAgent
from config import ResearchConfig, ResearchDepth

config = ResearchConfig(depth=ResearchDepth.MEDIUM)
agent = ResearchAgent(config)

result = await agent.research(
    "Compare Python vs JavaScript for backend development"
)
```

### Use Case 3: Deep Technical Research

```python
from agent import deep_research

result = await deep_research(
    "What are the latest advances in quantum computing error correction?"
)
```

### Use Case 4: Monitored Research

```python
from agent import ResearchAgent
from state import ResearchState

agent = ResearchAgent()
state = ResearchState("Research topic")

# Phase 1
planning = await agent.phase_1_planning(state)
print(f"Will gather {state.research_plan['estimated_sources']} sources")

# Modify plan if needed
if state.research_plan['estimated_sources'] > 50:
    agent.modify_research_plan(state, {"estimated_sources": 30})

# Continue with modified plan
gathering = await agent.phase_2_gathering(state)
```

## Troubleshooting

### Issue: Import errors

**Solution:** Make sure you're in the correct directory:

```bash
cd deep-research-agent
python -c "import agent; print('OK')"
```

### Issue: Research taking too long

**Solution:** Use QUICK depth for testing:

```python
config = ResearchConfig(depth=ResearchDepth.QUICK)
```

### Issue: Want to see what's happening

**Solution:** The agent prints progress by default. For even more detail, use streaming:

```python
async for update in agent.research_stream(query):
    print(update)
```

## Next Steps

1. **Try the examples**: Run `python examples/basic_research.py`
2. **Read the architecture**: See `ARCHITECTURE.md` for design details
3. **Customize**: Modify `config.py` for your needs
4. **Extend**: Add your own tools in `tools/` directory

## Tips

- Start with `ResearchDepth.QUICK` for testing
- Use `auto_advance=True` for simplicity
- Use `auto_advance=False` for control
- Always check `include_citations=True` for credibility
- Save sessions with `save_intermediate_results=True`

## Getting Help

1. Check examples in `examples/basic_research.py`
2. Read the full README in `README.md`
3. Review architecture in `ARCHITECTURE.md`
4. See Claude Agent SDK docs: https://docs.claude.com/en/api/agent-sdk/overview

---

**Ready to research? Start with `python examples/basic_research.py`!** 🚀
