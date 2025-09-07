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
async def orchestrator_assistant(query: str) -> str:
    """
    An orchestrator assistant that delegates tasks to other agents.

    Args:
        query (str): The user's query, which includes context like company name and tone.

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
        tools = [
            current_time, 
            chat_assistant, 
            scheduler_assistant, 
            ticketing_assistant
            ]
    )


    result = await orchestrator_agent.invoke_async(query)

    # The result is an AgentResult object, extract the final response text.
    response = str(result) # Reverted to str(result)
    return response

