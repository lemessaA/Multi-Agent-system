"""Lightweight Notion agent shim for local testing."""

from typing import Any, Dict


def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
    messages = payload.get("message", [])
    content = ""
    if messages:
        last = messages[-1]
        content = last.get("content") if isinstance(last, dict) else getattr(last, "content", "")
    return {"message": [type("M", (), {"content": f"Notion result for: {content}"})()]}