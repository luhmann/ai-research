"""
Phase 3: Analysis & Synthesis
"""
import asyncio
from typing import Dict, Any, List, Set
from datetime import datetime
from collections import defaultdict


class AnalysisPhase:
    """
    Phase 3: Analysis & Synthesis

    This phase:
    1. Cross-references multiple sources
    2. Identifies contradictions
    3. Extracts key themes and patterns
    4. Generates insights
    """

    def __init__(self, config):
        self.config = config

    async def execute(self, state) -> Dict[str, Any]:
        """
        Execute the analysis phase

        Args:
            state: ResearchState object with gathered sources

        Returns:
            Dictionary containing analysis results
        """
        print(f"\n{'='*60}")
        print(f"PHASE 3: ANALYSIS & SYNTHESIS")
        print(f"{'='*60}\n")

        sources = state.sources
        questions = state.research_questions

        print(f"Analyzing {len(sources)} sources...")
        print(f"Research questions: {len(questions)}\n")

        # Step 1: Cross-reference sources
        print("Step 1/5: Cross-referencing sources...")
        cross_references = await self._cross_reference_sources(sources, questions)

        # Step 2: Identify contradictions
        print("Step 2/5: Identifying contradictions...")
        contradictions = await self._identify_contradictions(sources, questions)

        # Step 3: Extract themes and patterns
        print("Step 3/5: Extracting themes and patterns...")
        themes = await self._extract_themes(sources, questions)

        # Step 4: Generate insights
        print("Step 4/5: Generating insights...")
        insights = await self._generate_insights(sources, questions, themes)

        # Step 5: Build knowledge graph
        print("Step 5/5: Building knowledge connections...")
        knowledge_graph = await self._build_knowledge_graph(themes, insights)

        # Create findings
        print("\nCreating findings...")
        findings = await self._create_findings(
            insights, sources, contradictions
        )

        # Add findings to state
        for finding in findings:
            state.add_finding(finding)

        # Display analysis summary
        self._display_analysis_summary(themes, insights, contradictions, findings)

        return {
            "cross_references": cross_references,
            "contradictions": contradictions,
            "themes": themes,
            "insights": insights,
            "knowledge_graph": knowledge_graph,
            "findings": findings,
            "analysis_confidence": self._calculate_confidence(sources, findings)
        }

    async def _cross_reference_sources(self, sources: List, questions: List) -> Dict[str, Any]:
        """Cross-reference sources to find corroboration"""

        # Group sources by question
        sources_by_question = defaultdict(list)
        for question in questions:
            sources_by_question[question.question] = question.sources

        cross_refs = {
            "total_sources": len(sources),
            "sources_per_question": {
                q: len(s) for q, s in sources_by_question.items()
            },
            "corroborated_facts": [],
            "unique_claims": []
        }

        # In production, use NLP to find corroborating information
        # For now, simplified analysis
        for question, q_sources in sources_by_question.items():
            if len(q_sources) >= 2:
                cross_refs["corroborated_facts"].append({
                    "question": question,
                    "sources_count": len(q_sources),
                    "confidence": min(0.9, 0.5 + (len(q_sources) * 0.1))
                })

        return cross_refs

    async def _identify_contradictions(self, sources: List, questions: List) -> List[Dict[str, Any]]:
        """Identify contradictory information between sources"""

        contradictions = []

        # In production, use semantic similarity and contradiction detection
        # For now, simple heuristic: if reliability scores vary widely
        for question in questions:
            q_sources = question.sources
            if len(q_sources) >= 2:
                reliability_scores = [
                    s.reliability_score for s in q_sources
                    if s.reliability_score is not None
                ]

                if reliability_scores:
                    variance = max(reliability_scores) - min(reliability_scores)
                    if variance > 0.3:
                        contradictions.append({
                            "question": question.question,
                            "type": "reliability_variance",
                            "description": f"Sources show varying reliability (variance: {variance:.2f})",
                            "sources_involved": len(q_sources),
                            "severity": "medium" if variance < 0.5 else "high"
                        })

        return contradictions

    async def _extract_themes(self, sources: List, questions: List) -> List[Dict[str, Any]]:
        """Extract key themes and patterns from sources"""

        themes = []

        # Extract themes from questions (simplified)
        for question in questions:
            # In production, use topic modeling or LLM-based theme extraction
            words = question.question.lower().split()
            key_terms = [w for w in words if len(w) > 5 and w.isalpha()]

            if key_terms:
                theme = {
                    "name": " ".join(key_terms[:3]),
                    "related_question": question.question,
                    "sources_count": len(question.sources),
                    "importance": question.priority,
                    "key_terms": key_terms
                }
                themes.append(theme)

        # Deduplicate and sort by importance
        themes = sorted(themes, key=lambda x: x["importance"], reverse=True)

        return themes[:5]  # Top 5 themes

    async def _generate_insights(
        self, sources: List, questions: List, themes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate insights from the analyzed information"""
        from state import Finding

        insights = []

        # Generate insights from themes
        for i, theme in enumerate(themes, 1):
            insight = {
                "id": f"insight_{i}",
                "type": "theme_based",
                "title": f"Key Finding: {theme['name']}",
                "description": (
                    f"Analysis of {theme['sources_count']} sources reveals important "
                    f"information about {theme['name']} in relation to "
                    f"{theme['related_question']}"
                ),
                "supporting_sources": theme['sources_count'],
                "confidence": min(0.9, 0.6 + (theme['sources_count'] * 0.05)),
                "priority": theme['importance']
            }
            insights.append(insight)

        # Generate comparative insights if we have multiple questions
        if len(questions) > 1:
            insight = {
                "id": f"insight_{len(insights) + 1}",
                "type": "comparative",
                "title": "Cross-Question Analysis",
                "description": (
                    f"Analysis across {len(questions)} research questions reveals "
                    f"connections and patterns that inform the overall research objective."
                ),
                "supporting_sources": len(sources),
                "confidence": 0.75,
                "priority": 4
            }
            insights.append(insight)

        return insights

    async def _build_knowledge_graph(
        self, themes: List[Dict[str, Any]], insights: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build a knowledge graph of connections"""

        # In production, build actual graph with nodes and edges
        # For now, simplified representation

        nodes = []
        edges = []

        # Create nodes from themes
        for theme in themes:
            nodes.append({
                "id": theme["name"],
                "type": "theme",
                "importance": theme["importance"]
            })

        # Create nodes from insights
        for insight in insights:
            nodes.append({
                "id": insight["id"],
                "type": "insight",
                "importance": insight["priority"]
            })

        # Create edges (connections)
        for insight in insights:
            if insight["type"] == "theme_based":
                # Connect insights to their themes
                for theme in themes:
                    if theme["name"] in insight["description"]:
                        edges.append({
                            "from": insight["id"],
                            "to": theme["name"],
                            "type": "derives_from"
                        })

        return {
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges)
        }

    async def _create_findings(
        self, insights: List[Dict[str, Any]], sources: List,
        contradictions: List[Dict[str, Any]]
    ) -> List:
        """Create Finding objects from insights"""
        from state import Finding

        findings = []

        for insight in insights:
            # Get relevant sources (simplified)
            relevant_sources = sources[:insight["supporting_sources"]]

            # Get related contradictions
            related_contradictions = [
                c["description"] for c in contradictions
                if insight.get("title", "") in c.get("description", "")
            ]

            finding = Finding(
                content=f"{insight['title']}: {insight['description']}",
                sources=relevant_sources,
                confidence=insight["confidence"],
                contradictions=related_contradictions
            )
            findings.append(finding)

        return findings

    def _calculate_confidence(self, sources: List, findings: List) -> float:
        """Calculate overall confidence in the analysis"""

        if not findings:
            return 0.0

        # Average confidence across findings
        avg_confidence = sum(f.confidence for f in findings) / len(findings)

        # Adjust based on source count
        source_factor = min(1.0, len(sources) / 20)  # 20+ sources = max

        # Combine
        overall_confidence = (avg_confidence * 0.7) + (source_factor * 0.3)

        return round(overall_confidence, 2)

    def _display_analysis_summary(
        self, themes: List, insights: List, contradictions: List, findings: List
    ):
        """Display analysis summary"""
        print(f"\n{'─'*60}")
        print("ANALYSIS SUMMARY")
        print(f"{'─'*60}\n")

        print(f"Key Themes Identified: {len(themes)}")
        for theme in themes[:3]:
            print(f"  • {theme['name']} (importance: {theme['importance']}/5)")

        print(f"\nInsights Generated: {len(insights)}")
        for insight in insights[:3]:
            print(f"  • {insight['title']} (confidence: {insight['confidence']:.0%})")

        print(f"\nContradictions Found: {len(contradictions)}")
        for contradiction in contradictions[:3]:
            print(f"  • {contradiction['description']} (severity: {contradiction['severity']})")

        print(f"\nTotal Findings: {len(findings)}")

        print(f"{'─'*60}\n")
