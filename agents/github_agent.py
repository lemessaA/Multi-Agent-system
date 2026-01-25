"""GitHub agent that uses the GitHub REST API.

This replaces the local mock with a minimal, safe caller to GitHub's
public search endpoints. It reads `GITHUB_API_KEY` or `GITHUB_TOKEN` from
the environment. If no token is present, it falls back to a harmless
mock response to avoid crashing during local development.
"""

import os
from typing import Any, Dict

import requests


def _make_message(text: str):
    return type("M", (), {"content": text})()


def _mock_response(content: str) -> Dict[str, Any]:
    return {"message": [_make_message(f"(mock) GitHub result for: {content}")]} 


def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
    messages = payload.get("message", [])
    content = ""
    if messages:
        last = messages[-1]
        content = last.get("content") if isinstance(last, dict) else getattr(last, "content", "")

    token = os.getenv("GITHUB_API_KEY") or os.getenv("GITHUB_TOKEN")
    if not token:
        return _mock_response(content)

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {token}",
        "User-Agent": "router-agent/1.0",
    }

    results = []

    try:
        # Search code (top 3 hits)
        params = {"q": f"{content} in:file", "per_page": 3}
        r_code = requests.get("https://api.github.com/search/code", headers=headers, params=params, timeout=10)
        if r_code.ok:
            data = r_code.json()
            for item in data.get("items", []):
                repo = item.get("repository", {}).get("full_name")
                path = item.get("path")
                url = item.get("html_url")
                results.append(f"code: {repo}/{path} — {url}")

        # Search issues/PRs (top 3)
        params_i = {"q": content, "per_page": 3}
        r_issues = requests.get("https://api.github.com/search/issues", headers=headers, params=params_i, timeout=10)
        if r_issues.ok:
            data = r_issues.json()
            for item in data.get("items", []):
                title = item.get("title")
                url = item.get("html_url")
                state = item.get("state")
                results.append(f"issue: [{state}] {title} — {url}")

    except requests.RequestException as e:
        return {"message": [_make_message(f"GitHub API request failed: {e}")]} 

    if not results:
        return {"message": [_make_message(f"No GitHub results for: {content}")]} 

    summary = f"GitHub results for: {content}\n" + "\n".join(results)
    return {"message": [_make_message(summary)]}