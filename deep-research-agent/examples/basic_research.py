"""
Basic Research Examples

This file demonstrates various ways to use the Deep Research Agent POC.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import ResearchAgent, quick_research, interactive_research, deep_research
from config import ResearchConfig, ResearchDepth, OutputFormat, SourceType


async def example_1_auto_research():
    """
    Example 1: Fully automated research

    This runs all phases automatically without user intervention.
    Good for: Quick research tasks where you trust the agent to work autonomously
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Fully Automated Research")
    print("="*70 + "\n")

    # Create agent with auto-advance enabled
    config = ResearchConfig(
        depth=ResearchDepth.MEDIUM,
        auto_advance=True,
        require_approval=False,
        output_format=OutputFormat.MARKDOWN
    )

    agent = ResearchAgent(config)

    # Run research
    query = "What are the key differences between transformer and recurrent neural networks?"
    result = await agent.research(query)

    print("\nResearch Complete!")
    print(f"Session ID: {result['session_id']}")
    print(f"Total Time: {result['total_time_seconds']:.2f} seconds")
    print(f"\nFinal Report:\n{result['final_report'][:500]}...")


async def example_2_phase_by_phase():
    """
    Example 2: Phase-by-phase control

    This demonstrates manual control over each phase, allowing you to
    review and modify between phases.
    Good for: Research that needs human oversight and iteration
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Phase-by-Phase Control")
    print("="*70 + "\n")

    # Create agent with manual control
    config = ResearchConfig(
        depth=ResearchDepth.MEDIUM,
        auto_advance=False,  # Manual mode
        require_approval=True,
        output_format=OutputFormat.MARKDOWN
    )

    agent = ResearchAgent(config)

    query = "How does quantum computing differ from classical computing?"

    # Initialize research
    from state import ResearchState
    state = ResearchState(query)

    # Phase 1: Planning
    print("--- Executing Phase 1: Planning ---")
    planning_result = await agent.phase_1_planning(state)
    print(f"Research plan created with {len(state.research_questions)} questions")

    # USER COULD REVIEW AND MODIFY PLAN HERE
    # For example:
    # agent.modify_research_plan(state, {"estimated_sources": 50})

    # Phase 2: Gathering
    print("\n--- Executing Phase 2: Gathering ---")
    gathering_result = await agent.phase_2_gathering(state)
    print(f"Gathered {gathering_result['total_sources']} sources")

    # USER COULD REVIEW SOURCES HERE
    # For example:
    # for source in state.sources[:3]:
    #     print(f"  - {source.title}")

    # Phase 3: Analysis
    print("\n--- Executing Phase 3: Analysis ---")
    analysis_result = await agent.phase_3_analysis(state)
    print(f"Generated {len(state.findings)} findings")
    print(f"Overall confidence: {analysis_result['analysis_confidence']:.0%}")

    # USER COULD REQUEST DEEPER ANALYSIS HERE
    # For example:
    # if analysis_result['analysis_confidence'] < 0.7:
    #     # Gather more sources or adjust analysis

    # Phase 4: Reporting
    print("\n--- Executing Phase 4: Reporting ---")
    reporting_result = await agent.phase_4_reporting(state, analysis_result)
    print(f"Report generated: {reporting_result['word_count']} words")

    # Save the session
    filepath = state.save()
    print(f"\nSession saved to: {filepath}")


async def example_3_streaming():
    """
    Example 3: Streaming research with real-time updates

    This demonstrates the streaming API that provides real-time updates
    as research progresses.
    Good for: Building interactive UIs or dashboards
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Streaming Research")
    print("="*70 + "\n")

    config = ResearchConfig(
        depth=ResearchDepth.QUICK,  # Use quick for demo
        auto_advance=True,
        output_format=OutputFormat.SUMMARY
    )

    agent = ResearchAgent(config)

    query = "What are the main use cases for large language models?"

    # Stream research progress
    async for update in agent.research_stream(query):
        update_type = update.get("type")

        if update_type == "started":
            print(f"🚀 Research started: {update['session_id']}")

        elif update_type == "phase_started":
            print(f"\n📍 Phase started: {update['phase']}")

        elif update_type == "phase_completed":
            phase = update['phase']
            print(f"✅ Phase completed: {phase}")

            if phase == "gathering":
                data = update.get('data', {})
                print(f"   Sources gathered: {data.get('total_sources', 0)}")

            elif phase == "analysis":
                data = update.get('data', {})
                print(f"   Confidence: {data.get('analysis_confidence', 0):.0%}")

        elif update_type == "completed":
            print(f"\n🎉 Research completed!")
            print(f"\n{update['final_report']}")


async def example_4_custom_configuration():
    """
    Example 4: Custom configuration

    This shows how to fully customize the research agent for specific needs.
    Good for: Specialized research requirements
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Custom Configuration")
    print("="*70 + "\n")

    # Create highly customized config
    config = ResearchConfig(
        # Research parameters
        depth=ResearchDepth.DEEP,
        max_sources=100,
        max_time_minutes=30,

        # Source configuration
        source_types=[SourceType.WEB, SourceType.ACADEMIC],
        exclude_domains=["example.com", "spam.com"],

        # Output configuration
        output_format=OutputFormat.FULL_DOSSIER,
        include_citations=True,
        include_confidence_scores=True,
        include_contradictions=True,

        # Phase control
        auto_advance=True,
        require_approval=False,

        # Advanced options
        use_subagents=True,
        max_subagents=5,
        enable_fact_checking=True,
        save_intermediate_results=True
    )

    agent = ResearchAgent(config)

    query = "What is the current state of AI safety research?"

    print(f"Starting deep research with custom config...")
    print(f"  Max sources: {config.max_sources}")
    print(f"  Max time: {config.max_time_minutes} minutes")
    print(f"  Output: {config.output_format.value}")

    result = await agent.research(query)

    print(f"\nResearch completed!")
    print(f"Total time: {result['total_time_seconds']:.2f} seconds")


async def example_5_convenience_functions():
    """
    Example 5: Using convenience functions

    The agent provides quick-start functions for common use cases.
    Good for: Quick prototyping and simple use cases
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Convenience Functions")
    print("="*70 + "\n")

    # Quick research - fastest, summary only
    print("--- Quick Research ---")
    summary = await quick_research("What is machine learning?")
    print(f"Summary length: {len(summary)} characters")

    # Deep research - comprehensive
    print("\n--- Deep Research ---")
    result = await deep_research("What are the ethical implications of AI?")
    print(f"Research completed in {result.get('total_time_seconds', 0):.2f}s")


async def example_6_resume_session():
    """
    Example 6: Resume a previous research session

    Shows how to save and resume research sessions.
    Good for: Long-running research or iterative refinement
    """
    print("\n" + "="*70)
    print("EXAMPLE 6: Resume Research Session")
    print("="*70 + "\n")

    # List existing sessions
    sessions = ResearchAgent.list_sessions()
    print(f"Found {len(sessions)} existing sessions:")
    for session in sessions[:3]:
        print(f"  - {session['session_id']}: {session['query'][:50]}...")

    # Resume a session (if any exist)
    if sessions:
        session_id = sessions[0]['session_id']
        print(f"\nResuming session: {session_id}")

        from state import ResearchState
        state = ResearchState.load(session_id)

        print(f"Query: {state.query}")
        print(f"Progress: {state.get_progress()}")

        # Could continue research from where it left off
        # agent = ResearchAgent()
        # result = await agent.research(state.query, session_id=session_id)


async def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("DEEP RESEARCH AGENT - EXAMPLES")
    print("="*70)

    # Run examples
    # await example_1_auto_research()
    await example_2_phase_by_phase()
    # await example_3_streaming()
    # await example_4_custom_configuration()
    # await example_5_convenience_functions()
    # await example_6_resume_session()


if __name__ == "__main__":
    asyncio.run(main())
