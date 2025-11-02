"""
Deep Research Agent - Main Orchestrator

This is the main research agent that coordinates all phases
and provides controllable research workflow.
"""
import asyncio
from typing import Dict, Any, Optional, AsyncIterator
from datetime import datetime
import time

from config import ResearchConfig, ResearchDepth
from state import ResearchState, Phase, PhaseStatus
from phases import PlanningPhase, GatheringPhase, AnalysisPhase, ReportingPhase


class ResearchAgent:
    """
    Main research agent orchestrator

    This agent provides controllable multi-phase research similar to
    ChatGPT Deep Research but with explicit control over each phase.
    """

    def __init__(self, config: Optional[ResearchConfig] = None):
        """
        Initialize the research agent

        Args:
            config: Research configuration (uses default if not provided)
        """
        self.config = config or ResearchConfig()

        # Initialize phases
        self.planning_phase = PlanningPhase(self.config)
        self.gathering_phase = GatheringPhase(self.config)
        self.analysis_phase = AnalysisPhase(self.config)
        self.reporting_phase = ReportingPhase(self.config)

    async def research(
        self,
        query: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Conduct research on a query

        This is the main entry point. Depending on config:
        - auto_advance=True: Runs all phases automatically
        - auto_advance=False: Requires manual phase progression

        Args:
            query: The research query
            session_id: Optional session ID to resume previous research

        Returns:
            Final research results
        """
        # Initialize or load state
        if session_id:
            state = ResearchState.load(session_id)
            print(f"Resuming research session: {session_id}")
        else:
            state = ResearchState(query)
            print(f"Starting new research session: {state.session_id}")

        print(f"\nResearch Configuration:")
        print(f"  Depth: {self.config.depth.value}")
        print(f"  Max Sources: {self.config.max_sources}")
        print(f"  Max Time: {self.config.max_time_minutes} minutes")
        print(f"  Output Format: {self.config.output_format.value}")
        print(f"  Auto-advance: {self.config.auto_advance}")
        print(f"  Interactive: {self.config.interactive}")

        # Execute phases based on configuration
        if self.config.auto_advance:
            # Run all phases automatically
            result = await self._execute_all_phases(state)
        else:
            # Manual phase progression (return for user control)
            print("\nManual mode: Use phase_X methods to progress through research")
            result = {
                "state": state,
                "status": "initialized",
                "next_phase": "planning"
            }

        # Save state
        if self.config.save_intermediate_results:
            filepath = state.save()
            print(f"\nResearch saved to: {filepath}")

        return result

    async def _execute_all_phases(self, state: ResearchState) -> Dict[str, Any]:
        """Execute all phases automatically"""

        results = {}
        total_start = time.time()

        # Phase 1: Planning
        if not state.is_phase_complete(Phase.PLANNING):
            results["planning"] = await self.phase_1_planning(state)

        # Phase 2: Gathering
        if not state.is_phase_complete(Phase.GATHERING):
            results["gathering"] = await self.phase_2_gathering(state)

        # Phase 3: Analysis
        if not state.is_phase_complete(Phase.ANALYSIS):
            results["analysis"] = await self.phase_3_analysis(state)

        # Phase 4: Reporting
        if not state.is_phase_complete(Phase.REPORTING):
            results["reporting"] = await self.phase_4_reporting(state, results["analysis"])

        total_time = time.time() - total_start

        return {
            "session_id": state.session_id,
            "query": state.query,
            "status": "completed",
            "total_time_seconds": total_time,
            "phase_results": results,
            "final_report": state.final_report,
            "progress": state.get_progress()
        }

    async def phase_1_planning(self, state: ResearchState) -> Dict[str, Any]:
        """
        Execute Phase 1: Planning

        Args:
            state: ResearchState object

        Returns:
            Planning phase results
        """
        start_time = time.time()
        state.start_phase(Phase.PLANNING)

        try:
            result = await self.planning_phase.execute(state.query, state)

            # Request approval if needed
            if self.config.require_approval:
                approved = await self.planning_phase.request_user_approval(
                    result["research_plan"]
                )
                result["approved"] = approved

            duration = time.time() - start_time
            state.complete_phase(Phase.PLANNING, result, duration)

            return result

        except Exception as e:
            state.fail_phase(Phase.PLANNING, [str(e)])
            raise

    async def phase_2_gathering(self, state: ResearchState) -> Dict[str, Any]:
        """
        Execute Phase 2: Information Gathering

        Args:
            state: ResearchState object

        Returns:
            Gathering phase results
        """
        if not state.is_phase_complete(Phase.PLANNING):
            raise ValueError("Must complete planning phase first")

        start_time = time.time()
        state.start_phase(Phase.GATHERING)

        try:
            result = await self.gathering_phase.execute(state)

            duration = time.time() - start_time
            state.complete_phase(Phase.GATHERING, result, duration)

            return result

        except Exception as e:
            state.fail_phase(Phase.GATHERING, [str(e)])
            raise

    async def phase_3_analysis(self, state: ResearchState) -> Dict[str, Any]:
        """
        Execute Phase 3: Analysis & Synthesis

        Args:
            state: ResearchState object

        Returns:
            Analysis phase results
        """
        if not state.is_phase_complete(Phase.GATHERING):
            raise ValueError("Must complete gathering phase first")

        start_time = time.time()
        state.start_phase(Phase.ANALYSIS)

        try:
            result = await self.analysis_phase.execute(state)

            duration = time.time() - start_time
            state.complete_phase(Phase.ANALYSIS, result, duration)

            return result

        except Exception as e:
            state.fail_phase(Phase.ANALYSIS, [str(e)])
            raise

    async def phase_4_reporting(
        self, state: ResearchState, analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute Phase 4: Report Generation

        Args:
            state: ResearchState object
            analysis_result: Results from analysis phase

        Returns:
            Reporting phase results
        """
        if not state.is_phase_complete(Phase.ANALYSIS):
            raise ValueError("Must complete analysis phase first")

        start_time = time.time()
        state.start_phase(Phase.REPORTING)

        try:
            result = await self.reporting_phase.execute(state, analysis_result)

            duration = time.time() - start_time
            state.complete_phase(Phase.REPORTING, result, duration)

            return result

        except Exception as e:
            state.fail_phase(Phase.REPORTING, [str(e)])
            raise

    async def research_stream(self, query: str) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream research progress in real-time (interactive mode)

        Args:
            query: The research query

        Yields:
            Progress updates as they happen
        """
        state = ResearchState(query)

        yield {
            "type": "started",
            "session_id": state.session_id,
            "query": query
        }

        # Phase 1
        yield {"type": "phase_started", "phase": "planning"}
        planning_result = await self.phase_1_planning(state)
        yield {"type": "phase_completed", "phase": "planning", "data": planning_result}

        # Phase 2
        yield {"type": "phase_started", "phase": "gathering"}
        gathering_result = await self.phase_2_gathering(state)
        yield {"type": "phase_completed", "phase": "gathering", "data": gathering_result}

        # Phase 3
        yield {"type": "phase_started", "phase": "analysis"}
        analysis_result = await self.phase_3_analysis(state)
        yield {"type": "phase_completed", "phase": "analysis", "data": analysis_result}

        # Phase 4
        yield {"type": "phase_started", "phase": "reporting"}
        reporting_result = await self.phase_4_reporting(state, analysis_result)
        yield {"type": "phase_completed", "phase": "reporting", "data": reporting_result}

        yield {
            "type": "completed",
            "session_id": state.session_id,
            "final_report": state.final_report
        }

    def get_progress(self, session_id: str) -> Dict[str, Any]:
        """
        Get progress for a research session

        Args:
            session_id: Session ID to check

        Returns:
            Progress information
        """
        state = ResearchState.load(session_id)
        return state.get_progress()

    def pause_gathering(self):
        """Pause the gathering phase (if in progress)"""
        self.gathering_phase.pause()

    def resume_gathering(self):
        """Resume the gathering phase"""
        self.gathering_phase.resume()

    def modify_research_plan(self, state: ResearchState, modifications: Dict[str, Any]):
        """
        Modify the research plan

        Args:
            state: ResearchState to modify
            modifications: Dictionary of modifications to apply
        """
        state.research_plan.update(modifications)
        state.add_user_modification("plan_modification", modifications)

    @staticmethod
    def list_sessions() -> list:
        """List all research sessions"""
        return ResearchState.list_sessions()


# Convenience functions for common use cases

async def quick_research(query: str) -> str:
    """
    Quick research (1-3 minutes, summary only)

    Args:
        query: Research query

    Returns:
        Executive summary
    """
    from config import QUICK_RESEARCH

    agent = ResearchAgent(QUICK_RESEARCH)
    result = await agent.research(query)
    return result.get("final_report", "")


async def interactive_research(query: str) -> ResearchState:
    """
    Interactive research with user control

    Args:
        query: Research query

    Returns:
        ResearchState object for manual phase control
    """
    from config import INTERACTIVE_RESEARCH

    agent = ResearchAgent(INTERACTIVE_RESEARCH)
    result = await agent.research(query)
    return result.get("state")


async def deep_research(query: str) -> Dict[str, Any]:
    """
    Deep research (15-30+ minutes, comprehensive)

    Args:
        query: Research query

    Returns:
        Complete research results
    """
    from config import DEEP_RESEARCH

    agent = ResearchAgent(DEEP_RESEARCH)
    return await agent.research(query)
