from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any


DEFAULT_STATE: dict[str, Any] = {
    "config": {},
    "keyword_lists": {},
    "listing_snapshots": {},
    "imports": {},
    "history": [],
    "undo": [],
    "redo": [],
}


class SessionStore:
    def __init__(self, path: str | Path | None = None):
        configured = path or os.environ.get("ERANK_SESSION")
        self.path = Path(configured) if configured else Path.cwd() / ".erank_session.json"
        self.state = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return deepcopy(DEFAULT_STATE)
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        state = deepcopy(DEFAULT_STATE)
        for key, value in data.items():
            state[key] = value
        return state

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.state, indent=2, ensure_ascii=False), encoding="utf-8")

    def config(self) -> dict[str, Any]:
        return self.state.setdefault("config", {})

    def begin(self, action: str) -> None:
        snapshot = deepcopy(self.state)
        snapshot["undo"] = []
        snapshot["redo"] = []
        self.state.setdefault("undo", []).append({"action": action, "state": snapshot})
        self.state["undo"] = self.state["undo"][-50:]
        self.state["redo"] = []

    def record(self, action: str, details: dict[str, Any] | None = None) -> None:
        self.state.setdefault("history", []).append(
            {
                "at": datetime.now(timezone.utc).isoformat(),
                "action": action,
                "details": details or {},
            }
        )
        self.state["history"] = self.state["history"][-200:]

    def undo(self) -> dict[str, Any]:
        stack = self.state.setdefault("undo", [])
        if not stack:
            return {"ok": False, "message": "Nothing to undo"}
        current = deepcopy(self.state)
        current["undo"] = []
        current["redo"] = []
        entry = stack.pop()
        redo_stack = self.state.setdefault("redo", [])
        redo_stack.append({"action": entry["action"], "state": current})
        restored = deepcopy(entry["state"])
        restored["undo"] = stack
        restored["redo"] = redo_stack
        self.state = restored
        self.record("undo", {"action": entry["action"]})
        self.save()
        return {"ok": True, "undone": entry["action"]}

    def redo(self) -> dict[str, Any]:
        stack = self.state.setdefault("redo", [])
        if not stack:
            return {"ok": False, "message": "Nothing to redo"}
        current = deepcopy(self.state)
        current["undo"] = []
        current["redo"] = []
        entry = stack.pop()
        undo_stack = self.state.setdefault("undo", [])
        undo_stack.append({"action": entry["action"], "state": current})
        restored = deepcopy(entry["state"])
        restored["undo"] = undo_stack
        restored["redo"] = stack
        self.state = restored
        self.record("redo", {"action": entry["action"]})
        self.save()
        return {"ok": True, "redone": entry["action"]}

    def summary(self) -> dict[str, Any]:
        return {
            "session_path": str(self.path),
            "config_keys": sorted(self.config().keys()),
            "keyword_lists": sorted(self.state.get("keyword_lists", {}).keys()),
            "listing_snapshots": len(self.state.get("listing_snapshots", {})),
            "imports": self.state.get("imports", {}),
            "history_count": len(self.state.get("history", [])),
            "undo_count": len(self.state.get("undo", [])),
            "redo_count": len(self.state.get("redo", [])),
        }
