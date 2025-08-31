from strands import tool


@tool
def delegate_task(agent_name: str, task: str) -> str:
    """
    Delegates a task to a specialist agent.

    Args:
        agent_name (str): The name of the agent to delegate the task to.
        task (str): The task to be delegated.

    Returns:
        str: The result from the specialist agent.
    """
    # In a real implementation, this would trigger the specified agent.
    return f"Task '{task}' delegated to {agent_name}. Result: [Agent Result]"


@tool
def send_user_response(message: str) -> str:
    """
    Sends a response to the user.

    Args:
        message (str): The message to send to the user.

    Returns:
        str: A confirmation that the message was sent.
    """
    # In a real implementation, this would send the message through the appropriate channel (e.g., WhatsApp).
    return f"Message sent to user: {message}"
