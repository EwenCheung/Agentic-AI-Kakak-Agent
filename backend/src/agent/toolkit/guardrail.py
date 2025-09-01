from strands import tool


@tool
def check_guardrail(response: str) -> bool:
    """
    Checks if a response is appropriate and within the defined guardrails.

    Args:
        response (str): The response to check.

    Returns:
        bool: True if the response is appropriate, False otherwise.
    """
    # In a real implementation, this would use a more sophisticated method to check the response.
    if "inappropriate" in response.lower():
        return False
    return True
