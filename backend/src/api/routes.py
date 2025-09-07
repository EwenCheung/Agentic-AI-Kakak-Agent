"""
API routes for Kakak Agent
Handles incoming messages from various channels and manages agent interactions
"""

import asyncio
import logging
import json
import httpx
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, List

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..config.settings import settings
from ..agent.orchestrator_agent.orchestrator_agent import memory_orchestrator
from ..agent.daily_digest_agent.daily_digest_agent import daily_digest_assistant
from ..agent.scheduler_agent.scheduler_agent import scheduler_assistant
from ..agent.ticketing_agent.ticketing_agent import ticketing_assistant
from ..services.calendar_client import get_calendar_status, get_calendar_client
from ..database.models import get_db, Ticket, Customer


class ChatAgentRequest(BaseModel):
    message: str = Field(..., description="Customer message to process")
    telegram_chat_id: Optional[str] = Field(None, description="Telegram chat ID for memory context")
    host_company: Optional[str] = Field("Kakak Agent", description="The name of the host company")
    tone_and_manner: Optional[str] = Field(None, description="The tone and manner for responses")

class MemoryChatRequest(BaseModel):
    message: str = Field(..., description="Customer message")
    chat_id: str = Field(..., description="Chat ID (used as user_id for memory)")

class OrchestratorRequest(BaseModel):
    message: str = Field(..., description="Orchestrator instruction.")
    chat_id: Optional[str] = Field(None, description="Chat ID for memory context")
    host_company: str = Field(..., description="The name of the host company")
    tone_and_manner: Optional[str] = Field(None, description="The tone and manner for responses (optional; will fallback to stored config)")
    company_config: Optional[Dict] = Field(None, description="Company configuration settings")

class AgentQueryRequest(BaseModel):
    query: str = Field(..., description="The query string for the agent.")

class AgentResponse(BaseModel):
    success: bool
    response: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat")
async def chat_endpoint(request: MemoryChatRequest, db: Session = Depends(get_db)):
    """
    Main chat endpoint with Mem0 memory integration using chat_id as user_id.
    Processes customer messages with persistent memory context.
    """
    try:
        # Use chat_id directly as user_id for Mem0 memory
        chat_id = request.chat_id
        
        # Get or create customer record (for business data only, not memory)
        customer = db.query(Customer).filter(Customer.telegram_chat_id == chat_id).first()
        
        if customer:
            customer_id = customer.id
            customer_name = customer.name
        else:
            # Create new customer record
            customer_name = f"User_{chat_id}"
            customer = Customer(
                name=customer_name,
                telegram_chat_id=chat_id
            )
            db.add(customer)
            db.commit()
            db.refresh(customer)
            customer_id = customer.id
            
            # Store initial customer info in memory
            memory_orchestrator.store_user_info(
                chat_id, 
                f"New customer: {customer_name}, chat_id: {chat_id}"
            )
            
            logger.info(f"Created new customer {customer_id} for chat_id {chat_id}")
        
        # Process with memory-aware orchestrator
        response = await memory_orchestrator.process_message(request.message, chat_id)
        
        return {"response": response, "chat_id": chat_id}
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message")


@router.post("/daily_digest")
async def handle_daily_digest(request: AgentQueryRequest):
    response = daily_digest_assistant(query=request.query)
    return {"response": response}

@router.post("/orchestrator_agent")
async def handle_orchestrator_agent(request: OrchestratorRequest):
    try:
        if request.chat_id:
            # Use memory-aware orchestrator
            response = await memory_orchestrator.process_message(request.message, request.chat_id)
        else:
            # Fallback to legacy orchestrator
            tone = request.tone_and_manner or settings.get_tone_and_manner()
            enriched_query = f"Company: {request.host_company}\nTone: {tone}\nInstruction: {request.message}"
            response = await memory_orchestrator.process_message(enriched_query, "legacy_api")
        
        return {"response": response}
    except Exception as e:
        logger.error(f"Orchestrator agent error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process orchestrator request")

# Memory management endpoints
@router.get("/memory/{chat_id}")
async def get_customer_memories(chat_id: str):
    """Get all Mem0 memories for a chat_id."""
    try:
        memories = memory_orchestrator.get_user_memories(chat_id)
        return {"chat_id": chat_id, "memories": memories}
    except Exception as e:
        logger.error(f"Error retrieving memories for {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve memories")

@router.post("/memory/{chat_id}")
async def store_customer_memory(chat_id: str, request: dict):
    """Manually store memory for a chat_id."""
    try:
        content = request.get("content", "")
        if not content:
            raise HTTPException(status_code=400, detail="Content is required")
        
        result = memory_orchestrator.store_user_info(chat_id, content)
        return {"chat_id": chat_id, "result": result}
    except Exception as e:
        logger.error(f"Error storing memory for {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to store memory")

@router.delete("/memory/{chat_id}")
async def clear_customer_memories(chat_id: str):
    """Clear all memories for a chat_id."""
    try:
        # Note: Mem0 doesn't have a direct "clear all" action, so we'll list and delete
        memories = memory_orchestrator.get_user_memories(chat_id)
        if memories.get("memories"):
            # This would need to be implemented based on Mem0's delete capabilities
            logger.info(f"Would clear {len(memories['memories'])} memories for {chat_id}")
        
        return {"chat_id": chat_id, "message": "Memory clear requested"}
    except Exception as e:
        logger.error(f"Error clearing memories for {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear memories")

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
    """Get all open tickets for dashboard display"""
    try:
        tickets = db.query(Ticket).filter(Ticket.status == 'open').order_by(Ticket.created_at.desc()).all()
        
        result = []
        for ticket in tickets:
            result.append({
                "id": ticket.id,
                "issue": ticket.issue,
                "priority": ticket.priority,
                "status": ticket.status,
                "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
                "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching open tickets: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch tickets")


@router.get("/dashboard/tickets/all", response_model=List[Dict])
async def get_all_tickets(db: Session = Depends(get_db)):
    """Get all tickets (both open and closed) for dashboard display"""
    try:
        tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).all()
        
        result = []
        for ticket in tickets:
            result.append({
                "id": ticket.id,
                "issue": ticket.issue,
                "priority": ticket.priority,
                "status": ticket.status,
                "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
                "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching all tickets: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch tickets")


@router.put("/dashboard/tickets/{ticket_id}/toggle-status")
async def toggle_ticket_status(ticket_id: int, db: Session = Depends(get_db)):
    """Toggle ticket status between 'open' and 'closed'"""
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        current_status = ticket.status
        new_status = "closed" if current_status == "open" else "open"
        
        # Update ticket status
        ticket.status = new_status
        ticket.updated_at = datetime.now()
        db.commit()
        db.refresh(ticket)
        
        return {
            "message": f"Ticket status changed from {current_status} to {new_status}",
            "ticket_id": ticket_id,
            "old_status": current_status,
            "new_status": new_status
        }
        
    except Exception as e:
        logger.error(f"Error toggling ticket status {ticket_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to toggle ticket status")


@router.put("/dashboard/tickets/{ticket_id}/close")
async def close_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """
    Closes a ticket by changing its status to 'inactive'.
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket.status = "inactive"
    ticket.updated_at = datetime.now()
    db.commit()
    db.refresh(ticket)
    
    return {
        "message": "Ticket closed successfully",
        "ticket_id": ticket_id,
        "status": ticket.status
    }


@router.delete("/dashboard/tickets/{ticket_id}")
async def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """
    Deletes a ticket from the database.
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    db.delete(ticket)
    db.commit()
    
    return {
        "message": "Ticket deleted successfully",
        "ticket_id": ticket_id
    }


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


# Removed os, load_dotenv, set_key imports
from fastapi import UploadFile, File # Keep UploadFile, File
from sqlalchemy.orm import Session # Keep Session
from fastapi import Depends # Keep Depends

# ... (existing imports)

from ..database.models import get_db, Ticket, Customer, IncomingMessage, get_config_db, EnvConfig, KnowledgeBase # Added KnowledgeBase
"""Knowledge base vectorisation import.
The original code expected functions `process_documents` and `vectorise_knowledge_base_from_db`.
The implementation file now provides `vectorise_knowledge_base_from_db` only.
Import it and alias to the old expected name to avoid refactoring other call sites.
"""
from ..database.data_processing.pdf_vdb import vectorise_knowledge_base_from_db 
import hashlib

from pydantic import BaseModel

class ChannelConfigRequest(BaseModel):
    telegram_bot_id: str
    client_secret_json_content: str

class AgentConfigRequest(BaseModel):
    tone_and_manner: Optional[str] = None

@router.post("/configure_channel")
async def configure_channel(
    request: ChannelConfigRequest,
    db_config: Session = Depends(get_config_db)
):
    """Configure channel integration (requires BOTH bot id and client secret JSON)."""
    # Validate JSON correctness early
    try:
        json.loads(request.client_secret_json_content)
    except Exception:
        raise HTTPException(status_code=400, detail="client_secret_json_content must be valid JSON text")

    try:
        env_config = db_config.query(EnvConfig).first()
        if not env_config:
            env_config = EnvConfig()
            db_config.add(env_config)

        env_config.telegram_bot_token = request.telegram_bot_id
        env_config.client_secret_json = request.client_secret_json_content

        db_config.commit()
        db_config.refresh(env_config)
        
        # Sync in-memory settings for any legacy direct reads (preferred: use getter)
        try:
            settings.TELEGRAM_BOT_TOKEN = env_config.telegram_bot_token
        except Exception:
            pass

        # Set up Telegram webhook
        webhook_url = "https://34a91af0c652.ngrok-free.app/telegram_webhook"
        webhook_success = await setup_telegram_webhook(request.telegram_bot_id, webhook_url)
        
        # Check if Google client secret was provided and trigger OAuth flow
        google_auth_url = None
        if request.client_secret_json_content and request.client_secret_json_content.strip():
            try:
                google_auth_url = await get_google_oauth_url(request.client_secret_json_content)
            except Exception as e:
                logger.error(f"Error creating Google OAuth URL: {e}")
        
        response_data = {
            "message": "Channel configuration saved and webhook configured successfully." if webhook_success else "Channel configuration saved, but webhook setup failed. Please check bot token.",
            "webhook_success": webhook_success
        }
        
        # Include Google OAuth URL if available
        if google_auth_url:
            response_data["google_auth_url"] = google_auth_url
            response_data["google_auth_required"] = True
            response_data["message"] += " Please complete Google Calendar authorization."
        
        return response_data
            
    except Exception as e:
        logger.error(f"Error configuring channel: {e}")
        raise HTTPException(status_code=500, detail=f"Error configuring channel: {e}")


async def setup_telegram_webhook(bot_token: str, webhook_url: str) -> bool:
    """
    Set up Telegram webhook by calling the Telegram Bot API.
    Returns True if successful, False otherwise.
    """
    try:
        telegram_api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        payload = {"url": webhook_url}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(telegram_api_url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    logger.info(f"Telegram webhook set successfully to {webhook_url}")
                    return True
                else:
                    logger.error(f"Telegram API error: {result.get('description', 'Unknown error')}")
                    return False
            else:
                logger.error(f"HTTP error setting webhook: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"Exception setting up Telegram webhook: {e}")
        return False


async def get_google_oauth_url(client_secret_json: str) -> str:
    """
    Generate Google OAuth URL for authorization.
    Returns the authorization URL that frontend can use.
    """
    try:
        from google_auth_oauthlib.flow import Flow
        import tempfile
        
        # Create temporary file for client secret
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            temp_file.write(client_secret_json)
            temp_file_path = temp_file.name
        
        try:
            # Create OAuth flow using OOB (out-of-band) flow
            flow = Flow.from_client_secrets_file(
                temp_file_path,
                scopes=["https://www.googleapis.com/auth/calendar"],
                redirect_uri="urn:ietf:wg:oauth:2.0:oob"  # OOB flow - shows code in browser
            )
            
            auth_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            
            return auth_url
        finally:
            os.remove(temp_file_path)
            
    except Exception as e:
        logger.error(f"Error generating Google OAuth URL: {e}")
        raise e

@router.post("/configure_agent")
async def configure_agent(
    request: AgentConfigRequest,
    db_config: Session = Depends(get_config_db)
):
    """Configure agent behavior (tone & manner). Tone is optional; if omitted existing is retained."""
    try:
        env_config = db_config.query(EnvConfig).first()
        if not env_config:
            env_config = EnvConfig()
            db_config.add(env_config)
        before = env_config.tone_and_manner
        if request.tone_and_manner is not None and request.tone_and_manner.strip() != "":
            env_config.tone_and_manner = request.tone_and_manner.strip()
        logger.info(f"configure_agent tone change: before='{before}' after='{env_config.tone_and_manner}'")

        db_config.commit()
        db_config.refresh(env_config)
        # Synchronize in-memory settings field so any code still (incorrectly) reading
        # settings.TONE_AND_MANNER gets the latest value. Preferred access remains
        # settings.get_tone_and_manner().
        try:
            settings.TONE_AND_MANNER = env_config.tone_and_manner
        except Exception:
            pass
        return {"message": "Agent configuration updated.", "tone_and_manner": env_config.tone_and_manner}
    except Exception as e:
        logger.error(f"Error configuring agent: {e}")
        raise HTTPException(status_code=500, detail=f"Error configuring agent: {e}")


@router.get("/config/current")
async def get_current_config(db_config: Session = Depends(get_config_db)):
    env_config = db_config.query(EnvConfig).first()
    return {
        "telegram_bot_token": env_config.telegram_bot_token if env_config else None,
        "has_client_secret": bool(env_config and env_config.client_secret_json),
        "tone_and_manner": env_config.tone_and_manner if env_config and env_config.tone_and_manner else settings.get_tone_and_manner(),
    }

@router.get("/config/diagnostics")
async def config_diagnostics(db_config: Session = Depends(get_config_db)):
    env_config = db_config.query(EnvConfig).first()
    db_tone = env_config.tone_and_manner if env_config else None
    effective = settings.get_tone_and_manner()
    return {
        "db_tone": db_tone,
        "effective_tone": effective,
        "matches": db_tone == effective,
    }


@router.get("/knowledge_base/documents")
async def list_knowledge_base_documents(db_config: Session = Depends(get_config_db)):
    docs = db_config.query(KnowledgeBase).order_by(KnowledgeBase.id.desc()).all()
    return [
        {
            "id": d.id,
            "file_name": d.file_name,
            "description": d.description,
            "content_type": d.content_type,
            "size_bytes": d.size_bytes,
            "created_at": d.created_at.isoformat() if getattr(d, 'created_at', None) else None,
            "study_status": getattr(d, 'study_status', None),
        }
        for d in docs
    ]

@router.post("/knowledge_base/upload")
async def upload_knowledge_base_documents(
    files: List[UploadFile] = File(..., description="One or more documents"),
    descriptions: Optional[List[str]] = None,
    db_config: Session = Depends(get_config_db)
):
    """Upload multiple knowledge base documents. descriptions list (if provided) aligns by index.

    Adds SHA256 hash to support duplicate detection. If an identical file (same hash) with the
    same name already exists, it will still store again (versioning) unless we choose to skip.
    Currently policy: skip exact duplicates (same hash & name).
    """
    results = []
    try:
        for idx, up in enumerate(files):
            data = await up.read()
            file_hash = hashlib.sha256(data).hexdigest()
            desc = None
            if descriptions and idx < len(descriptions):
                desc = descriptions[idx]

            # Check for existing duplicate
            existing = db_config.query(KnowledgeBase).filter(
                KnowledgeBase.file_name == up.filename,
                KnowledgeBase.file_hash == file_hash,
            ).first()
            if existing:
                results.append({
                    "id": existing.id,
                    "file_name": existing.file_name,
                    "duplicate": True,
                })
                continue

            kb = KnowledgeBase(
                file_name=up.filename,
                description=desc,
                content_type=up.content_type,
                size_bytes=len(data),
                file_content=data,
                file_hash=file_hash,
                study_status='not_studied'
            )
            db_config.add(kb)
            db_config.flush()  # get id without full commit yet
            results.append({"id": kb.id, "file_name": kb.file_name, "duplicate": False, "study_status": kb.study_status})
        db_config.commit()
        return {"message": "Documents processed", "documents": results}
    except Exception as e:
        logger.error(f"Error uploading documents: {e}")
        db_config.rollback()
        raise HTTPException(status_code=500, detail=f"Error uploading documents: {e}")

@router.delete("/knowledge_base/documents/{doc_id}")
async def delete_knowledge_base_document(doc_id: int, db_config: Session = Depends(get_config_db)):
    doc = db_config.query(KnowledgeBase).filter(KnowledgeBase.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    try:
        db_config.delete(doc)
        db_config.commit()
        return {"message": "Document deleted"}
    except Exception as e:
        db_config.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete: {e}")

from fastapi.responses import StreamingResponse
import io

@router.get("/knowledge_base/documents/{doc_id}/download")
async def download_knowledge_base_document(doc_id: int, db_config: Session = Depends(get_config_db)):
    doc = db_config.query(KnowledgeBase).filter(KnowledgeBase.id == doc_id).first()
    if not doc or not doc.file_content:
        raise HTTPException(status_code=404, detail="Document not found")
    return StreamingResponse(
        io.BytesIO(doc.file_content),
        media_type=doc.content_type or 'application/octet-stream',
        headers={"Content-Disposition": f"attachment; filename=\"{doc.file_name}\""}
    )


@router.get("/healthz")
async def healthz():
    return {"status": "ok"}


@router.get("/readyz")
async def readyz():
    calendar = get_calendar_status()
    return {"status": "ok" if calendar.get("configured") else "degraded", "calendar": calendar}

# ---------------- Knowledge Base Vectorization -----------------
_vector_state = {"status": "idle", "processed": [], "error": None}

@router.post("/knowledge_base/vectorise")
async def start_vectorise(background_tasks: BackgroundTasks, recreate: bool = True):
    """Trigger vectorisation of ALL knowledge base documents stored in DB.

    Query param recreate controls whether the existing vector store is fully rebuilt (default True)
    or appended to (recreate=False may duplicate chunks for already processed files).
    """
    if _vector_state["status"] == "running":
        return {"status": "running", "message": "Vectorisation already in progress"}
    _vector_state.update({"status": "running", "processed": [], "error": None, "recreate": recreate})

    def _run():
        try:
            processed = vectorise_knowledge_base_from_db(recreate=recreate)
            _vector_state.update({"status": "completed", "processed": processed})
        except Exception as e:
            _vector_state.update({"status": "error", "error": str(e)})

    background_tasks.add_task(_run)
    return {"status": "running"}

@router.get("/knowledge_base/vectorise/status")
async def vectorise_status():
    return _vector_state


# Google Calendar OAuth endpoints
@router.get("/google/oauth/start")
async def start_google_oauth(db_config: Session = Depends(get_config_db)):
    """Start Google OAuth flow and return authorization URL"""
    try:
        from google_auth_oauthlib.flow import Flow
        import tempfile
        
        # Get client secret from database
        env_config = db_config.query(EnvConfig).first()
        if not env_config or not env_config.client_secret_json:
            raise HTTPException(status_code=400, detail="Google client secret not configured")
        
        # Create temporary file for client secret
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            temp_file.write(env_config.client_secret_json)
            temp_file_path = temp_file.name
        
        try:
            # Create OAuth flow using OOB (out-of-band) flow
            flow = Flow.from_client_secrets_file(
                temp_file_path,
                scopes=["https://www.googleapis.com/auth/calendar"],
                redirect_uri="urn:ietf:wg:oauth:2.0:oob"  # OOB flow - shows code in browser
            )
            
            auth_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            
            return {
                "auth_url": auth_url,
                "state": state,
                "message": "Open this URL in your browser to authorize Google Calendar access"
            }
        finally:
            os.remove(temp_file_path)
            
    except Exception as e:
        logger.error(f"Error starting Google OAuth: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start OAuth: {e}")


class GoogleOAuthCallbackRequest(BaseModel):
    authorization_code: str
    state: str = None

@router.post("/google/oauth/callback")
async def google_oauth_callback(
    request: GoogleOAuthCallbackRequest,
    db_config: Session = Depends(get_config_db)
):
    """Handle OAuth callback and save credentials"""
    try:
        from google_auth_oauthlib.flow import Flow
        import tempfile
        
        # Get client secret from database
        env_config = db_config.query(EnvConfig).first()
        if not env_config or not env_config.client_secret_json:
            raise HTTPException(status_code=400, detail="Google client secret not configured")
        
        # Create temporary file for client secret
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            temp_file.write(env_config.client_secret_json)
            temp_file_path = temp_file.name
        
        try:
            # Create OAuth flow using OOB (out-of-band) flow
            flow = Flow.from_client_secrets_file(
                temp_file_path,
                scopes=["https://www.googleapis.com/auth/calendar"],
                redirect_uri="urn:ietf:wg:oauth:2.0:oob"  # OOB flow - shows code in browser
            )
            
            # Exchange authorization code for credentials
            flow.fetch_token(code=request.authorization_code)
            
            # Save credentials to token.json
            with open("token.json", "w") as token_file:
                token_file.write(flow.credentials.to_json())
            
            return {
                "message": "Google Calendar authorization successful!",
                "status": "authorized"
            }
        finally:
            os.remove(temp_file_path)
            
    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}")
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")


@router.get("/google/calendar/status")
async def google_calendar_status():
    """Check Google Calendar authorization status"""
    try:
        from ..services.calendar_client import get_calendar_status
        status = get_calendar_status()
        
        # Check if token.json exists
        token_exists = os.path.exists("token.json")
        
        return {
            "configured": status.get("configured", False),
            "ready": status.get("ready", False) and token_exists,
            "token_exists": token_exists,
            "reason": status.get("reason", "Unknown")
        }
    except Exception as e:
        logger.error(f"Error checking calendar status: {e}")
        return {
            "configured": False,
            "ready": False,
            "token_exists": False,
            "reason": f"Error: {e}"
        }
