from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from tools.slack_tools import (
    send_slack_message,
    search_slack_messages,
    get_thread_replies,
)

def build_slack_agent():
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-4o-mini"
    )

    tools = [
        send_slack_message,
        search_slack_messages,
        get_thread_replies,
    ]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True,
        system_message=(
            "You are a Slack operations agent. "
            "Search messages, read threads, and send messages using tools. "
            "Do not assume conversation context."
        ),
    )

    return agent
class _LocalAgent:
    def __init__(self, name: str):
        self.name = name

    def run(self, query: str):
        from utils.llm import agent_llm
        return str(agent_llm.invoke([{"role": "user", "content": query}]))


def build_slack_agent_safe():
    try:
        return build_slack_agent()
    except Exception:
        return _LocalAgent("slack")


slack_agent = build_slack_agent_safe()