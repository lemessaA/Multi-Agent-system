

import os
from typing import Optional


class Settings:
    GROQ_API_KEY: Optional[str] = os.getenv( 'GROQ_API_KEY' )
    GITHUB_TOKEN: Optional[str] = os.getenv( 'GITHUB_TOKEN' )
    NOTION_TOKEN: Optional[str] = os.getenv( 'NOTION_TOKEN' )
    SLACK_BOT_TOKEN: Optional[str] = os.getenv( 'SLACK_TOKEN' )

    # Model configurations
    ROUTER_MODEL: str = "llama2-70b-chat"
    AGENT_MODEL: str = "llama2-70b-chat"

    # Github settings
    DEFAULT_GITHUB_REPO: str = "main"
    # slack settings
    DEFAULT_SLACK_CHANNEL: str = "general"

settings = Settings()
