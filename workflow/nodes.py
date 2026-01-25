from pydantic import BaseModel, Field
from langgraph.types import Send
from .state import AgentInput, AgentOutput, Classification, RouterState

from utils.llm import router_llm
# Define the nodes used in the workflow

class ClassificationResult(BaseModel):
    """ Result of classifiying  a user query into agent-specific sub-questions."""

    classifications: list[Classification] = Field(
        description="List of agents to invoke with their targeted sub-questions"
    )

def classify_query(state: RouterState) -> dict:
    """Classify the user query into agent-specific sub-questions."""

    structured_llm = router_llm.with_structured_output(ClassificationResult)
    result = structured_llm.invoke([
        {
            "role": "system",
            "content": """
    Analyze this query and determine which knowledge bases to consult.
For each relevant source, generate a targeted sub-question optimized for that source.

Available sources:
- github: Code, API references, implementation details, issues, pull requests
- notion: Internal documentation, processes, policies, team wikis
- slack: Team discussions, informal knowledge sharing, recent conversations

Return ONLY the sources that are relevant to the query. Each source should have
a targeted sub-question optimized for that specific knowledge domain.

Example for "How do I authenticate API requests?":
- github: "What authentication code exists? Search for auth middleware, JWT handling"
- notion: "What authentication documentation exists? Look for API auth guides"
(slack omitted because it's not relevant for this technical question)
"""

        },
        { 
            "role": "user",
            "content": state["query"]
        }
    ])

    return {"classifications": result.classifications}



def route_to_agents(state: RouterState) -> list[Send]:
    """Route sub-questions to the appropriate agents based on classifications."""
    sends = []
    for classification in state["classifications"]:
        agent_input: AgentInput = {
            "query": classification["query"]
        }
        sends.append(Send(classification["source"], agent_input))
    return sends

def query_github(state: AgentInput) -> dict:
    """Invoke the GitHub agent with the provided query."""
    from agents import github_agent

    result = github_agent.invoke({
        "message": [{"role": "user", "content": state["query"]}]
    })
    return {"results": [{"source": "github", "result": result["message"][-1].content}]}

def query_notion(state: AgentInput) -> dict:
    """Invoke the Notion agent with the provided query."""
    from agents import notion_agent

    result = notion_agent.invoke({
        "message": [{"role":"user", "content": state["query"]}]

    })
    return {"results": [{"source": "notion", "result": result["message"][-1].content}]}


def query_slack(state: AgentInput) -> dict:
    """Invoke the Slack agent with the provide query."""
    from agents import slack_agent

    result = slack_agent.invoke({
        "message": [{"role": "user", "content": state["query"]}]

    })
    return {"results": [{"source": "slack", "result": result["message"][-1].content}]}


def synthesize_results(state: RouterState) -> dict:
    """Synthesize final answer from all agent results."""
    structured_llm = router_llm.with_structured_output(RouterState)
    combined_results = "\n\n".join(
        [f"Source: {res['source']}\nContent: {res['result']}" for res in state["results"]]
    )
    final_answer = structured_llm.invoke([
        {
            "role": "system",
            "content": """
            -Combine the information from the different sources without repeating yourself,
            -Highlight the most relevant and actionable points.,
            -Note any discrepencies between sources ,
            -Keep the answer concise and  well-organized,
            
            """
        },
        {
            "role": "user",
            "content": combined_results
        }
    ])
    return {"final_answer": final_answer}