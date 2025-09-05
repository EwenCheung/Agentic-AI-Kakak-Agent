from strands import Agent, tool
from strands.models import BedrockModel
from strands_tools import current_time
import threading

from ...config.settings import settings
from .scheduler_system_prompt import SCHEDULER_SYSTEM_PROMPT
from .tools.calendar_tools import (
    check_availability,
    schedule_event,
    get_empty_slots,
    cancel_event,
    list_events,
    update_event,
    search_events,
    list_calendars,
    get_event_details,
)

class SchedulerAssistant:
    def __init__(self):
        self.lock = threading.Lock()

    @tool
    def __call__(self, query: str) -> str:
        """Scheduler assistant with Google Calendar integration."""
        with self.lock:
            from datetime import datetime, timedelta

            today = datetime.utcnow().date()
            system_with_context = f"""{SCHEDULER_SYSTEM_PROMPT}

CURRENT DATE CONTEXT (hidden from user-facing replies):
- Today: {today.isoformat()} ({today.strftime('%A')})
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
                    update_event,
                    search_events,
                    list_calendars,
                    get_event_details,
                ],
            )
            return agent(query)

scheduler_assistant = SchedulerAssistant()

