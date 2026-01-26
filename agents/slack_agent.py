from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from tools.slack_tools import search_slack_messages, send_slack_message, get_thread_replies
from config.settings import settings


model = init_chat_model(settings.SLACK_BOT_TOKEN)

slack_agent = create_agent(
    model,
    tools=[search_slack_messages, send_slack_message, get_thread_replies],
    system_prompt=(
        "You are a slack assistant agent. Answer questions about Slack channels and messages."
        "relevant thread and discussions where team members have participated."
        "share information from Slack channels using the provided tools."
    )
)