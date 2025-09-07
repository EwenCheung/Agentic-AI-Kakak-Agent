from strands import Agent, tool
from strands.models import BedrockModel
from strands_tools import current_time
from datetime import datetime

from ...config.settings import settings
from .scheduler_system_prompt import SCHEDULER_SYSTEM_PROMPT
from .tools.calendar_tools import (
    check_availability,
    schedule_event,
    get_empty_slots,
    cancel_event,
    list_events,
    get_event_details,
    update_event,
    search_events,
    list_calendars
)

@tool
def scheduler_assistant(query: str) -> str:
    """Scheduler assistant with Google Calendar integration."""
    from datetime import datetime, timedelta

    today = datetime.utcnow().date()
    system_with_context = f"""{SCHEDULER_SYSTEM_PROMPT}

CURRENT DATE CONTEXT (hidden from user-facing replies):
- Today: {today.isoformat()} ({today.strftime('%A')})
- We are at GMT+8
- Use this for interpreting relative dates (today / tomorrow / yesterday).
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
            current_time,
            check_availability,
            schedule_event,
            get_empty_slots,
            cancel_event,
            list_events,
            get_event_details,
            update_event,
            search_events,
            list_calendars
        ],
    )
    return agent(query)
