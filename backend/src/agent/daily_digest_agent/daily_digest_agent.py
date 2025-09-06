from strands import Agent, tool

from strands.models import BedrockModel
from strands_tools import current_time

from ...config.settings import settings
from ..daily_digest_agent.daily_digest_system_prompt import DAILY_DIGEST_SYSTEM_PROMPT
from .tools.daily_digest_tools import get_open_tickets_summary, get_recent_high_priority_communications

@tool
def daily_digest_assistant(query: str) -> str:
    """
    A daily digest assistant that can provide a summary of the day's events.

    Args:
        query (str): The user's query.

    Returns:
        str: The agent's response.
    """
    model = BedrockModel(
        model_id=settings.BEDROCK_MODEL_ID,
        boto_session=settings.SESSION,
    )

    daily_digest_agent = Agent(
        model=model,
        system_prompt=DAILY_DIGEST_SYSTEM_PROMPT,
        tools=[current_time, get_open_tickets_summary, get_recent_high_priority_communications
],
    )

    response = daily_digest_agent(query)
    return response