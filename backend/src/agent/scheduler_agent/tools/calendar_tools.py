"""Google Calendar tool functions exposed to the scheduler agent.

These wrap the async MCP calendar client operations into synchronous Strands
tools so the LLM agent can invoke them.
"""

from strands import tool

from ....services.calendar_client import (
    get_calendar_client,
    run_async_calendar_operation,
)


@tool
def check_availability(date: str) -> str:
    """Return events for a date so the model can reason about availability."""
    client = get_calendar_client()
    return run_async_calendar_operation(client.list_events(date))


@tool
def schedule_event(
    title: str, start_time: str, end_time: str, description: str | None = None
) -> str:
    """Create a calendar event.

    start_time / end_time: ISO format YYYY-MM-DDTHH:MM:SSZ
    """
    client = get_calendar_client()
    return run_async_calendar_operation(
        client.create_event(
            title=title,
            start_datetime=start_time,
            end_datetime=end_time,
            description=description,
        )
    )


@tool
def list_events(date: str) -> str:
    client = get_calendar_client()
    return run_async_calendar_operation(client.list_events(date))


@tool
def update_event(
    event_id: str,
    title: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    description: str | None = None,
) -> str:
    client = get_calendar_client()
    return run_async_calendar_operation(
        client.update_event(
            event_id=event_id,
            title=title,
            start_datetime=start_time,
            end_datetime=end_time,
            description=description,
        )
    )


@tool
def delete_event(event_id: str) -> str:
    client = get_calendar_client()
    return run_async_calendar_operation(client.delete_event(event_id))


@tool
def search_events(query: str) -> str:
    client = get_calendar_client()
    return run_async_calendar_operation(client.search_events(query))


@tool
def get_event_details(event_id: str) -> str:
    client = get_calendar_client()
    return run_async_calendar_operation(client.get_event_details(event_id))


@tool
def get_empty_slots(date: str, duration_minutes: int = 60) -> str:
    """Return events for date and instruct model to derive free slots."""
    events_result = list_events(date)
    if "No events" in events_result:
        return f"Entire day {date} is available (no events scheduled)."
    return (
        f"Events for {date}:\n{events_result}\n\n"
        f"Analyze these events to find free slots of {duration_minutes} minutes or more."
    )


@tool
def cancel_event(event_id: str) -> str:  # alias for delete_event
    return delete_event(event_id)


@tool
def list_calendars() -> str:
    client = get_calendar_client()
    return run_async_calendar_operation(client.list_calendars())
