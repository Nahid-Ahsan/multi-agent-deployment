from fastapi import APIRouter, HTTPException
from schemas.schema import QueryRequest
from services.graph import build_graph

router = APIRouter()
agents = build_graph()

@router.post("/multi-agents")
async def handle_query(request: QueryRequest):
    try:
        result = agents.invoke({"messages": [request.query], "answer": ""})
        return {"answer": result["answer"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
