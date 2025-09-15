from langchain_core.tools import tool
from langchain_tavily import TavilySearch
import os
from .model import llm
from .config import TAVILY_API_KEY

tavily_api_key = TAVILY_API_KEY

# @tool
# def web_search(query: str) -> str:
#     """
#     Perform a real-time web search using the Tavily API.
    
#     Args:
#         query (str): Search term or question.

#     Returns:
#         str: Summarized results or error message.
#     """
#     try:
#         search = TavilySearch(max_results=3, tavily_api_key=tavily_api_key)
#         results = search.invoke(query)
#         formatted_results = "\n".join([f"- {r['title']}: {r['content'][:200]}..." for r in results])
#         return formatted_results if results else "No results found."
#     except Exception as e:
#         return f"Search error: {str(e)}"

# @tool
# def math_solver(expression: str) -> str:
#     """
#     Solve a math expression or problem. If it's arithmetic, use eval; otherwise, ask the LLM.

#     Args:
#         expression (str): A math problem or expression.

#     Returns:
#         str: Solution or error message.
#     """
#     try:
#         if all(c in "0123456789.+-*/() " for c in expression):
#             result = eval(expression, {"__builtins__": {}}, {})
#             return str(result)
#         else:
#             prompt = f"Solve the following math problem and return only the final answer: {expression}"
#             response = llm.invoke(prompt)
#             return response.content.strip()
#     except Exception as e:
#         return f"Math error: {str(e)}"


import os
import asyncio
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from aiocache import cached, Cache
import logging

logger = logging.getLogger("multi_agents_app")


# Reuse executors
thread_executor = None
process_executor = ProcessPoolExecutor(max_workers=2)  # tune for CPU tasks

# @cached(ttl=300, cache=Cache.MEMORY)  # cache for 5 minutes
# @tool
# async def web_search(query: str) -> str:
#     """
#     Perform a real-time web search using the Tavily API.
#     (I/O-bound -> run in async threadpool)
#     """
#     global thread_executor
#     if thread_executor is None:
#         from concurrent.futures import ThreadPoolExecutor
#         thread_executor = ThreadPoolExecutor(max_workers=5)

#     loop = asyncio.get_running_loop()
#     try:
#         def search_task():
#             search = TavilySearch(max_results=3, tavily_api_key=tavily_api_key)
#             return search.invoke(query)

#         results = await loop.run_in_executor(thread_executor, search_task)
#         print(f"[web_search] Returning fresh results for query: {query}")
        
#         formatted_results = "\n".join(
#             [f"- {r['title']}: {r['content'][:200]}..." for r in results]
#         )
#         return formatted_results if results else "No results found."
#     except Exception as e:
#         return f"Search error: {str(e)}"


@tool
async def web_search(query: str) -> str:
    """
    Perform a real-time web search using the Tavily API.
    Logs cache hits explicitly.
    """
    cache = Cache.MEMORY
    cached_result = await cache.get(query)
    if cached_result:
        print(f"[web_search] Cache HIT for query: {query}")
        return cached_result
    else:
        print(f"[web_search] Cache MISS for query: {query}")

    global thread_executor
    if thread_executor is None:
        from concurrent.futures import ThreadPoolExecutor
        thread_executor = ThreadPoolExecutor(max_workers=5)

    loop = asyncio.get_running_loop()
    try:
        def search_task():
            search = TavilySearch(max_results=3, tavily_api_key=tavily_api_key)
            return search.invoke(query)

        results = await loop.run_in_executor(thread_executor, search_task)

        formatted_results = "\n".join(
            [f"- {r['title']}: {r['content'][:200]}..." for r in results]
        )
        output = formatted_results if results else "No results found."

        # Save to cache for 5 minutes
        await cache.set(query, output, ttl=300)
        return output

    except Exception as e:
        logger.error(f"[web_search] Error: {str(e)}")
        return f"Search error: {str(e)}"


@tool
async def math_solver(expression: str) -> str:
    """
    Solve a math expression. Arithmetic runs in process pool (CPU),
    otherwise falls back to LLM.
    """
    loop = asyncio.get_running_loop()
    try:
        if all(c in "0123456789.+-*/() " for c in expression):
            # Use LRU cache for CPU-bound math evaluation
            @lru_cache(maxsize=128)
            def eval_task(expr):
                print(f"[math_solver] Computing fresh result for: {expr}")
                return eval(expr, {"__builtins__": {}}, {})

            result = await loop.run_in_executor(process_executor, eval_task, expression)
            return str(result)

        # Otherwise, ask LLM (I/O-bound)
        prompt = f"Solve the following math problem and return only the final answer: {expression}"
        response = await loop.run_in_executor(None, lambda: llm.invoke(prompt))
        return response.content.strip()
    except Exception as e:
        return f"Math error: {str(e)}"


