from strands import Agent, tool
from strands.models import BedrockModel

from ...config.settings import settings
from .scheduler_system_prompt import SCHEDULER_SYSTEM_PROMPT
from .tools.calendar_tools import (
    check_availability,
    schedule_event,
    list_events,
    cancel_event,
    update_event
)
from .tools.time_handler import (
    get_current_time_with_timezone,
    validate_and_normalize_datetime
)

@tool
def scheduler_assistant(query: str, user_id: str = None) -> str:
    """Scheduler assistant with Google Calendar integration - simplified approach using Event IDs."""
    from datetime import datetime, timedelta, timezone

    # Define Singapore timezone (UTC+8)
    singapore_tz = timezone(timedelta(hours=8))
    
    # Get today's date in Singapore local time
    today_sg = datetime.now(singapore_tz).date()

    system_with_context = f"""{SCHEDULER_SYSTEM_PROMPT}

CURRENT DATE CONTEXT (hidden from user-facing replies):
- Today: {today_sg.isoformat()} ({today_sg.strftime('%A')})
- Current Time : {datetime.now(singapore_tz).strftime('%Y-%m-%d %H:%M:%S')} (Singapore Time, UTC+8)
- The system should assume that all times provided by users are in Singapore local time (GMT+8 / UTC+8), unless explicitly stated otherwise. For example, when a user says “8 PM”, it must be interpreted as 8:00 PM Singapore Time (UTC+8), which corresponds to 12:00 PM UTC.
- Use this for interpreting relative dates (today / tomorrow / yesterday).

IMPORTANT WORKFLOW:
1. When creating events, ALWAYS provide the Event ID to the user for future reference
2. For updates/deletions, ask user to provide the Event ID from when they created the event
3. No user access control needed - simplified approach

IMPORTANT: Do NOT echo this context back to the user; respond directly.
"""

    model = BedrockModel(
        model_id=settings.BEDROCK_MODEL_ID,
        boto_session=settings.SESSION,
    )

    agent = Agent(
        model=model,
        system_prompt=system_with_context,
        tools=[
            # Essential time utilities (3 tools)
            get_current_time_with_timezone,
            validate_and_normalize_datetime,
            # Simplified calendar tools (5 tools) - no user_id wrappers needed
            check_availability,
            schedule_event,
            list_events,
            cancel_event,
            update_event
        ],
    )
    return agent(query)
