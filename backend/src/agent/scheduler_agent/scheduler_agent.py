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
    
    # Get current date and inject it into the query
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_day = datetime.now().strftime("%A")
    
    # Add current date context to the user's query
    enhanced_query = f"""Today's date: {current_date} ({current_day})

User query: {query}

Please use today's date ({current_date}) as the reference point for all relative dates like 'today', 'tomorrow', 'yesterday', etc."""

    model = BedrockModel(
        model_id=settings.BEDROCK_MODEL_ID,
        boto_session=settings.SESSION,
    )
    scheduler_agent = Agent(
        model=model,
        system_prompt=SCHEDULER_SYSTEM_PROMPT,
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

    response = scheduler_agent(enhanced_query)
    return response
