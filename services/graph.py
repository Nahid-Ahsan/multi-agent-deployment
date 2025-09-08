from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from typing import Annotated
from .agents import router_agent, search_agent, math_agent, routing_logic

class State(TypedDict):
    messages: Annotated[list, "add_messages"]
    answer: str

def build_graph():
    graph = StateGraph(State)
    graph.add_node("router_agent", router_agent)
    graph.add_node("search_agent", search_agent)
    graph.add_node("math_agent", math_agent)

    graph.add_edge(START, "router_agent")
    graph.add_conditional_edges("router_agent", routing_logic, {
        "math_agent": "math_agent",
        "search_agent": "search_agent"
    })

    graph.add_edge("search_agent", END)
    graph.add_edge("math_agent", END)

    return graph.compile()
