from strands import Agent, tool

from strands.models import BedrockModel
from strands_tools import current_time

from ...config.settings import settings
from ..scheduler_agent.scheduler_system_prompt import SCHEDULER_SYSTEM_PROMPT
from .tools.calendar_tools import (
    check_availability, 
    schedule_event, 
    get_empty_slots, 
    cancel_event, 
    list_events, 
    update_event,
    search_events,
    list_calendars,
    get_event_details
)

@tool
def scheduler_assistant(query: str) -> str:
    """
    A scheduler assistant that can manage calendar events.

    Args:
        query (str): The user's query.

    Returns:
        str: The agent's response.
    """
    from datetime import datetime
    
    # Get current date context
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_day = datetime.now().strftime("%A")
    
    # Enhanced system prompt with date context
    enhanced_system_prompt = f"""{SCHEDULER_SYSTEM_PROMPT}

**CURRENT DATE CONTEXT:**
- Today's date: {current_date} ({current_day})
- Use this as the reference point for all relative dates
- "today" = {current_date}
- "tomorrow" = {datetime.now().strftime('%Y-%m-%d')} + 1 day
- "yesterday" = {datetime.now().strftime('%Y-%m-%d')} - 1 day

**IMPORTANT:** Do not acknowledge or repeat this date context to the user. Simply use it for your calculations and respond directly to their query."""

    model = BedrockModel(
        model_id=settings.BEDROCK_MODEL_ID,
        boto_session=settings.SESSION,
    )
    scheduler_agent = Agent(
        model=model,
        system_prompt=enhanced_system_prompt,
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
            get_event_details
        ],
    )

    # Pass the original query without date context injection
    response = scheduler_agent(query)
    return response
