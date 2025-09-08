from langchain_core.tools import tool
from langchain_tavily import TavilySearch
import os
from .model import llm

tavily_api_key = os.getenv("TAVILY_API_KEY")

@tool
def web_search(query: str) -> str:
    """
    Perform a real-time web search using the Tavily API.
    
    Args:
        query (str): Search term or question.

    Returns:
        str: Summarized results or error message.
    """
    try:
        search = TavilySearch(max_results=3, tavily_api_key=tavily_api_key)
        results = search.invoke(query)
        formatted_results = "\n".join([f"- {r['title']}: {r['content'][:200]}..." for r in results])
        return formatted_results if results else "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"

@tool
def math_solver(expression: str) -> str:
    """
    Solve a math expression or problem. If it's arithmetic, use eval; otherwise, ask the LLM.

    Args:
        expression (str): A math problem or expression.

    Returns:
        str: Solution or error message.
    """
    try:
        if all(c in "0123456789.+-*/() " for c in expression):
            result = eval(expression, {"__builtins__": {}}, {})
            return str(result)
        else:
            prompt = f"Solve the following math problem and return only the final answer: {expression}"
            response = llm.invoke(prompt)
            return response.content.strip()
    except Exception as e:
        return f"Math error: {str(e)}"
