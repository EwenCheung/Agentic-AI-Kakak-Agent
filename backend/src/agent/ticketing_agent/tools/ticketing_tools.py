from strands import tool

@tool
def create_ticket(issue: str, priority: str) -> str:
    """
    Create a support ticket with the given issue and priority.

    Args:
        issue (str): The description of the issue.
        priority (str): The priority level of the ticket (e.g., 'low', 'medium', 'high').

    Returns:
        str: Confirmation message with the ticket ID.
    """
    # Here you would integrate with the actual ticketing system API or service
    # For demonstration purposes, we'll just return a mock ticket ID
    ticket_id = "TICKET12345"
    return f"Ticket created with ID: {ticket_id}, Issue: {issue}, Priority: {priority}"

@tool
def check_ticket_status(ticket_id: str) -> str:
    """
    Check the status of a support ticket by its ID.

    Args:
        ticket_id (str): The ID of the ticket to check.

    Returns:
        str: The current status of the ticket.
    """
    # Here you would integrate with the actual ticketing system API or service
    # For demonstration purposes, we'll just return a placeholder status
    status = "In Progress"
    return f"Status of ticket {ticket_id}: {status}"

@tool
def update_ticket(ticket_id: str, update_info: str) -> str:
    """
    Update a support ticket with new information.

    Args:
        ticket_id (str): The ID of the ticket to update.
        update_info (str): The information to update the ticket with.

    Returns:
        str: Confirmation message indicating the status of the update.
    """
    # Here you would integrate with the actual ticketing system API or service
    # For demonstration purposes, we'll just return a confirmation string
    return f"Ticket {ticket_id} updated with info: {update_info}"

@tool
def close_ticket(ticket_id: str) -> str:
    """
    Close a support ticket by its ID.

    Args:
        ticket_id (str): The ID of the ticket to close.

    Returns:
        str: Confirmation message indicating the ticket has been closed.
    """
    # Here you would integrate with the actual ticketing system API or service
    # For demonstration purposes, we'll just return a confirmation string
    return f"Ticket {ticket_id} has been closed."

@tool
def list_open_tickets() -> str:
    """
    List all open support tickets.

    Returns:
        str: A list of open tickets with their IDs and issues.
    """
    # Here you would integrate with the actual ticketing system API or service
    # For demonstration purposes, we'll just return a placeholder list
    open_tickets = [
        {"ticket_id": "TICKET12345", "issue": "Issue 1"},
        {"ticket_id": "TICKET12346", "issue": "Issue 2"},
        {"ticket_id": "TICKET12347", "issue": "Issue 3"},
    ]
    tickets_str = "\n".join([f"ID: {t['ticket_id']}, Issue: {t['issue']}" for t in open_tickets])
    return f"Open Tickets:\n{tickets_str}"

@tool
def assign_ticket(ticket_id: str, agent_name: str) -> str:
    """
    Assign a support ticket to a specific agent.

    Args:
        ticket_id (str): The ID of the ticket to assign.
        agent_name (str): The name of the agent to assign the ticket to.

    Returns:
        str: Confirmation message indicating the ticket has been assigned.
    """
    # Here you would integrate with the actual ticketing system API or service
    # For demonstration purposes, we'll just return a confirmation string
    return f"Ticket {ticket_id} has been assigned to agent {agent_name}."

@tool
def escalate_ticket(ticket_id: str, reason: str) -> str:
    """
    Escalate a support ticket for further attention.

    Args:
        ticket_id (str): The ID of the ticket to escalate.
        reason (str): The reason for escalation.

    Returns:
        str: Confirmation message indicating the ticket has been escalated.
    """
    # Here you would integrate with the actual ticketing system API or service
    # For demonstration purposes, we'll just return a confirmation string
    return f"Ticket {ticket_id} has been escalated for reason: {reason}."

@tool
def get_ticket_details(ticket_id: str) -> str:
    """
    Retrieve detailed information about a support ticket by its ID.

    Args:
        ticket_id (str): The ID of the ticket to retrieve details for.

    Returns:
        str: Detailed information about the ticket.
    """
    # Here you would integrate with the actual ticketing system API or service
    # For demonstration purposes, we'll just return placeholder details
    details = {
        "ticket_id": ticket_id,
        "issue": "Sample issue description",
        "priority": "High",
        "status": "In Progress",
        "assigned_to": "Agent Name",
        "created_at": "2024-01-01 10:00:00",
        "updated_at": "2024-01-02 12:00:00",
    }
    details_str = "\n".join([f"{key}: {value}" for key, value in details.items()])
    return f"Ticket Details:\n{details_str}"

@tool
def check_for_existing_ticket(issue_description: str) -> str:
    """
    Checks if a ticket with a similar issue description already exists.

    Args:
        issue_description (str): The description of the issue to check for.

    Returns:
        str: The ID of the existing ticket if found, otherwise an empty string.
    """
    # In a real implementation, this would use a search or query to find similar tickets.
    if "similar issue" in issue_description.lower():
        return "TICKET12345"
    return ""
