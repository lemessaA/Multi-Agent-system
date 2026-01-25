from langchain.tools import tool
from config.settings import settings


@tool
def search_code(query: str, repo: str = None) -> str:
    """Search code in GitHub repositories."""
    repo = repo or settings.DEFAULT_REPO
    # Implement actual GitHub API call here
    return f"Found code matching '{query}' in {repo}: authentication middleware in src/auth.py"


@tool
def search_issues(query: str) -> str:
    """Search GitHub issues and pull requests."""
    # Implement actual GitHub API call here
    return f"Found 3 issues matching '{query}': #142 (API auth docs), #89 (OAuth flow), #203 (token refresh)"


@tool
def search_prs(query: str) -> str:
    """Search pull requests for implementation details."""
    # Implement actual GitHub API call here
    return f"PR #156 added JWT authentication, PR #178 updated OAuth scopes"