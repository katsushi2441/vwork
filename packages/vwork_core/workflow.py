from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


@dataclass
class Workflow:
    spec: dict[str, Any]
    path: Path | None = None
    logs: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, path: str | Path) -> "Workflow":
        p = Path(path)
        text = p.read_text(encoding="utf-8")
        if p.suffix in {".yaml", ".yml"}:
            if yaml is None:
                raise RuntimeError("PyYAML is required to load YAML workflows")
            spec = yaml.safe_load(text)
        else:
            spec = json.loads(text)
        return cls(spec=spec, path=p)

    @property
    def id(self) -> str:
        return str(self.spec.get("id") or "workflow")

    @property
    def name(self) -> str:
        return str(self.spec.get("name") or self.id)

    def log(self, message: str) -> None:
        self.logs.append(message)

    def validate_minimum(self) -> list[str]:
        missing = []
        for key in ("id", "name", "source", "generate", "publish"):
            if key not in self.spec:
                missing.append(key)
        return missing

