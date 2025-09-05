"""
Google Calendar Tools for Scheduler Agent

Provides calendar functionality through the Google Calendar MCP client.
These tools integrate with the Strands framework for AI agent operations.
"""

from strands import tool
from src.services.calendar_client import get_calendar_client, run_async_calendar_operation


@tool
def check_availability(date: str) -> str:
    """
    Check availability for a specific date.
    
    Args:
        date (str): Date to check availability for (YYYY-MM-DD format)
    
    Returns:
        str: List of events for the specified date to determine availability
    """
    client = get_calendar_client()
    return run_async_calendar_operation(
        client.list_events(date)
    )


@tool
def schedule_event(title: str, start_time: str, end_time: str, description: str = None) -> str:
    """
    Schedule a new calendar event.
    
    Args:
        title (str): Event title
        start_time (str): Start time in ISO format (YYYY-MM-DDTHH:MM:SSZ)
        end_time (str): End time in ISO format (YYYY-MM-DDTHH:MM:SSZ)
        description (str, optional): Event description
    
    Returns:
        str: Confirmation of event creation
    """
    client = get_calendar_client()
    return run_async_calendar_operation(
        client.create_event(
            title=title,
            start_datetime=start_time,
            end_datetime=end_time,
            description=description
        )
    )


@tool
def list_events(date: str) -> str:
    """
    List all events for a specific date.
    
    Args:
        date (str): Date to list events for (YYYY-MM-DD format)
    
    Returns:
        str: List of events for the specified date
    """
    client = get_calendar_client()
    return run_async_calendar_operation(
        client.list_events(date)
    )


@tool
def update_event(event_id: str, title: str = None, start_time: str = None, 
                end_time: str = None, description: str = None) -> str:
    """
    Update an existing calendar event.
    
    Args:
        event_id (str): ID of the event to update
        title (str, optional): New event title
        start_time (str, optional): New start time in ISO format
        end_time (str, optional): New end time in ISO format
        description (str, optional): New event description
    
    Returns:
        str: Confirmation of event update
    """
    client = get_calendar_client()
    return run_async_calendar_operation(
        client.update_event(
            event_id=event_id,
            title=title,
            start_datetime=start_time,
            end_datetime=end_time,
            description=description
        )
    )


@tool
def delete_event(event_id: str) -> str:
    """
    Delete a calendar event.
    
    Args:
        event_id (str): ID of the event to delete
    
    Returns:
        str: Confirmation of event deletion
    """
    client = get_calendar_client()
    return run_async_calendar_operation(
        client.delete_event(event_id)
    )


@tool
def search_events(query: str) -> str:
    """
    Search for events by text query.
    
    Args:
        query (str): Search query to find events
    
    Returns:
        str: Search results matching the query
    """
    client = get_calendar_client()
    return run_async_calendar_operation(
        client.search_events(query)
    )


@tool
def get_event_details(event_id: str) -> str:
    """
    Get detailed information about a specific event.
    
    Args:
        event_id (str): ID of the event to get details for
    
    Returns:
        str: Detailed event information
    """
    client = get_calendar_client()
    return run_async_calendar_operation(
        client.get_event_details(event_id)
    )


@tool
def get_empty_slots(date: str, duration_minutes: int = 60) -> str:
    """
    Find empty time slots for a specific date.
    
    Args:
        date (str): Date to find empty slots for (YYYY-MM-DD format)
        duration_minutes (int): Minimum duration for empty slots in minutes
    
    Returns:
        str: Available time slots for the specified date
    """
    client = get_calendar_client()
    events_result = run_async_calendar_operation(
        client.list_events(date)
    )
    
    # Simple implementation - just return the events list for now
    # The agent can analyze this to determine free slots
    if "No events found" in events_result:
        return f"Entire day {date} is available (no events scheduled)"
    else:
        return f"Events for {date}:\n{events_result}\n\nAnalyze these events to find free slots of {duration_minutes} minutes or more."


@tool
def cancel_event(event_id: str) -> str:
    """
    Cancel (delete) a calendar event.
    
    Args:
        event_id (str): ID of the event to cancel
    
    Returns:
        str: Confirmation of event cancellation
    """
    return delete_event(event_id)


@tool
def list_calendars() -> str:
    """
    List all available calendars.
    
    Returns:
        str: List of all calendars with their details
    """
    client = get_calendar_client()
    return run_async_calendar_operation(
        client.list_calendars()
    )
