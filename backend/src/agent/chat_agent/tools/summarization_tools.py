from strands import tool
from ....services.summarization_service import summarization_service

@tool
def summarize_customer_conversation(customer_id: int) -> str:
    """
    Summarizes the conversation history for a given customer and updates their record.

    Args:
        customer_id (int): The ID of the customer whose conversation needs to be summarized.

    Returns:
        str: The generated summary or an error message.
    """
    return summarization_service.summarize_and_update_customer_conversation(customer_id)