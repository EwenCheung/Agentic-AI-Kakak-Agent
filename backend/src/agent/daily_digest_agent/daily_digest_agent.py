from strands import Agent, tool

from strands.models import BedrockModel

from ...config.settings import settings
from ..daily_digest_agent.daily_digest_system_prompt import DAILY_DIGEST_SYSTEM_PROMPT
from .tools.daily_digest_tools import get_open_tickets_summary, get_upcoming_events

@tool
async def daily_digest_assistant(query: str) -> str:
    """
    A daily digest assistant that can provide a concise summary of the day's important events and information.

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
        tools=[get_open_tickets_summary, get_upcoming_events
],
    )

    response = await daily_digest_agent.invoke_async(query) # Changed to await invoke_async
    print(f"Daily Digest Agent Response: {response}") # Added for debugging
    return str(response)