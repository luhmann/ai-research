"""
State management for research sessions
"""
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional
from pathlib import Path


class PhaseStatus(Enum):
    """Status of a research phase"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class Phase(Enum):
    """Research phases"""
    PLANNING = "planning"
    GATHERING = "gathering"
    ANALYSIS = "analysis"
    REPORTING = "reporting"


@dataclass
class Source:
    """Information about a source"""
    url: str
    title: str
    snippet: str
    timestamp: str
    reliability_score: Optional[float] = None
    source_type: str = "web"


@dataclass
class ResearchQuestion:
    """A research question to investigate"""
    question: str
    priority: int = 1  # 1-5, 5 is highest
    status: str = "pending"  # pending, researched, answered
    answer: Optional[str] = None
    sources: List[Source] = None

    def __post_init__(self):
        if self.sources is None:
            self.sources = []


@dataclass
class Finding:
    """A research finding or insight"""
    content: str
    sources: List[Source]
    confidence: float  # 0.0 to 1.0
    contradictions: List[str] = None  # Contradictory information found
    timestamp: str = None

    def __post_init__(self):
        if self.contradictions is None:
            self.contradictions = []
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class PhaseResult:
    """Result from a research phase"""
    phase: Phase
    status: PhaseStatus
    data: Dict[str, Any]
    timestamp: str
    duration_seconds: Optional[float] = None
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class ResearchState:
    """Manages the state of a research session"""

    def __init__(self, query: str, session_id: Optional[str] = None):
        self.query = query
        self.session_id = session_id or self._generate_session_id()
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = self.created_at

        # Phase tracking
        self.current_phase: Optional[Phase] = None
        self.phase_results: Dict[Phase, PhaseResult] = {}

        # Research data
        self.research_plan: Dict[str, Any] = {}
        self.research_questions: List[ResearchQuestion] = []
        self.sources: List[Source] = []
        self.findings: List[Finding] = []
        self.final_report: Optional[str] = None

        # Metadata
        self.total_sources_gathered: int = 0
        self.total_time_seconds: float = 0.0
        self.user_modifications: List[Dict[str, Any]] = []

    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        # Simple hash of query for uniqueness
        query_hash = abs(hash(self.query)) % 10000
        return f"research_{timestamp}_{query_hash:04d}"

    def start_phase(self, phase: Phase):
        """Mark a phase as started"""
        self.current_phase = phase
        self.updated_at = datetime.utcnow().isoformat()

    def complete_phase(self, phase: Phase, data: Dict[str, Any],
                      duration_seconds: float = 0.0,
                      errors: List[str] = None):
        """Mark a phase as completed and store results"""
        result = PhaseResult(
            phase=phase,
            status=PhaseStatus.COMPLETED,
            data=data,
            timestamp=datetime.utcnow().isoformat(),
            duration_seconds=duration_seconds,
            errors=errors or []
        )
        self.phase_results[phase] = result
        self.updated_at = result.timestamp
        self.total_time_seconds += duration_seconds

    def fail_phase(self, phase: Phase, errors: List[str]):
        """Mark a phase as failed"""
        result = PhaseResult(
            phase=phase,
            status=PhaseStatus.FAILED,
            data={},
            timestamp=datetime.utcnow().isoformat(),
            errors=errors
        )
        self.phase_results[phase] = result
        self.updated_at = result.timestamp

    def add_source(self, source: Source):
        """Add a source to the research"""
        self.sources.append(source)
        self.total_sources_gathered += 1
        self.updated_at = datetime.utcnow().isoformat()

    def add_finding(self, finding: Finding):
        """Add a research finding"""
        self.findings.append(finding)
        self.updated_at = datetime.utcnow().isoformat()

    def add_user_modification(self, modification_type: str, data: Dict[str, Any]):
        """Record a user modification to the research"""
        self.user_modifications.append({
            "type": modification_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.updated_at = datetime.utcnow().isoformat()

    def get_phase_status(self, phase: Phase) -> PhaseStatus:
        """Get the status of a specific phase"""
        if phase not in self.phase_results:
            return PhaseStatus.PENDING
        return self.phase_results[phase].status

    def is_phase_complete(self, phase: Phase) -> bool:
        """Check if a phase is completed"""
        return self.get_phase_status(phase) == PhaseStatus.COMPLETED

    def get_progress(self) -> Dict[str, Any]:
        """Get overall progress summary"""
        phases = [Phase.PLANNING, Phase.GATHERING, Phase.ANALYSIS, Phase.REPORTING]
        completed = sum(1 for p in phases if self.is_phase_complete(p))

        return {
            "session_id": self.session_id,
            "query": self.query,
            "current_phase": self.current_phase.value if self.current_phase else None,
            "phases_completed": completed,
            "total_phases": len(phases),
            "progress_percent": (completed / len(phases)) * 100,
            "sources_gathered": self.total_sources_gathered,
            "findings_count": len(self.findings),
            "elapsed_time_seconds": self.total_time_seconds,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    def _make_serializable(self, obj):
        """Convert objects to JSON-serializable format"""
        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_serializable(i) for i in obj]
        elif hasattr(obj, '__dict__'):
            return self._make_serializable(obj.__dict__)
        else:
            return str(obj)

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization"""
        return {
            "session_id": self.session_id,
            "query": self.query,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "current_phase": self.current_phase.value if self.current_phase else None,
            "phase_results": {
                p.value: {
                    "status": r.status.value,
                    "data": self._make_serializable(r.data),
                    "timestamp": r.timestamp,
                    "duration_seconds": r.duration_seconds,
                    "errors": r.errors
                }
                for p, r in self.phase_results.items()
            },
            "research_plan": self.research_plan,
            "research_questions": [
                {
                    "question": q.question,
                    "priority": q.priority,
                    "status": q.status,
                    "answer": q.answer,
                    "sources": [asdict(s) for s in q.sources]
                }
                for q in self.research_questions
            ],
            "sources": [asdict(s) for s in self.sources],
            "findings": [asdict(f) for f in self.findings],
            "final_report": self.final_report,
            "total_sources_gathered": self.total_sources_gathered,
            "total_time_seconds": self.total_time_seconds,
            "user_modifications": self.user_modifications
        }

    def save(self, directory: str = "./research_sessions"):
        """Save state to disk"""
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, f"{self.session_id}.json")

        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

        return filepath

    @classmethod
    def load(cls, session_id: str, directory: str = "./research_sessions") -> 'ResearchState':
        """Load state from disk"""
        filepath = os.path.join(directory, f"{session_id}.json")

        with open(filepath, 'r') as f:
            data = json.load(f)

        # Reconstruct the state object
        state = cls(query=data["query"], session_id=data["session_id"])
        state.created_at = data["created_at"]
        state.updated_at = data["updated_at"]
        state.current_phase = Phase(data["current_phase"]) if data["current_phase"] else None
        state.research_plan = data["research_plan"]
        state.final_report = data["final_report"]
        state.total_sources_gathered = data["total_sources_gathered"]
        state.total_time_seconds = data["total_time_seconds"]
        state.user_modifications = data["user_modifications"]

        # Reconstruct complex objects
        state.research_questions = [
            ResearchQuestion(
                question=q["question"],
                priority=q["priority"],
                status=q["status"],
                answer=q["answer"],
                sources=[Source(**s) for s in q["sources"]]
            )
            for q in data["research_questions"]
        ]

        state.sources = [Source(**s) for s in data["sources"]]
        state.findings = [Finding(**f) for f in data["findings"]]

        # Reconstruct phase results
        for phase_name, result_data in data["phase_results"].items():
            phase = Phase(phase_name)
            state.phase_results[phase] = PhaseResult(
                phase=phase,
                status=PhaseStatus(result_data["status"]),
                data=result_data["data"],
                timestamp=result_data["timestamp"],
                duration_seconds=result_data["duration_seconds"],
                errors=result_data["errors"]
            )

        return state

    @staticmethod
    def list_sessions(directory: str = "./research_sessions") -> List[Dict[str, Any]]:
        """List all saved research sessions"""
        if not os.path.exists(directory):
            return []

        sessions = []
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                filepath = os.path.join(directory, filename)
                with open(filepath, 'r') as f:
                    data = json.load(f)
                sessions.append({
                    "session_id": data["session_id"],
                    "query": data["query"],
                    "created_at": data["created_at"],
                    "updated_at": data["updated_at"],
                    "progress_percent": (
                        sum(1 for p in data["phase_results"].values()
                            if p["status"] == "completed") / 4 * 100
                    )
                })

        return sorted(sessions, key=lambda x: x["updated_at"], reverse=True)
