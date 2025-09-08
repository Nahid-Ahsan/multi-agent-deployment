from langgraph.prebuilt import create_react_agent
from .tools import web_search, math_solver
from .model import llm


def search_agent(state):
    agent = create_react_agent(llm, [web_search])
    result = agent.invoke({"messages": state["messages"]})
    state["answer"] = result["messages"][-1].content
    return state

def math_agent(state):
    agent = create_react_agent(llm, [math_solver])
    result = agent.invoke({"messages": state["messages"]})
    state["answer"] = result["messages"][-1].content
    return state

def router_agent(state):
    return state

agent_docs = {
    "search_agent": search_agent.__doc__,
    "math_agent": math_agent.__doc__,
}

def routing_logic(state):
    prompt = f"""
    You are a router agent. Choose the best agent for the query: {state['messages'][0]}

    Available agents:
    - math_agent: Solves math problems using the math_solver tool.
    - search_agent: Processes queries requiring web search using a ReAct-style agent.

    Respond with only the agent name.
    """
    response = llm.invoke(prompt)
    decision = response.content.strip().lower()
    return "math_agent" if "math" in decision or any(c in state["messages"][0] for c in "+-*/=") else "search_agent"
