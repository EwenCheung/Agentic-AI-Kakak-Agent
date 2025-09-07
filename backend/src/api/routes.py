"""
API routes for Kakak Agent
Handles incoming messages from various channels and manages agent interactions
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, List

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..agent.orchestrator_agent.orchestrator_agent import orchestrator_assistant
from ..agent.chat_agent.chat_agent import chat_assistant
from ..agent.daily_digest_agent.daily_digest_agent import daily_digest_assistant
from ..agent.scheduler_agent.scheduler_agent import scheduler_assistant
from ..agent.ticketing_agent.ticketing_agent import ticketing_assistant
from ..services.calendar_client import get_calendar_status, get_calendar_client
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


from ..database.models import get_db, Ticket, Customer, IncomingMessage
from ..services.summarization_service import summarization_service


@router.post("/telegram_webhook")
async def telegram_webhook(update: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Receives updates from Telegram webhook and stores them in the database queue.
    """
    print("Received Telegram update:", update)
    
    # Convert payload to string to store in DB
    payload_str = json.dumps(update)
    
    # Create a new message queue entry
    new_message = IncomingMessage(payload=payload_str, status='new')
    db.add(new_message)
    db.commit()
    
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
    digest_raw = await daily_digest_assistant(
        query="Provide a summary of today's events, open tickets, and important information using tools and your knowledge in a buisness view."
    )
    
    # Extract the concise summary from the orchestrator's verbose output
    # Look for "Daily Digest Agent Response: " and take the text after it.
    # If not found, return the raw digest.
    summary_prefix = "Daily Digest Agent Response: "
    if summary_prefix in digest_raw:
        digest_summary = digest_raw.split(summary_prefix, 1)[1].strip()
    else:
        digest_summary = digest_raw.strip() # Fallback to raw if prefix not found

    return {"summarise_digest": digest_summary}

@router.get("/upcoming_events")
async def get_upcoming_events():
    """
    Retrieves upcoming calendar events from the calendar service for the next 7 days.
    """
    try:
        calendar_client = get_calendar_client()
        today = datetime.now()
        one_week_from_now = today + timedelta(days=7)
        
        # Format dates as 'YYYY-MM-DD' strings for the list_events method
        start_date_str = today.strftime("%Y-%m-%d")
        end_date_str = one_week_from_now.strftime("%Y-%m-%d")

        events_str = calendar_client.list_events(start_date_str, end_date_str)
        
        # The list_events method returns a string representation of the events.
        # We need to parse it back into a Python object if it's a valid JSON string.
        # If it's "No upcoming events found." or an error message, return it as is.
        if events_str.startswith("[") and events_str.endswith("]"):
            try:
                events = json.loads(events_str)
                return {"events": events}
            except json.JSONDecodeError:
                return {"message": "Failed to parse events from calendar service.", "raw_response": events_str}
        else:
            return {"message": events_str} # This will handle "No upcoming events found." or error messages
    except Exception as e:
        logger.error(f"Error retrieving upcoming events: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving upcoming events: {e}")


@router.get("/healthz")
async def healthz():
    return {"status": "ok"}


@router.get("/readyz")
async def readyz():
    calendar = get_calendar_status()
    return {"status": "ok" if calendar.get("configured") else "degraded", "calendar": calendar}
