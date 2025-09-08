from strands import Agent, tool

from strands.models import BedrockModel

from ...config.settings import settings
from ..ticketing_agent.ticketing_system_prompt import TICKETING_SYSTEM_PROMPT
from .tools.ticketing_tools import create_ticket, check_ticket_status, update_ticket, close_ticket, list_open_tickets, assign_ticket, escalate_ticket, get_ticket_details, check_for_existing_ticket


@tool
def ticketing_assistant(query: str) -> str:
    """
    A ticketing assistant that can manage support tickets.

    Args:
        query (str): The user's query.

    Returns:
        str: The agent's response.
    """

    model = BedrockModel(
        model_id=settings.BEDROCK_MODEL_ID,
        boto_session=settings.SESSION,
    )
    ticketing_agent = Agent(
        model=model,
        system_prompt=TICKETING_SYSTEM_PROMPT,
        tools = [create_ticket, check_ticket_status, update_ticket, close_ticket, list_open_tickets, assign_ticket, escalate_ticket, get_ticket_details, check_for_existing_ticket]
    )


    response = ticketing_agent(query)
    return response
