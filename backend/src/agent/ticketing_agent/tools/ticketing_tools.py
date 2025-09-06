from strands import tool
from sqlalchemy.orm import Session
from ....database.models import Ticket, get_db

@tool
def create_ticket(issue: str, priority: str) -> str:
    """
    Create a support ticket with the given issue and priority.
    """
    db: Session = next(get_db())
    try:
        new_ticket = Ticket(issue=issue, priority=priority)
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)
        return f"Ticket created with ID: {new_ticket.id}, Issue: {issue}, Priority: {priority}"
    except Exception as e:
        db.rollback()
        return f"Error creating ticket: {e}"
    finally:
        db.close()

@tool
def check_ticket_status(ticket_id: int) -> str:
    """
    Check the status of a support ticket by its ID.
    """
    db: Session = next(get_db())
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if ticket:
            return f"Status of ticket {ticket_id}: {ticket.status}"
        return f"Ticket with ID {ticket_id} not found."
    finally:
        db.close()

@tool
def update_ticket(ticket_id: int, update_info: str) -> str:
    """
    Update a support ticket with new information.
    """
    db: Session = next(get_db())
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if ticket:
            ticket.issue = f"{ticket.issue}\n\nUpdate: {update_info}"
            db.commit()
            return f"Ticket {ticket_id} updated."
        return f"Ticket with ID {ticket_id} not found."
    except Exception as e:
        db.rollback()
        return f"Error updating ticket: {e}"
    finally:
        db.close()

@tool
def close_ticket(ticket_id: int) -> str:
    """
    Close a support ticket by its ID.
    """
    db: Session = next(get_db())
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if ticket:
            ticket.status = 'closed'
            db.commit()
            return f"Ticket {ticket_id} has been closed."
        return f"Ticket with ID {ticket_id} not found."
    except Exception as e:
        db.rollback()
        return f"Error closing ticket: {e}"
    finally:
        db.close()

@tool
def list_open_tickets() -> str:
    """
    List all open support tickets.
    """
    db: Session = next(get_db())
    try:
        open_tickets = db.query(Ticket).filter(Ticket.status == 'open').all()
        if not open_tickets:
            return "No open tickets found."
        tickets_str = "\n".join([f"ID: {t.id}, Issue: {t.issue}, Priority: {t.priority}" for t in open_tickets])
        return f"Open Tickets:\n{tickets_str}"
    finally:
        db.close()

@tool
def assign_ticket(ticket_id: int, agent_name: str) -> str:
    """
    Assign a support ticket to a specific agent.
    """
    db: Session = next(get_db())
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if ticket:
            ticket.assigned_to = agent_name
            db.commit()
            return f"Ticket {ticket_id} has been assigned to agent {agent_name}."
        return f"Ticket with ID {ticket_id} not found."
    except Exception as e:
        db.rollback()
        return f"Error assigning ticket: {e}"
    finally:
        db.close()

@tool
def escalate_ticket(ticket_id: int, reason: str) -> str:
    """
    Escalate a support ticket for further attention by setting its priority to high.
    """
    db: Session = next(get_db())
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if ticket:
            ticket.priority = 'high'
            ticket.issue = f"{ticket.issue}\n\nEscalation Reason: {reason}"
            db.commit()
            return f"Ticket {ticket_id} has been escalated to high priority."
        return f"Ticket with ID {ticket_id} not found."
    except Exception as e:
        db.rollback()
        return f"Error escalating ticket: {e}"
    finally:
        db.close()

@tool
def get_ticket_details(ticket_id: int) -> str:
    """
    Retrieve detailed information about a support ticket by its ID.
    """
    db: Session = next(get_db())
    try:
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
    finally:
        db.close()

@tool
def check_for_existing_ticket(issue_description: str) -> str:
    """
    Checks if a ticket with a similar issue description already exists.
    """
    db: Session = next(get_db())
    try:
        # A simple search, can be improved with more advanced searching techniques
        existing_ticket = db.query(Ticket).filter(Ticket.issue.like(f"%{issue_description}%")).first()
        if existing_ticket:
            return str(existing_ticket.id)
        return ""
    finally:
        db.close()
