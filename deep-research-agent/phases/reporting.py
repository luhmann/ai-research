"""
Phase 4: Report Generation
"""
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from config import OutputFormat


class ReportingPhase:
    """
    Phase 4: Report Generation

    This phase:
    1. Organizes findings into coherent structure
    2. Adds citations for all claims
    3. Formats according to user preferences
    4. Generates executive summary
    """

    def __init__(self, config):
        self.config = config

    async def execute(self, state, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the reporting phase

        Args:
            state: ResearchState object
            analysis_result: Results from analysis phase

        Returns:
            Dictionary containing the final report
        """
        print(f"\n{'='*60}")
        print(f"PHASE 4: REPORT GENERATION")
        print(f"{'='*60}\n")

        print(f"Output format: {self.config.output_format.value}")
        print(f"Include citations: {self.config.include_citations}")
        print(f"Include contradictions: {self.config.include_contradictions}\n")

        # Step 1: Generate executive summary
        print("Step 1/4: Generating executive summary...")
        executive_summary = await self._generate_executive_summary(state, analysis_result)

        # Step 2: Organize findings
        print("Step 2/4: Organizing findings...")
        organized_content = await self._organize_findings(state, analysis_result)

        # Step 3: Add citations
        print("Step 3/4: Adding citations...")
        cited_content = await self._add_citations(organized_content, state.sources)

        # Step 4: Format report
        print("Step 4/4: Formatting final report...")
        final_report = await self._format_report(
            executive_summary,
            cited_content,
            state,
            analysis_result
        )

        # Store in state
        state.final_report = final_report

        # Display report
        self._display_report(final_report)

        return {
            "report": final_report,
            "format": self.config.output_format.value,
            "word_count": len(final_report.split()),
            "citation_count": len(state.sources),
            "executive_summary": executive_summary
        }

    async def _generate_executive_summary(
        self, state, analysis_result: Dict[str, Any]
    ) -> str:
        """Generate a concise executive summary"""

        findings = state.findings
        insights = analysis_result.get("insights", [])
        confidence = analysis_result.get("analysis_confidence", 0.0)

        summary = f"""# Executive Summary

**Research Query:** {state.query}

**Research Conducted:** {datetime.utcnow().strftime("%Y-%m-%d")}

**Sources Analyzed:** {state.total_sources_gathered}

**Overall Confidence:** {confidence:.0%}

## Key Findings

"""

        # Add top findings
        for i, finding in enumerate(findings[:5], 1):
            summary += f"{i}. {finding.content[:200]}{'...' if len(finding.content) > 200 else ''}\n"
            summary += f"   *Confidence: {finding.confidence:.0%}*\n\n"

        # Add key insights
        if insights:
            summary += "\n## Key Insights\n\n"
            for insight in insights[:3]:
                summary += f"- **{insight['title']}**: {insight['description']}\n"

        # Add limitations/contradictions if enabled
        if self.config.include_contradictions:
            contradictions = analysis_result.get("contradictions", [])
            if contradictions:
                summary += "\n## Important Considerations\n\n"
                for contradiction in contradictions[:3]:
                    summary += f"- {contradiction['description']}\n"

        return summary

    async def _organize_findings(
        self, state, analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Organize findings into a coherent structure"""

        themes = analysis_result.get("themes", [])
        findings = state.findings

        # Group findings by theme
        content_sections = []

        # Introduction
        content_sections.append({
            "title": "Introduction",
            "content": f"This research investigates: {state.query}\n\n"
                      f"The analysis is based on {state.total_sources_gathered} sources "
                      f"gathered across {len(state.research_questions)} research questions."
        })

        # Main content organized by themes
        for theme in themes:
            # Find findings related to this theme
            related_findings = [
                f for f in findings
                if any(term in f.content.lower()
                      for term in theme.get("key_terms", []))
            ]

            if related_findings:
                section_content = f"## {theme['name'].title()}\n\n"

                for finding in related_findings:
                    section_content += f"{finding.content}\n\n"

                    # Add contradictions if any
                    if finding.contradictions and self.config.include_contradictions:
                        section_content += "**Note:** "
                        section_content += "; ".join(finding.contradictions) + "\n\n"

                content_sections.append({
                    "title": theme['name'].title(),
                    "content": section_content
                })

        # Conclusion
        content_sections.append({
            "title": "Conclusion",
            "content": self._generate_conclusion(state, analysis_result)
        })

        return {
            "sections": content_sections,
            "total_sections": len(content_sections)
        }

    def _generate_conclusion(self, state, analysis_result: Dict[str, Any]) -> str:
        """Generate conclusion section"""

        insights = analysis_result.get("insights", [])
        confidence = analysis_result.get("analysis_confidence", 0.0)

        conclusion = "## Conclusion\n\n"
        conclusion += f"This research on '{state.query}' has yielded {len(state.findings)} "
        conclusion += f"key findings based on {state.total_sources_gathered} sources.\n\n"

        if insights:
            conclusion += "The analysis reveals several important insights:\n\n"
            for insight in insights[:3]:
                conclusion += f"- {insight['description']}\n"

        conclusion += f"\n\nThe overall confidence in these findings is {confidence:.0%}, "
        conclusion += "based on source quality, cross-referencing, and corroboration.\n"

        return conclusion

    async def _add_citations(
        self, organized_content: Dict[str, Any], sources: List
    ) -> Dict[str, Any]:
        """Add citations to the content"""
        from tools.citation import format_citation

        if not self.config.include_citations:
            return organized_content

        # Create bibliography
        bibliography = []
        for i, source in enumerate(sources, 1):
            citation = format_citation({
                "url": source.url,
                "title": source.title,
                "author": "Unknown",  # Would extract from source in production
                "date": source.timestamp
            }, style="apa")

            bibliography.append(f"[{i}] {citation}")

        # Add bibliography section
        organized_content["sections"].append({
            "title": "References",
            "content": "## References\n\n" + "\n\n".join(bibliography)
        })

        organized_content["bibliography"] = bibliography
        return organized_content

    async def _format_report(
        self, executive_summary: str, content: Dict[str, Any],
        state, analysis_result: Dict[str, Any]
    ) -> str:
        """Format the final report according to output format"""

        if self.config.output_format == OutputFormat.SUMMARY:
            # Executive summary only
            return executive_summary

        elif self.config.output_format == OutputFormat.MARKDOWN:
            # Full markdown report
            return self._format_markdown(executive_summary, content, state)

        elif self.config.output_format == OutputFormat.JSON:
            # Structured JSON
            return self._format_json(executive_summary, content, state, analysis_result)

        elif self.config.output_format == OutputFormat.FULL_DOSSIER:
            # Complete research package
            return self._format_full_dossier(executive_summary, content, state, analysis_result)

        else:
            return executive_summary

    def _format_markdown(self, summary: str, content: Dict[str, Any], state) -> str:
        """Format as markdown report"""

        report = f"""# Research Report: {state.query}

{summary}

---

"""

        # Add all sections
        for section in content["sections"]:
            report += f"\n{section['content']}\n\n"

        # Add metadata
        report += f"""
---

**Research Metadata:**
- Session ID: {state.session_id}
- Created: {state.created_at}
- Total Research Time: {state.total_time_seconds:.1f} seconds
- Sources: {state.total_sources_gathered}
- Findings: {len(state.findings)}
"""

        return report

    def _format_json(
        self, summary: str, content: Dict[str, Any],
        state, analysis_result: Dict[str, Any]
    ) -> str:
        """Format as JSON"""
        import json

        data = {
            "query": state.query,
            "session_id": state.session_id,
            "created_at": state.created_at,
            "executive_summary": summary,
            "sections": content["sections"],
            "findings": [
                {
                    "content": f.content,
                    "confidence": f.confidence,
                    "sources_count": len(f.sources),
                    "contradictions": f.contradictions
                }
                for f in state.findings
            ],
            "sources": [
                {
                    "url": s.url,
                    "title": s.title,
                    "reliability": s.reliability_score
                }
                for s in state.sources
            ],
            "analysis": {
                "confidence": analysis_result.get("analysis_confidence", 0.0),
                "themes_count": len(analysis_result.get("themes", [])),
                "insights_count": len(analysis_result.get("insights", [])),
                "contradictions_count": len(analysis_result.get("contradictions", []))
            },
            "metadata": {
                "total_time_seconds": state.total_time_seconds,
                "sources_gathered": state.total_sources_gathered,
                "findings_count": len(state.findings)
            }
        }

        return json.dumps(data, indent=2)

    def _format_full_dossier(
        self, summary: str, content: Dict[str, Any],
        state, analysis_result: Dict[str, Any]
    ) -> str:
        """Format as complete research dossier"""

        # Start with markdown report
        dossier = self._format_markdown(summary, content, state)

        # Add detailed analysis appendix
        dossier += "\n\n---\n\n# Appendix: Detailed Analysis\n\n"

        # Add themes
        dossier += "## Identified Themes\n\n"
        for theme in analysis_result.get("themes", []):
            dossier += f"### {theme['name'].title()}\n"
            dossier += f"- Importance: {theme['importance']}/5\n"
            dossier += f"- Sources: {theme['sources_count']}\n"
            dossier += f"- Key Terms: {', '.join(theme.get('key_terms', []))}\n\n"

        # Add insights
        dossier += "## Generated Insights\n\n"
        for insight in analysis_result.get("insights", []):
            dossier += f"### {insight['title']}\n"
            dossier += f"{insight['description']}\n\n"
            dossier += f"- Confidence: {insight['confidence']:.0%}\n"
            dossier += f"- Supporting Sources: {insight['supporting_sources']}\n\n"

        # Add contradictions
        if analysis_result.get("contradictions"):
            dossier += "## Contradictions & Limitations\n\n"
            for contradiction in analysis_result.get("contradictions", []):
                dossier += f"### {contradiction['type']}\n"
                dossier += f"{contradiction['description']}\n"
                dossier += f"- Severity: {contradiction['severity']}\n"
                dossier += f"- Sources Involved: {contradiction['sources_involved']}\n\n"

        # Add all sources with details
        dossier += "## Complete Source List\n\n"
        for i, source in enumerate(state.sources, 1):
            dossier += f"{i}. **{source.title}**\n"
            dossier += f"   - URL: {source.url}\n"
            dossier += f"   - Reliability: {source.reliability_score:.2f}\n"
            dossier += f"   - Type: {source.source_type}\n"
            dossier += f"   - Snippet: {source.snippet[:100]}...\n\n"

        return dossier

    def _display_report(self, report: str):
        """Display the final report"""
        print(f"\n{'='*60}")
        print("FINAL REPORT")
        print(f"{'='*60}\n")

        # Display first 1000 characters
        preview_length = 1000
        if len(report) > preview_length:
            print(report[:preview_length])
            print(f"\n... [Report continues for {len(report) - preview_length} more characters]")
        else:
            print(report)

        print(f"\n{'='*60}\n")
