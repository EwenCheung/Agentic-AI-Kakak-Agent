from strands import tool
from sqlalchemy.orm import Session
from ....database.models import Ticket, get_db

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
    db: Session = next(get_db())
    new_ticket = Ticket(issue=issue, priority=priority)
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return f"Ticket created with ID: {new_ticket.id}, Issue: {issue}, Priority: {priority}"

@tool
def check_ticket_status(ticket_id: int) -> str:
    """
    Check the status of a support ticket by its ID.

    Args:
        ticket_id (int): The ID of the ticket to check.

    Returns:
        str: The current status of the ticket.
    """
    db: Session = next(get_db())
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket:
        return f"Status of ticket {ticket_id}: {ticket.status}"
    return f"Ticket with ID {ticket_id} not found."

@tool
def update_ticket(ticket_id: int, update_info: str) -> str:
    """
    Update a support ticket with new information.

    Args:
        ticket_id (int): The ID of the ticket to update.
        update_info (str): The information to update the ticket with.

    Returns:
        str: Confirmation message indicating the status of the update.
    """
    db: Session = next(get_db())
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket:
        ticket.issue = f"{ticket.issue}\n\nUpdate: {update_info}"
        db.commit()
        return f"Ticket {ticket_id} updated."
    return f"Ticket with ID {ticket_id} not found."

@tool
def close_ticket(ticket_id: int) -> str:
    """
    Close a support ticket by its ID.

    Args:
        ticket_id (int): The ID of the ticket to close.

    Returns:
        str: Confirmation message indicating the ticket has been closed.
    """
    db: Session = next(get_db())
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket:
        ticket.status = 'closed'
        db.commit()
        return f"Ticket {ticket_id} has been closed."
    return f"Ticket with ID {ticket_id} not found."

@tool
def list_open_tickets() -> str:
    """
    List all open support tickets.

    Returns:
        str: A list of open tickets with their IDs and issues.
    """
    db: Session = next(get_db())
    open_tickets = db.query(Ticket).filter(Ticket.status == 'open').all()
    if not open_tickets:
        return "No open tickets found."
    tickets_str = "\n".join([f"ID: {t.id}, Issue: {t.issue}, Priority: {t.priority}" for t in open_tickets])
    return f"Open Tickets:\n{tickets_str}"

@tool
def assign_ticket(ticket_id: int, agent_name: str) -> str:
    """
    Assign a support ticket to a specific agent.

    Args:
        ticket_id (int): The ID of the ticket to assign.
        agent_name (str): The name of the agent to assign the ticket to.

    Returns:
        str: Confirmation message indicating the ticket has been assigned.
    """
    db: Session = next(get_db())
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket:
        ticket.assigned_to = agent_name
        db.commit()
        return f"Ticket {ticket_id} has been assigned to agent {agent_name}."
    return f"Ticket with ID {ticket_id} not found."

@tool
def escalate_ticket(ticket_id: int, reason: str) -> str:
    """
    Escalate a support ticket for further attention by setting its priority to high.

    Args:
        ticket_id (int): The ID of the ticket to escalate.
        reason (str): The reason for escalation.

    Returns:
        str: Confirmation message indicating the ticket has been escalated.
    """
    db: Session = next(get_db())
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket:
        ticket.priority = 'high'
        ticket.issue = f"{ticket.issue}\n\nEscalation Reason: {reason}"
        db.commit()
        return f"Ticket {ticket_id} has been escalated to high priority."
    return f"Ticket with ID {ticket_id} not found."

@tool
def get_ticket_details(ticket_id: int) -> str:
    """
    Retrieve detailed information about a support ticket by its ID.

    Args:
        ticket_id (int): The ID of the ticket to retrieve details for.

    Returns:
        str: Detailed information about the ticket.
    """
    db: Session = next(get_db())
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket:
        details = {
            "ticket_id": ticket.id,
            "issue": ticket.issue,
            "priority": ticket.priority,
            "status": ticket.status,
            "assigned_to": ticket.assigned_to,
            "created_at": ticket.created_at.isoformat(),
            "updated_at": ticket.updated_at.isoformat(),
        }
        details_str = "\n".join([f"{key}: {value}" for key, value in details.items()])
        return f"Ticket Details:\n{details_str}"
    return f"Ticket with ID {ticket_id} not found."

@tool
def check_for_existing_ticket(issue_description: str) -> str:
    """
    Checks if a ticket with a similar issue description already exists.

    Args:
        issue_description (str): The description of the issue to check for.

    Returns:
        str: The ID of the existing ticket if found, otherwise an empty string.
    """
    db: Session = next(get_db())
    # A simple search, can be improved with more advanced searching techniques
    existing_ticket = db.query(Ticket).filter(Ticket.issue.like(f"%{issue_description}%")).first()
    if existing_ticket:
        return str(existing_ticket.id)
    return ""