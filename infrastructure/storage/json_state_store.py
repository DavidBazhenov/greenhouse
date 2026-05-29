from __future__ import annotations

import json
from pathlib import Path

from domain.models import GardenState


class JsonStateStore:
    def __init__(self, path: str) -> None:
        self.path = Path(path)

    def load(self) -> GardenState:
        if not self.path.exists():
            return GardenState()
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return GardenState.from_dict(data)

    def save(self, state: GardenState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(state.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
