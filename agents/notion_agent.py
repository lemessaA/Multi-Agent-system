from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from tools.notion_tools import search_notion, get_notion_page

def build_notion_agent():
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-4o-mini"
    )

    tools = [search_notion, get_notion_page]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True,
        system_message=(
            "You are a Notion workspace assistant. "
            "Search pages and retrieve content only using tools. "
            "Never invent Notion data."
        ),
    )

    return agent
class _LocalAgent:
    def __init__(self, name: str):
        self.name = name

    def run(self, query: str):
        from utils.llm import agent_llm
        return str(agent_llm.invoke([{"role": "user", "content": query}]))


def build_notion_agent_safe():
    try:
        return build_notion_agent()
    except Exception:
        return _LocalAgent("notion")


notion_agent = build_notion_agent_safe()