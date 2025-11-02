"""
Phase 1: Query Planning & Clarification
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime


class PlanningPhase:
    """
    Phase 1: Query Planning & Clarification

    This phase:
    1. Analyzes the research query
    2. Generates clarifying questions
    3. Breaks down into sub-questions
    4. Creates a research plan
    """

    def __init__(self, config):
        self.config = config

    async def execute(self, query: str, state) -> Dict[str, Any]:
        """
        Execute the planning phase

        Args:
            query: The research query
            state: ResearchState object

        Returns:
            Dictionary containing the research plan
        """
        print(f"\n{'='*60}")
        print(f"PHASE 1: QUERY PLANNING & CLARIFICATION")
        print(f"{'='*60}\n")
        print(f"Query: {query}\n")

        # Step 1: Analyze the query
        print("Step 1/4: Analyzing query...")
        query_analysis = await self._analyze_query(query)

        # Step 2: Generate clarifying questions (if interactive)
        print("Step 2/4: Generating clarifying questions...")
        clarifying_questions = await self._generate_clarifying_questions(query, query_analysis)

        # Handle interactive mode
        if self.config.interactive and clarifying_questions:
            print("\nClarifying questions:")
            for i, q in enumerate(clarifying_questions, 1):
                print(f"  {i}. {q}")
            print("\n(In interactive mode, you would answer these questions)")
            # In real implementation, wait for user input here

        # Step 3: Break down into research questions
        print("Step 3/4: Breaking down into research questions...")
        research_questions = await self._generate_research_questions(query, query_analysis)

        # Step 4: Create research plan
        print("Step 4/4: Creating research plan...")
        research_plan = await self._create_research_plan(
            query, query_analysis, research_questions
        )

        # Display the plan
        self._display_plan(research_plan)

        # Store in state
        state.research_plan = research_plan
        state.research_questions = research_questions

        return {
            "query": query,
            "query_analysis": query_analysis,
            "clarifying_questions": clarifying_questions,
            "research_questions": research_questions,
            "research_plan": research_plan
        }

    async def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze the research query to understand intent and scope"""

        # In production, use Claude to analyze the query
        # For now, simple heuristic analysis

        words = query.lower().split()

        query_type = "general"
        if any(w in words for w in ["how", "why", "what", "when", "where", "who"]):
            query_type = "question"
        elif any(w in words for w in ["compare", "contrast", "versus", "vs"]):
            query_type = "comparison"
        elif any(w in words for w in ["explain", "describe", "analyze"]):
            query_type = "explanation"
        elif any(w in words for w in ["trend", "history", "evolution"]):
            query_type = "temporal"

        # Estimate complexity
        complexity = "medium"
        if len(words) > 15 or "comprehensive" in words or "detailed" in words:
            complexity = "high"
        elif len(words) < 5:
            complexity = "low"

        # Extract key topics (simplified)
        key_topics = [w for w in words if len(w) > 4 and w.isalpha()][:5]

        return {
            "query_type": query_type,
            "complexity": complexity,
            "estimated_sources_needed": self.config.max_sources,
            "estimated_time_minutes": self.config.max_time_minutes,
            "key_topics": key_topics,
            "scope": "broad" if len(key_topics) > 3 else "focused"
        }

    async def _generate_clarifying_questions(
        self, query: str, analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate questions to clarify the research intent"""

        questions = []

        # Generate based on query type and complexity
        if analysis["scope"] == "broad":
            questions.append(
                "Would you like me to focus on specific aspects of this topic, "
                "or provide a comprehensive overview?"
            )

        if analysis["query_type"] == "comparison":
            questions.append(
                "What criteria are most important for the comparison?"
            )

        if analysis["complexity"] == "high":
            questions.append(
                "Are there specific sub-topics you'd like me to prioritize?"
            )

        # Default questions
        if not questions:
            questions.extend([
                "What level of detail do you need? (overview vs. in-depth)",
                "Are there specific sources or perspectives you want included?"
            ])

        return questions[:3]  # Max 3 questions

    async def _generate_research_questions(
        self, query: str, analysis: Dict[str, Any]
    ) -> List:
        """Break down the main query into specific research questions"""
        from state import ResearchQuestion

        # In production, use Claude to generate relevant questions
        # For now, generate based on query analysis

        questions = []

        # Generate based on query type
        if analysis["query_type"] == "question":
            # Main question
            questions.append(ResearchQuestion(
                question=query,
                priority=5
            ))

            # Supporting questions
            questions.append(ResearchQuestion(
                question=f"What is the background/context for: {query}",
                priority=4
            ))

            questions.append(ResearchQuestion(
                question=f"What are expert opinions on: {query}",
                priority=3
            ))

        elif analysis["query_type"] == "comparison":
            questions.append(ResearchQuestion(
                question=f"What are the key characteristics to compare for: {query}",
                priority=5
            ))

            questions.append(ResearchQuestion(
                question=f"What are the advantages and disadvantages in: {query}",
                priority=4
            ))

        else:
            # General research questions
            for topic in analysis["key_topics"][:3]:
                questions.append(ResearchQuestion(
                    question=f"What is important to know about {topic} in the context of: {query}",
                    priority=3
                ))

        return questions

    async def _create_research_plan(
        self, query: str, analysis: Dict[str, Any],
        research_questions: List
    ) -> Dict[str, Any]:
        """Create a detailed research plan"""

        plan = {
            "objective": query,
            "research_type": analysis["query_type"],
            "scope": analysis["scope"],
            "estimated_duration_minutes": analysis["estimated_time_minutes"],
            "estimated_sources": analysis["estimated_sources_needed"],

            "phases": [
                {
                    "phase": "gathering",
                    "tasks": [
                        f"Search for information on: {q.question}"
                        for q in research_questions[:3]
                    ],
                    "estimated_minutes": int(analysis["estimated_time_minutes"] * 0.4)
                },
                {
                    "phase": "analysis",
                    "tasks": [
                        "Cross-reference sources for consistency",
                        "Identify key themes and patterns",
                        "Note contradictions or disagreements",
                        "Extract actionable insights"
                    ],
                    "estimated_minutes": int(analysis["estimated_time_minutes"] * 0.3)
                },
                {
                    "phase": "reporting",
                    "tasks": [
                        "Organize findings into coherent structure",
                        "Add citations for all claims",
                        f"Format as {self.config.output_format.value}",
                        "Generate executive summary"
                    ],
                    "estimated_minutes": int(analysis["estimated_time_minutes"] * 0.3)
                }
            ],

            "search_strategy": {
                "source_types": [st.value for st in self.config.source_types],
                "max_sources_per_question": max(
                    5, self.config.max_sources // len(research_questions)
                ),
                "use_parallel_search": self.config.use_subagents
            },

            "quality_criteria": {
                "min_sources": min(10, self.config.max_sources // 2),
                "require_citations": self.config.include_citations,
                "check_contradictions": self.config.include_contradictions,
                "min_confidence": 0.7
            },

            "created_at": datetime.utcnow().isoformat()
        }

        return plan

    def _display_plan(self, plan: Dict[str, Any]):
        """Display the research plan to the user"""
        print(f"\n{'─'*60}")
        print("RESEARCH PLAN")
        print(f"{'─'*60}\n")

        print(f"Objective: {plan['objective']}")
        print(f"Type: {plan['research_type']}")
        print(f"Scope: {plan['scope']}")
        print(f"Estimated Duration: {plan['estimated_duration_minutes']} minutes")
        print(f"Estimated Sources: {plan['estimated_sources']}")

        print(f"\nSearch Strategy:")
        print(f"  - Source Types: {', '.join(plan['search_strategy']['source_types'])}")
        print(f"  - Max Sources per Question: {plan['search_strategy']['max_sources_per_question']}")
        print(f"  - Parallel Search: {plan['search_strategy']['use_parallel_search']}")

        print(f"\nPhase Breakdown:")
        for phase_info in plan['phases']:
            print(f"\n  {phase_info['phase'].upper()} ({phase_info['estimated_minutes']} min):")
            for task in phase_info['tasks']:
                print(f"    • {task}")

        print(f"\n{'─'*60}\n")

    async def request_user_approval(self, plan: Dict[str, Any]) -> bool:
        """
        Request user approval for the plan (in interactive mode)

        Args:
            plan: The research plan

        Returns:
            True if approved, False otherwise
        """
        if not self.config.require_approval:
            return True

        print("\nDo you approve this research plan?")
        print("Options:")
        print("  1. Approve and continue")
        print("  2. Modify plan")
        print("  3. Cancel research")

        # In real implementation, wait for user input
        # For demo, auto-approve
        print("\n[Auto-approved for demo]")
        return True
