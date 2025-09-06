
"""Google Calendar tool functions exposed to the scheduler agent."""

from strands import tool

from ....services.calendar_client import get_calendar_client


@tool
def check_availability(date: str) -> str:
    """Return events for a date so the model can reason about availability."""
    client = get_calendar_client()
    return client.list_events(date)


@tool
def schedule_event(
    title: str, start_time: str, end_time: str, description: str | None = None
) -> str:
    """Create a calendar event.

    start_time / end_time: ISO format YYYY-MM-DDTHH:MM:SSZ
    """
    client = get_calendar_client()
    return client.create_event(
        title=title,
        start_datetime=start_time,
        end_datetime=end_time,
        description=description,
    )


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
def update_event(event_id: str, title: str = None, start_time: str = None, end_time: str = None, description: str = None) -> str:
    """
    Updates an existing calendar event.

    Args:
        event_id (str): The ID of the event to update.
        title (str, optional): The new title for the event. Defaults to None.
        start_time (str, optional): The new start time (ISO format YYYY-MM-DDTHH:MM:SSZ). Defaults to None.
        end_time (str, optional): The new end time (ISO format YYYY-MM-DDTHH:MM:SSZ). Defaults to None.
        description (str, optional): The new description for the event. Defaults to None.

    Returns:
        str: Confirmation message indicating the event has been updated.
    """
    client = get_calendar_client()
    return client.update_event(event_id, title, start_time, end_time, description)


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
