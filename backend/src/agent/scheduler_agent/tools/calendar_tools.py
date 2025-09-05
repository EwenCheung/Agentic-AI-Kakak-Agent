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