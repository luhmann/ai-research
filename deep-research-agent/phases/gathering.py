"""
Phase 2: Information Gathering
"""
import asyncio
from typing import Dict, Any, List
from datetime import datetime
import time


class GatheringPhase:
    """
    Phase 2: Information Gathering

    This phase:
    1. Executes web searches for each research question
    2. Collects information from multiple sources
    3. Tracks progress in real-time
    4. Allows user to pause/resume
    """

    def __init__(self, config):
        self.config = config
        self.paused = False

    async def execute(self, state) -> Dict[str, Any]:
        """
        Execute the information gathering phase

        Args:
            state: ResearchState object with research plan

        Returns:
            Dictionary containing gathered information
        """
        print(f"\n{'='*60}")
        print(f"PHASE 2: INFORMATION GATHERING")
        print(f"{'='*60}\n")

        research_plan = state.research_plan
        research_questions = state.research_questions

        print(f"Questions to research: {len(research_questions)}")
        print(f"Target sources: {research_plan['estimated_sources']}")
        print(f"Search strategy: {research_plan['search_strategy']}\n")

        # Track progress
        gathered_sources = []
        search_results = {}

        # Process each research question
        for i, question in enumerate(research_questions, 1):
            print(f"\nResearching Question {i}/{len(research_questions)}:")
            print(f"  {question.question}")

            # Search for this question
            sources = await self._search_question(question, research_plan)

            # Store results
            question.status = "researched"
            question.sources = sources
            gathered_sources.extend(sources)
            search_results[question.question] = sources

            # Add to state
            for source in sources:
                state.add_source(source)

            # Show progress
            print(f"  Found: {len(sources)} sources")
            self._show_progress(i, len(research_questions), len(gathered_sources))

            # Check if we should pause (in interactive mode)
            if self.config.interactive and self.paused:
                print("\n[Paused - waiting for user to continue]")
                # In real implementation, wait for user input
                await asyncio.sleep(0.1)

            # Small delay between questions to avoid rate limiting
            await asyncio.sleep(0.5)

        # Summary
        print(f"\n{'─'*60}")
        print(f"GATHERING COMPLETE")
        print(f"{'─'*60}")
        print(f"Total sources gathered: {len(gathered_sources)}")
        print(f"Questions researched: {len(research_questions)}")
        print(f"{'─'*60}\n")

        return {
            "total_sources": len(gathered_sources),
            "sources_by_question": search_results,
            "questions_researched": len(research_questions),
            "gathered_sources": gathered_sources
        }

    async def _search_question(self, question, research_plan: Dict[str, Any]) -> List:
        """
        Search for information related to a specific research question

        Args:
            question: ResearchQuestion object
            research_plan: The research plan

        Returns:
            List of Source objects
        """
        from state import Source
        from tools.web_search import create_web_search_tool

        max_sources = research_plan['search_strategy']['max_sources_per_question']

        # Create web search tool
        search_tool = create_web_search_tool()
        search_fn = search_tool["function"]

        # Perform search
        try:
            result = await search_fn({
                "query": question.question,
                "max_results": max_sources
            })

            # Extract sources from results
            sources = []
            if "metadata" in result and "results" in result["metadata"]:
                for r in result["metadata"]["results"]:
                    source = Source(
                        url=r["url"],
                        title=r["title"],
                        snippet=r["snippet"],
                        timestamp=r["timestamp"],
                        reliability_score=r.get("relevance_score", 0.5),
                        source_type=result["metadata"].get("source_type", "web")
                    )
                    sources.append(source)

            return sources

        except Exception as e:
            print(f"  Error searching: {e}")
            return []

    def _show_progress(self, current: int, total: int, sources_count: int):
        """Display progress bar and statistics"""
        progress = current / total
        bar_length = 40
        filled = int(bar_length * progress)
        bar = '█' * filled + '░' * (bar_length - filled)

        print(f"\n  Progress: [{bar}] {current}/{total} ({progress*100:.1f}%)")
        print(f"  Sources collected: {sources_count}")

    async def search_parallel(self, questions: List, max_parallel: int = 3) -> Dict[str, List]:
        """
        Search multiple questions in parallel using subagents

        Args:
            questions: List of research questions
            max_parallel: Maximum number of parallel searches

        Returns:
            Dictionary mapping questions to their sources
        """
        print(f"\n  Using parallel search with {max_parallel} workers...")

        results = {}

        # Split questions into batches
        for i in range(0, len(questions), max_parallel):
            batch = questions[i:i + max_parallel]

            # Search batch in parallel
            tasks = [
                self._search_question(q, {"search_strategy": {"max_sources_per_question": 10}})
                for q in batch
            ]

            batch_results = await asyncio.gather(*tasks)

            # Store results
            for question, sources in zip(batch, batch_results):
                results[question.question] = sources

        return results

    def pause(self):
        """Pause the gathering process"""
        self.paused = True
        print("\n[Gathering paused]")

    def resume(self):
        """Resume the gathering process"""
        self.paused = False
        print("\n[Gathering resumed]")

    def adjust_depth(self, new_max_sources: int):
        """
        Adjust the search depth mid-gathering

        Args:
            new_max_sources: New maximum sources to gather
        """
        print(f"\n[Adjusting search depth to {new_max_sources} sources]")
        # In real implementation, update the research plan
