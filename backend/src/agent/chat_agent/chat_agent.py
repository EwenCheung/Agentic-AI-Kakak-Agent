from strands import Agent, tool
from strands.models import BedrockModel
import json
from typing import Optional, Dict, Any, List
import asyncio
import textwrap


from ...config.settings import settings
from .chat_system_prompt import CHAT_SYSTEM_PROMPT
from .tools.telegram_tools import send_message
from .tools.summarization_tools import summarize_customer_conversation


@tool
async def chat_assistant(
    query: str,
    chat_id: int,
    host_company: str = "Company A",
    tone_and_manner: str = "Friendly and Professional",
    configuration: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execution agent for orchestrator instructions (NOT direct end-user freeform input).

    Returns normalized JSON plan; optionally executes planned tool calls and attaches results.
    """

    model = BedrockModel(
        model_id=settings.BEDROCK_MODEL_ID,
        boto_session=settings.SESSION,
    )

    # Avoid Python str.format consuming JSON braces in the prompt by doing simple placeholder replacement
    formatted_prompt = (
        CHAT_SYSTEM_PROMPT
        .replace("{host_company}", host_company)
        .replace("{tone_and_manner}", tone_and_manner)
    )

    print("formatted_prompt", formatted_prompt)

    tools = [
        send_message,
        summarize_customer_conversation
    ]

    chat_agent = Agent(
        model=model,
        system_prompt=formatted_prompt,
        tools=tools,
    )

    # Build orchestrator context block
    context_parts = [
        f"INSTRUCTION: {query}",
        f"CUSTOMER_CHAT_ID: {chat_id}"
    ]

    orchestrator_context = "\n".join(context_parts)
    print("orchestrator_context", orchestrator_context)
    raw_response = await chat_agent.invoke_async(orchestrator_context)
    return raw_response