"""
Citation management tool for tracking and formatting sources
"""
from typing import Dict, Any, List
from datetime import datetime
import re


def create_citation_manager_tool():
    """
    Create a citation manager tool for Claude

    This tool manages citations and formats them in various styles
    """

    async def manage_citation(args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage citations for research sources

        Args:
            action: Action to perform (add, format, list, verify)
            source: Source information (for add action)
            citation_style: Citation style (apa, mla, chicago, ieee)
            claim: Claim to verify (for verify action)

        Returns:
            Citation management result
        """
        action = args.get("action", "add")
        source = args.get("source", {})
        citation_style = args.get("citation_style", "apa")
        claim = args.get("claim", "")

        result = {
            "action": action,
            "timestamp": datetime.utcnow().isoformat()
        }

        if action == "add":
            # Add a new citation
            formatted = format_citation(source, citation_style)
            result["citation"] = formatted
            result["citation_id"] = generate_citation_id(source)

        elif action == "format":
            # Format an existing source
            formatted = format_citation(source, citation_style)
            result["citation"] = formatted

        elif action == "list":
            # List all citations (mock)
            result["citations"] = [
                "[1] Sample citation in " + citation_style + " format",
                "[2] Another sample citation"
            ]

        elif action == "verify":
            # Verify a claim has citations
            has_citation = bool(claim and source)
            result["verified"] = has_citation
            result["claim"] = claim
            result["missing_citation"] = not has_citation

        return {
            "content": [{
                "type": "text",
                "text": f"Citation {action} completed:\n\n" + str(result)
            }],
            "metadata": result
        }

    return {
        "name": "manage_citation",
        "description": "Manage research citations. Can add sources, format citations "
                      "in various styles, list all citations, and verify claims are cited.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add", "format", "list", "verify"],
                    "description": "Citation management action to perform"
                },
                "source": {
                    "type": "object",
                    "description": "Source information (url, title, author, date, etc.)"
                },
                "citation_style": {
                    "type": "string",
                    "enum": ["apa", "mla", "chicago", "ieee"],
                    "description": "Citation style to use",
                    "default": "apa"
                },
                "claim": {
                    "type": "string",
                    "description": "Claim to verify has citations"
                }
            },
            "required": ["action"]
        },
        "function": manage_citation
    }


def format_citation(source: Dict[str, Any], style: str = "apa") -> str:
    """
    Format a source as a citation

    Args:
        source: Source information
        style: Citation style (apa, mla, chicago, ieee)

    Returns:
        Formatted citation string
    """
    url = source.get("url", "")
    title = source.get("title", "Untitled")
    author = source.get("author", "Unknown Author")
    date = source.get("date", datetime.utcnow().strftime("%Y-%m-%d"))
    accessed = source.get("accessed", datetime.utcnow().strftime("%Y-%m-%d"))

    # Extract year from date
    year_match = re.search(r'\d{4}', date)
    year = year_match.group(0) if year_match else "n.d."

    if style == "apa":
        # APA format: Author. (Year). Title. Retrieved from URL
        return f"{author}. ({year}). {title}. Retrieved from {url}"

    elif style == "mla":
        # MLA format: Author. "Title." Website, Date. URL.
        return f'{author}. "{title}." Web. {date}. {url}.'

    elif style == "chicago":
        # Chicago format: Author. "Title." Website. Date. URL.
        return f'{author}. "{title}." Accessed {accessed}. {url}.'

    elif style == "ieee":
        # IEEE format: [#] Author, "Title," Website, Date. [Online]. Available: URL
        return f'{author}, "{title}," {date}. [Online]. Available: {url}'

    else:
        # Default format
        return f"{author}. {title}. {url} (accessed {accessed})"


def generate_citation_id(source: Dict[str, Any]) -> str:
    """
    Generate a unique ID for a citation

    Args:
        source: Source information

    Returns:
        Citation ID
    """
    url = source.get("url", "")
    # Simple hash-based ID
    if url:
        return f"cite_{abs(hash(url)) % 100000:05d}"
    return f"cite_{abs(hash(str(source))) % 100000:05d}"


def extract_citations_from_text(text: str) -> List[str]:
    """
    Extract citation markers from text

    Args:
        text: Text containing citations

    Returns:
        List of citation markers found
    """
    # Match patterns like [1], [Author 2023], (Smith, 2023), etc.
    patterns = [
        r'\[\d+\]',  # [1], [2], etc.
        r'\[[\w\s]+\s+\d{4}\]',  # [Author 2023]
        r'\([\w\s]+,\s*\d{4}\)',  # (Author, 2023)
    ]

    citations = []
    for pattern in patterns:
        citations.extend(re.findall(pattern, text))

    return citations


def validate_citations(text: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate that all claims in text are properly cited

    Args:
        text: Text to validate
        sources: List of available sources

    Returns:
        Validation results
    """
    citations = extract_citations_from_text(text)

    # Split text into sentences
    sentences = re.split(r'[.!?]+', text)

    uncited_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence or len(sentence) < 20:
            continue

        # Check if sentence has a citation
        has_citation = any(cite in sentence for cite in citations)
        if not has_citation:
            uncited_sentences.append(sentence)

    return {
        "total_sentences": len([s for s in sentences if s.strip()]),
        "citations_found": len(citations),
        "uncited_sentences": uncited_sentences,
        "citation_coverage": (
            1.0 - len(uncited_sentences) / max(len(sentences), 1)
        ),
        "is_well_cited": len(uncited_sentences) < len(sentences) * 0.3
    }


class CitationManager:
    """Manager for tracking citations throughout research"""

    def __init__(self):
        self.sources: List[Dict[str, Any]] = []
        self.citation_map: Dict[str, str] = {}  # claim -> citation_id

    def add_source(self, source: Dict[str, Any]) -> str:
        """Add a source and return its citation ID"""
        citation_id = generate_citation_id(source)
        self.sources.append({
            **source,
            "citation_id": citation_id
        })
        return citation_id

    def cite_claim(self, claim: str, citation_id: str):
        """Associate a claim with a citation"""
        self.citation_map[claim] = citation_id

    def get_bibliography(self, style: str = "apa") -> List[str]:
        """Get formatted bibliography"""
        return [
            format_citation(source, style)
            for source in self.sources
        ]

    def get_citation_for_claim(self, claim: str) -> str:
        """Get the citation ID for a claim"""
        return self.citation_map.get(claim, "")

    def get_source_by_id(self, citation_id: str) -> Dict[str, Any]:
        """Get source by citation ID"""
        for source in self.sources:
            if source.get("citation_id") == citation_id:
                return source
        return {}
