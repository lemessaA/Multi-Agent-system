from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from workflow.state import RouterState, Classification, AgentInput, AgentOutput
from workflow.nodes import (
    classify_query,
    query_github,
    query_notion,
    query_slack,
    synthesize_results,
    route_to_agents,
)

# `router_llm` is initialized in `workflow.nodes` to avoid circular imports.

workflow = (
    StateGraph(RouterState)
    .add_node("classify", classify_query)
    .add_node("github", query_github)
    .add_node("notion", query_notion)
    .add_node("slack", query_slack)
    .add_node("synthesize", synthesize_results)
    .add_edge(START, "classify")
    .add_conditional_edges("classify", route_to_agents, ["github", "notion", "slack"])
    .add_edge("github", "synthesize")
    .add_edge("notion", "synthesize")
    .add_edge("slack", "synthesize")
    .add_edge("synthesize", END)
    .compile()
)

# Backwards-compatible alias: some callers import `OrchestratorGraph` from this module.
class OrchestratorGraph:
    """Backward-compatible wrapper for older callers that expect to
    instantiate an orchestrator class. This provides an `invoke` method
    that delegates to the compiled `workflow` object exported above.
    """

    def __init__(self):
        self._workflow = workflow

    def invoke(self, *args, **kwargs):
        return self._workflow.invoke(*args, **kwargs)


# Preserve the ready-to-run compiled workflow as `workflow` and also expose it
# under a conservative name for callers that expect an instance-like object.
Orchestrator = workflow