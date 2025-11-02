"""
Configuration options for the Deep Research Agent
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List


class ResearchDepth(Enum):
    """Research depth levels"""
    QUICK = "quick"      # 1-3 min, 5-10 sources
    MEDIUM = "medium"    # 5-10 min, 20-30 sources
    DEEP = "deep"        # 15-30+ min, 50+ sources


class OutputFormat(Enum):
    """Output format options"""
    MARKDOWN = "markdown"           # Full markdown report
    JSON = "json"                   # Structured JSON data
    SUMMARY = "summary"             # Executive summary only
    FULL_DOSSIER = "full_dossier"  # Complete research package


class SourceType(Enum):
    """Types of sources to search"""
    WEB = "web"                     # General web search
    ACADEMIC = "academic"           # Academic papers
    NEWS = "news"                   # News articles
    DOCUMENTATION = "documentation" # Technical docs
    CUSTOM = "custom"               # User-provided sources


@dataclass
class ResearchConfig:
    """Configuration for a research session"""

    # Research parameters
    depth: ResearchDepth = ResearchDepth.MEDIUM
    max_sources: Optional[int] = None  # Override based on depth
    max_time_minutes: Optional[int] = None  # Time limit

    # Source configuration
    source_types: List[SourceType] = None
    custom_sources: List[str] = None  # Specific URLs or domains
    exclude_domains: List[str] = None  # Domains to exclude

    # Output configuration
    output_format: OutputFormat = OutputFormat.MARKDOWN
    include_citations: bool = True
    include_confidence_scores: bool = True
    include_contradictions: bool = True

    # Phase control
    auto_advance: bool = False  # Automatically proceed through phases
    require_approval: bool = True  # Require user approval between phases
    interactive: bool = False  # Interactive real-time mode

    # Advanced options
    use_subagents: bool = True  # Use parallel subagents
    max_subagents: int = 3  # Maximum parallel subagents
    enable_fact_checking: bool = True
    save_intermediate_results: bool = True

    # API configuration
    anthropic_api_key: Optional[str] = None  # If not in env
    model: str = "claude-sonnet-4.5"

    def __post_init__(self):
        """Set defaults based on depth"""
        if self.source_types is None:
            self.source_types = [SourceType.WEB]

        if self.custom_sources is None:
            self.custom_sources = []

        if self.exclude_domains is None:
            self.exclude_domains = []

        # Set max_sources based on depth if not specified
        if self.max_sources is None:
            if self.depth == ResearchDepth.QUICK:
                self.max_sources = 10
            elif self.depth == ResearchDepth.MEDIUM:
                self.max_sources = 30
            else:  # DEEP
                self.max_sources = 100

        # Set time limits based on depth if not specified
        if self.max_time_minutes is None:
            if self.depth == ResearchDepth.QUICK:
                self.max_time_minutes = 3
            elif self.depth == ResearchDepth.MEDIUM:
                self.max_time_minutes = 10
            else:  # DEEP
                self.max_time_minutes = 30


# Default configurations for common use cases
QUICK_RESEARCH = ResearchConfig(
    depth=ResearchDepth.QUICK,
    auto_advance=True,
    require_approval=False,
    output_format=OutputFormat.SUMMARY
)

INTERACTIVE_RESEARCH = ResearchConfig(
    depth=ResearchDepth.MEDIUM,
    auto_advance=False,
    require_approval=True,
    interactive=True,
    output_format=OutputFormat.MARKDOWN
)

DEEP_RESEARCH = ResearchConfig(
    depth=ResearchDepth.DEEP,
    auto_advance=False,
    require_approval=True,
    use_subagents=True,
    max_subagents=5,
    output_format=OutputFormat.FULL_DOSSIER
)
