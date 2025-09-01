from strands import Agent, tool

from strands.models import BedrockModel
from strands_tools import current_time

from ...config.settings import settings
from ..orchestrator_agent.orchestrator_system_prompt import ORCHESTRATOR_SYSTEM_PROMPT
from ..chat_agent.chat_agent import chat_assistant
from ..daily_digest_agent.daily_digest_agent import daily_digest_assistant
from ..scheduler_agent.scheduler_agent import scheduler_assistant
from ..ticketing_agent.ticketing_agent import ticketing_assistant


@tool
def orchestrator_assistant(query: str, company_name: str, tone_and_manner: str, phone_number: str) -> str:
    """
    An orchestrator assistant that delegates tasks to other agents.

    Args:
        query (str): The user's query.
        company_name (str): The name of the company.
        tone_and_manner (str): The tone and manner to use in the response.
        phone_number (str): The phone number of the user.

    Returns:
        str: The agent's response.
    """

    model = BedrockModel(
        model_id=settings.BEDROCK_MODEL_ID,
        boto_session=settings.SESSION,
    )
    orchestrator_agent = Agent(
        model=model,
        system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
        tools = [current_time, chat_assistant, daily_digest_assistant, scheduler_assistant, ticketing_assistant]
    )


    response = orchestrator_agent(query)
    return response