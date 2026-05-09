from dataclasses import dataclass, field
from typing import Any


@dataclass
class Artifact:
    kind: str
    path: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowResult:
    workflow_id: str
    status: str
    fetched: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0
    artifacts: list[Artifact] = field(default_factory=list)
    logs: list[str] = field(default_factory=list)

