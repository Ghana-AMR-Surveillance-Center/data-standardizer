from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict


def log_event(event_type: str, payload: Dict[str, Any]) -> None:
    os.makedirs("logs", exist_ok=True)
    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "type": event_type,
        "payload": payload,
    }
    try:
        with open(os.path.join("logs", "audit.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


