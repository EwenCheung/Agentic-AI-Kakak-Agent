from strands import Agent, tool

from strands.models import BedrockModel
from strands_tools import current_time

from ...config.settings import settings
from ..scheduler_agent.scheduler_system_prompt import SCHEDULER_SYSTEM_PROMPT
from .tools.calendar_tools import check_availability, schedule_event, get_empty_slots, cancel_event, list_events, update_event

@tool
def scheduler_assistant(query: str) -> str:
    """
    A scheduler assistant that can manage calendar events.

    Args:
        query (str): The user's query.

    Returns:
        str: The agent's response.
    """

    model = BedrockModel(
        model_id=settings.BEDROCK_MODEL_ID,
        boto_session=settings.SESSION,
    )
    scheduler_agent = Agent(
        model=model,
        system_prompt=SCHEDULER_SYSTEM_PROMPT,
        tools=[current_time, check_availability, schedule_event, get_empty_slots, cancel_event, list_events, update_event],
    )


    response = scheduler_agent(query)
    return response
