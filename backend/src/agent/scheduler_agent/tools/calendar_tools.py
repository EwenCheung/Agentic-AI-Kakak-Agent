"""Google Calendar tool functions exposed to the scheduler agent - simplified approach."""

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
        result = client.list_events(date, user_id=None)  # Remove user_id requirement
        
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
    """Create a calendar event and return the Event ID for future updates/deletions.

    Args:
        title: Event title
        start_time: Start time in ISO format (YYYY-MM-DDTHH:MM:SS or YYYY-MM-DDTHH:MM:SSZ)
        end_time: End time in ISO format (YYYY-MM-DDTHH:MM:SS or YYYY-MM-DDTHH:MM:SSZ)
        description: Optional event description
        timezone_name: Timezone for the event (IANA format, e.g., 'Asia/Singapore')
    
    Returns:
        Success message with Event ID for future reference
    """
    try:
        # Normalize datetime strings with timezone-naive format (preferred for Google Calendar)
        normalized_start = timezone_handler.normalize_datetime_with_timezone(start_time, timezone_name)
        normalized_end = timezone_handler.normalize_datetime_with_timezone(end_time, timezone_name)
        
        client = get_calendar_client()
        result = client.create_event(
            title=title,
            start_datetime=normalized_start,
            end_datetime=normalized_end,
            description=description,
            user_id=None,  # Remove user_id requirement
            timezone=timezone_name  # Pass timezone to calendar client
        )
        
        return f"✅ Event '{title}' scheduled successfully from {normalized_start} to {normalized_end} in {timezone_name}.\n\n📝 {result}\n\n⚠️ IMPORTANT: Save the Event ID above for future updates or deletions!"
        
    except Exception as e:
        return f"Error scheduling event: {str(e)}"


@tool
def list_events(date: str) -> str:
    """List all events on a given date."""
    client = get_calendar_client()
    return client.list_events(date, user_id=None)


@tool
def cancel_event(event_id: str) -> str:
    """Cancel/delete an event using its Event ID.
    
    Args:
        event_id: The Event ID provided when the event was created
    
    Returns:
        Confirmation of cancellation
    """
    client = get_calendar_client()
    return client.delete_event(event_id, user_id=None)


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
    Updates an existing calendar event using its Event ID.

    Args:
        event_id (str): The Event ID provided when the event was created.
        title (str, optional): The new title for the event.
        start_time (str, optional): The new start time (flexible format: '4pm', '16:00', 'Sep 9', '2024-01-15T14:00:00').
        end_time (str, optional): The new end time (flexible format: '5pm', '17:00', '2024-01-15T15:00:00').
        description (str, optional): The new description for the event.
        timezone_name (str): Timezone for datetime interpretation (IANA format).

    Returns:
        str: Confirmation message indicating the event has been updated.
    """
    try:
        # Get the existing event first to preserve details
        client = get_calendar_client()
        existing_result = client.service.events().get(calendarId="primary", eventId=event_id).execute()
        
        # Parse existing start and end times
        existing_start = existing_result.get('start', {}).get('dateTime')
        existing_end = existing_result.get('end', {}).get('dateTime')
        
        normalized_start = None
        normalized_end = None
        
        if start_time:
            # If user provides just time (like "4pm"), combine with existing date
            if _is_time_only(start_time):
                if existing_start:
                    # Extract date from existing event, combine with new time
                    existing_date = existing_start.split('T')[0]  # Get YYYY-MM-DD part
                    new_datetime = f"{existing_date}T{_parse_time_to_24h(start_time)}"
                    normalized_start = timezone_handler.normalize_datetime_with_timezone(new_datetime, timezone_name)
                else:
                    # Fallback to today if no existing start time
                    from datetime import date
                    today = date.today().isoformat()
                    new_datetime = f"{today}T{_parse_time_to_24h(start_time)}"
                    normalized_start = timezone_handler.normalize_datetime_with_timezone(new_datetime, timezone_name)
            else:
                # Full datetime or date provided
                normalized_start = timezone_handler.normalize_datetime_with_timezone(start_time, timezone_name)
        
        if end_time:
            # Similar logic for end time
            if _is_time_only(end_time):
                if existing_end:
                    existing_date = existing_end.split('T')[0]
                    new_datetime = f"{existing_date}T{_parse_time_to_24h(end_time)}"
                    normalized_end = timezone_handler.normalize_datetime_with_timezone(new_datetime, timezone_name)
                else:
                    from datetime import date
                    today = date.today().isoformat()
                    new_datetime = f"{today}T{_parse_time_to_24h(end_time)}"
                    normalized_end = timezone_handler.normalize_datetime_with_timezone(new_datetime, timezone_name)
            else:
                normalized_end = timezone_handler.normalize_datetime_with_timezone(end_time, timezone_name)
        
        client = get_calendar_client()
        result = client.update_event(
            event_id, 
            title, 
            normalized_start, 
            normalized_end, 
            description, 
            user_id=None,
            timezone=timezone_name
        )
        
        update_details = []
        if title:
            update_details.append(f"title: {title}")
        if normalized_start:
            update_details.append(f"start: {normalized_start}")
        if normalized_end:
            update_details.append(f"end: {normalized_end}")
        if description:
            update_details.append(f"description: {description}")
        
        return f"✅ Event {event_id} updated successfully ({', '.join(update_details)}) in timezone {timezone_name}.\n\n📝 {result}"
        
    except Exception as e:
        return f"Error updating event: {str(e)}"


def _is_time_only(time_str: str) -> bool:
    """Check if the input is just a time (like '4pm', '16:00') rather than a full datetime."""
    import re
    time_patterns = [
        r'^\d{1,2}:\d{2}\s*(am|pm)$',   # 4:30pm
        r'^\d{1,2}\s*(am|pm)$',         # 4pm
        r'^\d{1,2}:\d{2}$',             # 16:30
        r'^\d{1,2}$',                   # 16
    ]
    time_str_clean = time_str.lower().strip()
    return any(re.match(pattern, time_str_clean) for pattern in time_patterns)


def _parse_time_to_24h(time_str: str) -> str:
    """Convert time string to 24-hour format HH:MM."""
    import re
    time_str_clean = time_str.lower().strip()
    
    # 4:30pm -> 16:30
    match = re.match(r'^(\d{1,2}):(\d{2})\s*(am|pm)$', time_str_clean)
    if match:
        hour, minute, period = int(match.group(1)), int(match.group(2)), match.group(3)
        if period == 'pm' and hour != 12:
            hour += 12
        elif period == 'am' and hour == 12:
            hour = 0
        return f"{hour:02d}:{minute:02d}:00"
    
    # 4pm -> 16:00
    match = re.match(r'^(\d{1,2})\s*(am|pm)$', time_str_clean)
    if match:
        hour, period = int(match.group(1)), match.group(2)
        if period == 'pm' and hour != 12:
            hour += 12
        elif period == 'am' and hour == 12:
            hour = 0
        return f"{hour:02d}:00:00"
    
    # 16:30 -> 16:30:00
    match = re.match(r'^(\d{1,2}):(\d{2})$', time_str_clean)
    if match:
        hour, minute = int(match.group(1)), int(match.group(2))
        return f"{hour:02d}:{minute:02d}:00"
    
    # 16 -> 16:00:00
    match = re.match(r'^(\d{1,2})$', time_str_clean)
    if match:
        hour = int(match.group(1))
        return f"{hour:02d}:00:00"
    
    return "12:00:00"  # Default fallback
