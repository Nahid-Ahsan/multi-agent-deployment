from fastapi import APIRouter, HTTPException
from schemas.schema import QueryRequest
from services.graph import build_graph
import asyncio


router = APIRouter()
agents = build_graph()

@router.post("/multi-agents")
async def handle_query(request: QueryRequest):
    try:
        result = agents.invoke({"messages": [request.query], "answer": ""})
        return {"answer": result["answer"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
from aiocache import Cache
cache = Cache(Cache.MEMORY)

@router.post("/cache-multi-agents")
async def handle_query(request: QueryRequest):
    key = f"multi_agents:{request.query.strip().lower()}"
    try:
        cached = await cache.get(key)
        if cached:
            return {"answer": cached, "cached": True}

        result = agents.invoke({"messages": [request.query], "answer": ""})
        answer = result["answer"]

        await cache.set(key, answer, ttl=300)  # cache for 5 minutes
        return {"answer": answer, "cached": False}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))