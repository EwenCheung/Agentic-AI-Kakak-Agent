
"""Google Calendar tool functions exposed to the scheduler agent."""

from strands import tool
from .time_handler import timezone_handler

from ....services.calendar_client import get_calendar_client


@tool
def check_availability(date: str, timezone_name: str = "Asia/Singapore") -> str:
    """Return events for a date so the model can reason about availability.
    
    Args:
        date: Date in YYYY-MM-DD format
        timezone_name: Timezone to interpret the date in (IANA format)
    
    Returns:
        Events for the specified date in the given timezone
    """
    try:
        # Validate timezone
        if not timezone_handler.is_valid_timezone(timezone_name):
            return f"Error: Invalid timezone '{timezone_name}'. Please use IANA timezone names like 'Asia/Singapore'."
        
        client = get_calendar_client()
        result = client.list_events(date)
        
        return f"Events for {date} in {timezone_name}: {result}"
        
    except Exception as e:
        return f"Error checking availability: {str(e)}"


@tool
def schedule_event(
    title: str, 
    start_time: str, 
    end_time: str, 
    description: str | None = None,
    timezone_name: str = "Asia/Singapore"
) -> str:
    """Create a calendar event with accurate timezone handling.

    Args:
        title: Event title
        start_time: Start time in ISO format (YYYY-MM-DDTHH:MM:SS or YYYY-MM-DDTHH:MM:SSZ)
        end_time: End time in ISO format (YYYY-MM-DDTHH:MM:SS or YYYY-MM-DDTHH:MM:SSZ)
        description: Optional event description
        timezone_name: Timezone for the event (IANA format, e.g., 'Asia/Singapore')
    
    Returns:
        Success message or error details
    """
    try:
        # Normalize datetime strings with proper timezone handling
        normalized_start = timezone_handler.normalize_datetime(start_time, timezone_name)
        normalized_end = timezone_handler.normalize_datetime(end_time, timezone_name)
        
        client = get_calendar_client()
        result = client.create_event(
            title=title,
            start_datetime=normalized_start,
            end_datetime=normalized_end,
            description=description,
        )
        
        return f"Event '{title}' scheduled successfully from {normalized_start} to {normalized_end} in {timezone_name}. {result}"
        
    except Exception as e:
        return f"Error scheduling event: {str(e)}"


@tool
def list_events(date: str) -> str:
    client = get_calendar_client()
    return client.list_events(date)


@tool
def get_empty_slots(date: str, duration_minutes: int = 60) -> str:
    """Return events for date and instruct model to derive free slots."""
    events_result = list_events(date)
    if "No upcoming events found." in events_result:
        return f"Entire day {date} is available (no events scheduled)."
    return (
        f"Events for {date}:\n{events_result}\n\n"
        f"Analyze these events to find free slots of {duration_minutes} minutes or more."
    )


@tool
def cancel_event(event_id: str) -> str:  # alias for delete_event
    client = get_calendar_client()
    return client.delete_event(event_id)


@tool
def get_event_details(event_id: str) -> str:
    """
    Retrieves comprehensive details about a specific calendar event.

    Args:
        event_id (str): The ID of the event to retrieve details for.

    Returns:
        str: Detailed information about the event.
    """
    client = get_calendar_client()
    return client.get_event_details(event_id)


@tool
def update_event(
    event_id: str, 
    title: str = None, 
    start_time: str = None, 
    end_time: str = None, 
    description: str = None,
    timezone_name: str = "Asia/Singapore"
) -> str:
    """
    Updates an existing calendar event with timezone-aware datetime handling.

    Args:
        event_id (str): The ID of the event to update.
        title (str, optional): The new title for the event.
        start_time (str, optional): The new start time (ISO format with timezone handling).
        end_time (str, optional): The new end time (ISO format with timezone handling).
        description (str, optional): The new description for the event.
        timezone_name (str): Timezone for datetime interpretation (IANA format).

    Returns:
        str: Confirmation message indicating the event has been updated.
    """
    try:
        # Normalize datetime strings if provided
        normalized_start = None
        normalized_end = None
        
        if start_time:
            normalized_start = timezone_handler.normalize_datetime(start_time, timezone_name)
        
        if end_time:
            normalized_end = timezone_handler.normalize_datetime(end_time, timezone_name)
        
        client = get_calendar_client()
        result = client.update_event(event_id, title, normalized_start, normalized_end, description)
        
        update_details = []
        if title:
            update_details.append(f"title: {title}")
        if normalized_start:
            update_details.append(f"start: {normalized_start}")
        if normalized_end:
            update_details.append(f"end: {normalized_end}")
        if description:
            update_details.append(f"description: {description}")
        
        return f"Event {event_id} updated successfully ({', '.join(update_details)}) in timezone {timezone_name}. {result}"
        
    except Exception as e:
        return f"Error updating event: {str(e)}"


@tool
def search_events(query: str) -> str:
    """
    Searches for calendar events by a text query.

    Args:
        query (str): The text query to search for.

    Returns:
        str: A summary of events matching the query.
    """
    client = get_calendar_client()
    return client.search_events(query)


@tool
def list_calendars() -> str:
    """
    Lists all available calendars.

    Returns:
        str: A list of calendars.
    """
    client = get_calendar_client()
    return client.list_calendars()
