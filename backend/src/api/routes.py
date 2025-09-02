"""
API routes for Kakak Agent
Handles incoming messages from various channels and manages agent interactions
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, Callable

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from ..agent.orchestrator_agent.orchestrator_agent import orchestrator_assistant
from ..agent.chat_agent.chat_agent import chat_assistant
from ..agent.daily_digest_agent.daily_digest_agent import daily_digest_assistant
from ..agent.scheduler_agent.scheduler_agent import scheduler_assistant
from ..agent.ticketing_agent.ticketing_agent import ticketing_assistant


class ChatAgentRequest(BaseModel):
    message: str = Field(..., description="Orchestrator instruction (NOT raw customer text). E.g. 'Send a friendly confirmation asking for their order number.'")
    host_company: str = Field(..., description="The name of the host company")
    tone_and_manner: str = Field(..., description="The tone and manner for responses")
    chat_id: Optional[str] = Field(None, description="Telegram chat ID if instruction involves a specific conversation or sending a message. Omit for aggregate analytics or internal tasks.")
    company_config: Optional[Dict] = Field(None, description="Company configuration settings")
    execute_plan: Optional[bool] = Field(None, description="(Deprecated) Ignored. Tool plans are always auto-executed now.")
    iterative: Optional[bool] = Field(False, description="If true, run iterative plan->execute cycles.")
    cycles: Optional[int] = Field(3, description="Max cycles when iterative=true.")


class ChatAgentByPhoneRequest(BaseModel):
    message: str = Field(..., description="Orchestrator instruction (will resolve phone->chat_id).")
    host_company: str = Field(..., description="The name of the host company")
    tone_and_manner: str = Field(..., description="The tone and manner for responses")
    phone_number: str = Field(..., description="Customer's phone number with country code (e.g., '+6585505541')")
    company_config: Optional[Dict] = Field(None, description="Company configuration settings")


class AgentResponse(BaseModel):
    success: bool
    response: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat_agent")
async def handle_chat_agent(request: ChatAgentRequest):
    """Return agent plan + executions. If iterative flag set, run iterative loop."""
    return chat_assistant(
        query=request.message,
        host_company=request.host_company,
        tone_and_manner=request.tone_and_manner,
        configuration=request.company_config,
    )

@router.post("/daily_digest")
async def handle_daily_digest(message):
    daily_digest_assistant(message)
    return {"response": "Message processed"}

@router.post("/orchestrator_agent")
async def handle_orchestrator_agent(message):
    orchestrator_assistant.invoke(message)
    return {"response": "Message processed"}

@router.post("/scheduler_agent")
async def handle_scheduler_agent(message):
    scheduler_assistant.invoke(message)
    return {"response": "Message processed"}

@router.post("/ticketing_agent")
async def handle_ticketing_agent(message):
    ticketing_assistant.invoke(message)
    return {"response": "Message processed"}