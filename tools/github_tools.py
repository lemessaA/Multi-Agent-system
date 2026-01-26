import os
import requests
from typing import Optional
from langchain.tools import tool
from dotenv import load_dotenv



load_dotenv()



# helper for safe requests


def _make_github_header() -> dict:
    token = os.getenv("GITHUB_API_KEY") or os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("Github token not found in environment variables.")
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {token}",
        "User-Agent": "langchain-github-tool/1.0",

    }


# GitHub Search Tool

@tool
def search_code(query: str, max_results: Optional[int] = 3) -> str:
    """Search GitHub code for a given query."""
    headers = _make_github_header()
    params = {"q": f"{query} in:file", "per_page": max_results}
    response = requests.get("https://api.github.com/search/code", headers=headers, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    results = []
    for item in data.get("items", []):
        repo = item.get("repository", {}).get("full_name")
        path = item.get("path")
        url = item.get("html_url")
        results.append(f"{repo}/{path} — {url}")
    return "\n".join(results) if results else "No results found."

@tool
def search_issues(query: str, max_results: Optional[int] = 3) -> str:
    """Search GitHub issues and pull requests for a given query."""
    headers = _make_github_header()
    params = {"q": query, "per_page": max_results}
    response = requests.get("https://api.github.com/search/issues", headers=headers, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    results = []
    for item in data.get("items", []):
        title = item.get("title")
        url = item.get("html_url")
        state = item.get("state")
        results.append(f"[{state}] {title} — {url}")
    return "\n".join(results) if results else "No results found."

@tool
def get_repo_details(owner: str, repo: str) -> str:
    """Get details of a GitHub repository."""
    headers = _make_github_header()
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
    details = (
        f"Repository: {data.get('full_name')}\n"
        f"Description: {data.get('description')}\n"
        f"Stars: {data.get('stargazers_count')}\n"
        f"Forks: {data.get('forks_count')}\n"
        f"Open Issues: {data.get('open_issues_count')}\n"
        f"URL: {data.get('html_url')}"
    )
    return details


