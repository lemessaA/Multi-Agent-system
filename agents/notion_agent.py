from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from tools.notion_tools import search_notion, get_notion_page
from config.settings import settings


model = init_chat_model(settings.NOTION_TOKEN)

notion_agent = create_agent(
    model=model,
    tools=[search_notion, get_notion_page],
    system_prompt=(
        "You are a Notion expert. Answer questions about Notion pages and content."
        "process, policies, and documentation by  searching Notion workspaces and pages."
        "the organizaton's Notion workspace using the provided tools."
    ),
    verbose=True,
)