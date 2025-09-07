from strands import tool
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import logging
import json

from ....services.calendar_client import get_calendar_client
from ....database.models import Ticket, get_db

logger = logging.getLogger(__name__)

@tool
def get_open_tickets_summary() -> str:
    """
    Retrieves a summary of open support tickets from the database.

    Returns:
        str: A summary of open tickets.
    """
    db: Session = next(get_db())
    open_tickets = db.query(Ticket).filter(Ticket.status == 'open').all()

    if not open_tickets:
        return "No open tickets found."

    priority_counts = db.query(
        Ticket.priority, func.count(Ticket.id)
    ).filter(
        Ticket.status == 'open'
    ).group_by(Ticket.priority).all()

    summary_parts = []
    total_open = len(open_tickets)
    summary_parts.append(f"Total open tickets: {total_open}.")

    for priority, count in priority_counts:
        summary_parts.append(f"{count} {priority} priority tickets.")

    return " ".join(summary_parts)


@tool
def get_recent_high_priority_communications() -> str:
    """
    Retrieves a summary of recent high-priority communications.

    Returns:
        str: A summary of recent high-priority messages.
    """
    db: Session = next(get_db())
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + timedelta(days=1)

    high_priority_tickets_today = db.query(Ticket).filter(
        Ticket.priority == 'high',
        Ticket.created_at >= today_start,
        Ticket.created_at < tomorrow_start
    ).all()

    if not high_priority_tickets_today:
        return "No new high-priority communications today."

    communications_summary = [f"New high-priority ticket (ID: {t.id}): {t.issue}" for t in high_priority_tickets_today]
    return "Recent high-priority communications:\n" + "\n".join(communications_summary)


@tool
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
                # Return a string representation of the events for the agent
                return f"Upcoming Events: {json.dumps(events, indent=2)}"
            except json.JSONDecodeError:
                return "Failed to parse events from calendar service."
        else:
            return events_str # This will handle "No upcoming events found." or error messages
    except Exception as e:
        logger.error(f"Error retrieving upcoming events: {e}")
        return f"Error retrieving upcoming events: {e}"
