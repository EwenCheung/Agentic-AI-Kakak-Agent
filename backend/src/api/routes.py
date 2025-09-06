"""
API routes for Kakak Agent
Handles incoming messages from various channels and manages agent interactions
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..agent.orchestrator_agent.orchestrator_agent import orchestrator_assistant
from ..agent.chat_agent.chat_agent import chat_assistant
from ..agent.daily_digest_agent.daily_digest_agent import daily_digest_assistant
from ..agent.scheduler_agent.scheduler_agent import scheduler_assistant
from ..agent.ticketing_agent.ticketing_agent import ticketing_assistant
from ..services.calendar_client import get_calendar_status
from ..database.models import get_db, Ticket, Customer


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

class AgentQueryRequest(BaseModel):
    query: str = Field(..., description="The query string for the agent.")

class AgentResponse(BaseModel):
    success: bool
    response: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat_agent")
async def handle_chat_agent(request: ChatAgentRequest):
    """Return agent plan + executions. If iterative flag set, run iterative loop.
    {
    "message":"Send message saying hi",
    "chat_id":"7734986853",
    "host_company": "Company A",
    "tone_and_manner": "Friendly and Professional"
    }
    """
    if not request.chat_id:
        raise HTTPException(status_code=400, detail="chat_id is a required field.")

    return chat_assistant(
        query=request.message,
        chat_id=int(request.chat_id),
        host_company=request.host_company,
        tone_and_manner=request.tone_and_manner,
    )

@router.post("/daily_digest")
async def handle_daily_digest(request: AgentQueryRequest):
    response = daily_digest_assistant(query=request.query)
    return {"response": response}

@router.post("/orchestrator_agent")
async def handle_orchestrator_agent(request: ChatAgentByPhoneRequest):
    response = orchestrator_assistant(
        query=request.message,
        company_name=request.host_company,
        tone_and_manner=request.tone_and_manner,
        phone_number=request.phone_number
    )
    return {"response": response}

class SchedulerAgentRequest(BaseModel):
    query: str = Field(..., description="Natural language scheduling request")


@router.post("/scheduler_agent")
async def handle_scheduler_agent(request: SchedulerAgentRequest):
    try:
        result = scheduler_assistant(query=request.query)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ticketing_agent")
async def handle_ticketing_agent(request: AgentQueryRequest):
    result = ticketing_assistant(query=request.query)
    return {"response": result}


from ..services.summarization_service import summarization_service


@router.post("/telegram_webhook")
async def telegram_webhook(update: Dict[str, Any], background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Receives updates from Telegram webhook, parses them, and passes to the orchestrator.
    """
    print("Received Telegram update:", update)

    if "message" not in update or "text" not in update["message"]:
        return {"status": "ok"}

    message = update["message"]
    chat_id = message["chat"]["id"]
    text = message["text"]
    first_name = message["from"].get("first_name", "User")
    message_time = datetime.fromtimestamp(message["date"]).strftime('%Y-%m-%d %H:%M:%S')

    # 1. Get or create customer
    customer = db.query(Customer).filter(Customer.telegram_chat_id == str(chat_id)).first()
    if not customer:
        customer = Customer(telegram_chat_id=str(chat_id), name=first_name)
        db.add(customer)
        db.commit()
        db.refresh(customer)

    # 2. Append new message to conversation history
    new_history_entry = f"[{first_name} at {message_time}]: {text}\n"
    if customer.conversation_history:
        customer.conversation_history += new_history_entry
    else:
        customer.conversation_history = new_history_entry
    db.commit()

    # 3. Construct the full context for the orchestrator
    orchestrator_query = f"""A new message has been received from a customer.

## Customer Details:
- Name: {customer.name}
- Telegram Chat ID: {customer.telegram_chat_id}

## Conversation Summary:
{customer.conversation_summary or 'No summary yet.'}

## Recent Conversation History:
{customer.conversation_history}

Please analyze the full context and the latest message to determine the appropriate next action."""

    # 4. Trigger orchestrator in the background
    background_tasks.add_task(
        orchestrator_assistant,
        query=orchestrator_query
    )

    # 5. Check for and trigger summarization if history is long
    if customer.conversation_history and len(customer.conversation_history) > 4000:
        background_tasks.add_task(summarization_service.summarize_and_update_customer_conversation, customer.id)

    return {"status": "ok"}



@router.get("/dashboard/tickets/open", response_model=List[Dict])
async def get_open_tickets(db: Session = Depends(get_db)):
    """
    Retrieves a list of all open tickets for the dashboard.
    """
    open_tickets = db.query(Ticket).filter(Ticket.status == "open").all()
    return [
        {
            "id": ticket.id,
            "issue": ticket.issue,
            "priority": ticket.priority,
            "status": ticket.status,
            "created_at": ticket.created_at.isoformat(),
            "updated_at": ticket.updated_at.isoformat(),
            "assigned_to": ticket.assigned_to,
        }
        for ticket in open_tickets
    ]


@router.get("/dashboard/customers/summaries", response_model=List[Dict])
async def get_customer_summaries(db: Session = Depends(get_db)):
    """
    Retrieves a list of all customers with their conversation summaries for the dashboard.
    """
    customers = db.query(Customer).all()
    return [
        {
            "id": customer.id,
            "telegram_chat_id": customer.telegram_chat_id,
            "name": customer.name,
            "company_id": customer.company_id,
            "conversation_summary": customer.conversation_summary,
            "created_at": customer.created_at.isoformat(),
            "updated_at": customer.updated_at.isoformat(),
        }
        for customer in customers
    ]

@router.get("/dashboard/daily_digest")
async def get_daily_digest(db: Session = Depends(get_db)):
    """
    Retrieves a daily digest summary
    """
    digest = orchestrator_assistant(
        query="Provide a summary of today's events, open tickets, and important information using daily_digest agent and your knowledge.."
    )
    return {"summarise_digest": digest}


@router.get("/healthz")
async def healthz():
    return {"status": "ok"}


@router.get("/readyz")
async def readyz():
    calendar = get_calendar_status()
    return {"status": "ok" if calendar.get("configured") else "degraded", "calendar": calendar}
