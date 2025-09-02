from fastapi import FastAPI, Request
import logging

from .api.routes import router as api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Kakak Agent API")

# Include all API routes (adds /chat_agent, /chat_agent_by_phone, etc.)
app.include_router(api_router)

@app.get("/")
async def root(request: Request):
    return {"message": "Kakak Agent API is running"}