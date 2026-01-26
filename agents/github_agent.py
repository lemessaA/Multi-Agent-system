from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from tools.github_tools import search_code, search_issues

def build_github_agent():
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-4o-mini"
    )

    tools = [search_code, search_issues]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True,
        system_message=(
            "You are a GitHub research agent. "
            "Use tools to search code, issues, and pull requests. "
            "Always prefer tools over guessing."
        ),
    )

    return agent


class _LocalAgent:
    def __init__(self, name: str):
        self.name = name

    def run(self, query: str):
        from utils.llm import agent_llm
        return str(agent_llm.invoke([{"role": "user", "content": query}]))


def build_github_agent_safe():
    try:
        return build_github_agent()
    except Exception:
        return _LocalAgent("github")
github_agent = build_github_agent()