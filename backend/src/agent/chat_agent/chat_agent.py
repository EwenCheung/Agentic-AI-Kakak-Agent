from strands import Agent, tool

from strands.models import BedrockModel

from ...config.settings import settings
from .chat_system_prompt import CHAT_SYSTEM_PROMPT
from .tools.chat_tools import search_knowledge_base, retrieve_conversation_history



@tool
def chat_assistant(query: str, company_name: str, tone_and_manner: str, phone_number: str) -> str:
    """
    A chat assistant that can answer questions and escalate to other agents.

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

    formatted_prompt = CHAT_SYSTEM_PROMPT.format(
        company_name=company_name,
        tone_and_manner=tone_and_manner
    )

    chat_agent = Agent(
        model=model,
        system_prompt=formatted_prompt,
        tools=[search_knowledge_base, retrieve_conversation_history],
    )


    response = chat_agent(query)
    return response