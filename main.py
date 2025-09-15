from fastapi import FastAPI
from endpoints.endpoint import router as query_router
import uvicorn
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # show INFO level logs
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# Optional: get a named logger for your app
logger = logging.getLogger("multi_agents_app")

app = FastAPI(title="Multi-Agents API")
app.include_router(query_router)

if __name__ == "__main__":
    import os
    # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    workers = int(os.getenv("API_WORKERS", os.cpu_count()))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=workers,
        log_config=None
    )
