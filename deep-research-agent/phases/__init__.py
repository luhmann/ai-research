"""
Research phases for the Deep Research Agent
"""
from .planning import PlanningPhase
from .gathering import GatheringPhase
from .analysis import AnalysisPhase
from .reporting import ReportingPhase

__all__ = [
    'PlanningPhase',
    'GatheringPhase',
    'AnalysisPhase',
    'ReportingPhase'
]
