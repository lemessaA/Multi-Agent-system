from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from typing import List, Any
from langchain.tools import BaseTool

model = init_chat_model("groq:groq-7b-chat")

github_agent = create_agent(
    model,
    tools=[BaseTool]
)