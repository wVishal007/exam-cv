# from nodes import analyze,conditional_node,rewrite
from .nodes import conditional_node,analyze,rewrite
from .agent_states import agentState
from langgraph.graph import StateGraph,START,END

graph = StateGraph(agentState)

graph.add_node("analyze",analyze)
graph.add_node("rewrite",rewrite)

graph.add_edge(START,"analyze")
graph.add_conditional_edges("analyze",conditional_node,{
    "end":END,
    "rewrite":"rewrite"
})
graph.add_edge("rewrite",END)

workflow = graph.compile()


