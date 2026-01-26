from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from tools.github_tools import search_code, search_issues, get_repo_details
from config.settings import settings

model = init_chat_model(settings.GITHUB_TOKEN)

github_agent = create_agent(
    model=model,
    tools=[search_code, search_issues, get_repo_details],
    system_prompt=(
        "You are a GitHub assistant agent. Use the provided tools to search code, issues, "
        "and get repository details on GitHub based on user queries."
    ),
    verbose=True,
    
)

