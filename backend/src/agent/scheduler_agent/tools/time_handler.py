"""
Time Handler for Scheduler Agent

Provides robust timezone handling and datetime utilities for calendar operations.
Based on the Google Calendar MCP datetime utilities with Python implementation.
"""

import re
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Union
from zoneinfo import ZoneInfo, available_timezones
from strands import tool
import logging

logger = logging.getLogger(__name__)

class TimezoneHandler:
    """Handles timezone operations and datetime conversions for the scheduler agent."""
    
    def __init__(self, default_timezone: str = "UTC"):
        """
        Initialize the timezone handler.
        
        Args:
            default_timezone: Default timezone to use (IANA format, e.g., 'America/Los_Angeles')
        """
        self.default_timezone = default_timezone
        if not self.is_valid_timezone(default_timezone):
            logger.warning(f"Invalid default timezone '{default_timezone}', falling back to UTC")
            self.default_timezone = "UTC"
    
    @staticmethod
    def is_valid_timezone(timezone_name: str) -> bool:
        """
        Validate an IANA timezone name.
        
        Args:
            timezone_name: IANA timezone name to validate
            
        Returns:
            True if valid timezone, False otherwise
        """
        try:
            ZoneInfo(timezone_name)
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_system_timezone() -> str:
        """
        Get the system's default timezone.
        
        Returns:
            IANA timezone name for the system's timezone
        """
        try:
            # Get system timezone using datetime
            local_tz = datetime.now().astimezone().tzinfo
            if hasattr(local_tz, 'key'):
                return local_tz.key
            else:
                # Fallback: try to determine from UTC offset
                utc_offset = datetime.now().astimezone().utcoffset()
                if utc_offset == timedelta(0):
                    return "UTC"
                else:
                    # This is a simplified fallback - in practice you might want more sophisticated detection
                    hours = int(utc_offset.total_seconds() / 3600)
                    if hours == 8:
                        return "Asia/Singapore"  # Common GMT+8 timezone
                    elif hours == -8:
                        return "America/Los_Angeles"
                    elif hours == -5:
                        return "America/New_York"
                    else:
                        return "UTC"
        except Exception:
            logger.warning('Could not determine system timezone, falling back to UTC')
            return 'UTC'
    
    @staticmethod
    def has_timezone_in_datetime(datetime_str: str) -> bool:
        """
        Check if a datetime string includes timezone information.
        
        Args:
            datetime_str: ISO 8601 datetime string
            
        Returns:
            True if timezone is included, False if timezone-naive
        """
        pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})$'
        return bool(re.match(pattern, datetime_str))
    
    def convert_to_timezone(self, datetime_str: str, target_timezone: str, source_timezone: Optional[str] = None) -> str:
        """
        Convert a datetime string to a specific timezone.
        
        Args:
            datetime_str: ISO 8601 datetime string (with or without timezone)
            target_timezone: Target timezone (IANA format)
            source_timezone: Source timezone if datetime_str is timezone-naive
            
        Returns:
            ISO 8601 formatted datetime string in target timezone
        """
        try:
            # Validate target timezone
            if not self.is_valid_timezone(target_timezone):
                raise ValueError(f"Invalid target timezone: {target_timezone}")
            
            # Parse the datetime
            if self.has_timezone_in_datetime(datetime_str):
                # Timezone-aware datetime
                dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            else:
                # Timezone-naive datetime
                dt = datetime.fromisoformat(datetime_str)
                if source_timezone:
                    if not self.is_valid_timezone(source_timezone):
                        raise ValueError(f"Invalid source timezone: {source_timezone}")
                    dt = dt.replace(tzinfo=ZoneInfo(source_timezone))
                else:
                    dt = dt.replace(tzinfo=ZoneInfo(self.default_timezone))
            
            # Convert to target timezone
            target_dt = dt.astimezone(ZoneInfo(target_timezone))
            return target_dt.isoformat()
            
        except Exception as e:
            logger.error(f"Error converting datetime '{datetime_str}' to timezone '{target_timezone}': {e}")
            return datetime_str  # Return original on error
    
    def normalize_datetime(self, datetime_str: str, timezone_name: Optional[str] = None) -> str:
        """
        Normalize a datetime string to ISO 8601 format with timezone.
        
        Args:
            datetime_str: Various datetime formats
            timezone_name: Timezone to use if datetime is timezone-naive
            
        Returns:
            Normalized ISO 8601 datetime string with timezone
        """
        try:
            # Use provided timezone or default
            tz = timezone_name or self.default_timezone
            
            if not self.is_valid_timezone(tz):
                logger.warning(f"Invalid timezone '{tz}', using UTC")
                tz = "UTC"
            
            if self.has_timezone_in_datetime(datetime_str):
                # Already has timezone, parse and normalize
                dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                return dt.isoformat()
            else:
                # Timezone-naive, add timezone
                dt = datetime.fromisoformat(datetime_str)
                dt = dt.replace(tzinfo=ZoneInfo(tz))
                return dt.isoformat()
                
        except Exception as e:
            logger.error(f"Error normalizing datetime '{datetime_str}': {e}")
            # Fallback to current time with UTC
            return datetime.now(timezone.utc).isoformat()
    
    def create_calendar_time_object(self, datetime_str: str, fallback_timezone: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a time object for Google Calendar API.
        
        Args:
            datetime_str: ISO 8601 datetime string or date-only string
            fallback_timezone: Timezone to use if datetime is timezone-naive
            
        Returns:
            Dictionary compatible with Google Calendar API time object
        """
        try:
            # Check if this is a date-only string (all-day event)
            if 'T' not in datetime_str:
                # All-day event
                return {"date": datetime_str}
            
            # Use provided fallback timezone or default
            tz = fallback_timezone or self.default_timezone
            
            if not self.is_valid_timezone(tz):
                logger.warning(f"Invalid fallback timezone '{tz}', using UTC")
                tz = "UTC"
            
            if self.has_timezone_in_datetime(datetime_str):
                # Timezone included in datetime - use as-is
                return {"dateTime": datetime_str}
            else:
                # Timezone-naive datetime - use fallback timezone
                return {"dateTime": datetime_str, "timeZone": tz}
                
        except Exception as e:
            logger.error(f"Error creating time object for '{datetime_str}': {e}")
            # Fallback to current time
            now = datetime.now(timezone.utc)
            return {"dateTime": now.isoformat()}


# Global timezone handler instance
timezone_handler = TimezoneHandler(default_timezone="Asia/Singapore")  # GMT+8 as mentioned in your agent


@tool
def get_current_time_with_timezone(timezone_name: str = "Asia/Singapore") -> str:
    """
    Get the current time in a specific timezone.
    
    Args:
        timezone_name: IANA timezone name (e.g., 'Asia/Singapore', 'America/New_York')
        
    Returns:
        Current time in the specified timezone as ISO 8601 string
    """
    try:
        if not timezone_handler.is_valid_timezone(timezone_name):
            return f"Error: Invalid timezone '{timezone_name}'. Use IANA timezone names like 'Asia/Singapore' or 'America/New_York'."
        
        now = datetime.now(ZoneInfo(timezone_name))
        return f"Current time in {timezone_name}: {now.isoformat()}"
        
    except Exception as e:
        logger.error(f"Error getting current time for timezone '{timezone_name}': {e}")
        return f"Error getting current time: {str(e)}"


@tool
def convert_datetime_timezone(datetime_str: str, from_timezone: str, to_timezone: str) -> str:
    """
    Convert a datetime from one timezone to another.
    
    Args:
        datetime_str: ISO 8601 datetime string
        from_timezone: Source timezone (IANA format)
        to_timezone: Target timezone (IANA format)
        
    Returns:
        Converted datetime string with timezone information
    """
    try:
        result = timezone_handler.convert_to_timezone(datetime_str, to_timezone, from_timezone)
        return f"Converted {datetime_str} from {from_timezone} to {to_timezone}: {result}"
        
    except Exception as e:
        logger.error(f"Error converting datetime: {e}")
        return f"Error converting datetime: {str(e)}"


@tool
def validate_and_normalize_datetime(datetime_str: str, timezone_name: str = "Asia/Singapore") -> str:
    """
    Validate and normalize a datetime string for calendar operations.
    
    Args:
        datetime_str: Various datetime formats to normalize
        timezone_name: Timezone to apply if datetime is timezone-naive
        
    Returns:
        Normalized ISO 8601 datetime string suitable for calendar API
    """
    try:
        normalized = timezone_handler.normalize_datetime(datetime_str, timezone_name)
        return f"Normalized datetime: {normalized}"
        
    except Exception as e:
        logger.error(f"Error normalizing datetime: {e}")
        return f"Error normalizing datetime: {str(e)}"


@tool
def get_timezone_info(timezone_name: str) -> str:
    """
    Get information about a specific timezone.
    
    Args:
        timezone_name: IANA timezone name
        
    Returns:
        Timezone information including current time and UTC offset
    """
    try:
        if not timezone_handler.is_valid_timezone(timezone_name):
            return f"Error: Invalid timezone '{timezone_name}'"
        
        now = datetime.now(ZoneInfo(timezone_name))
        utc_now = datetime.now(timezone.utc)
        offset = now.utcoffset()
        
        info = {
            "timezone": timezone_name,
            "current_time": now.isoformat(),
            "utc_offset": str(offset),
            "is_dst": now.dst() != timedelta(0) if now.dst() is not None else False,
            "utc_time": utc_now.isoformat()
        }
        
        return json.dumps(info, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting timezone info: {e}")
        return f"Error getting timezone info: {str(e)}"


@tool
def list_common_timezones() -> str:
    """
    List common timezones for reference.
    
    Returns:
        JSON string with common timezone names and their current times
    """
    common_timezones = [
        "UTC",
        "Asia/Singapore",
        "Asia/Kuala_Lumpur", 
        "Asia/Jakarta",
        "Asia/Bangkok",
        "Asia/Tokyo",
        "America/New_York",
        "America/Los_Angeles",
        "Europe/London",
        "Europe/Paris",
        "Australia/Sydney"
    ]
    
    timezone_info = {}
    for tz in common_timezones:
        try:
            now = datetime.now(ZoneInfo(tz))
            timezone_info[tz] = {
                "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
                "utc_offset": str(now.utcoffset())
            }
        except Exception as e:
            timezone_info[tz] = {"error": str(e)}
    
    return json.dumps(timezone_info, indent=2)


@tool 
def create_calendar_event_times(start_time: str, end_time: str, timezone_name: str = "Asia/Singapore") -> str:
    """
    Create properly formatted time objects for calendar event creation.
    
    Args:
        start_time: Event start time (ISO 8601 format)
        end_time: Event end time (ISO 8601 format)
        timezone_name: Timezone for the event
        
    Returns:
        JSON string with formatted time objects for calendar API
    """
    try:
        start_obj = timezone_handler.create_calendar_time_object(start_time, timezone_name)
        end_obj = timezone_handler.create_calendar_time_object(end_time, timezone_name)
        
        result = {
            "start": start_obj,
            "end": end_obj,
            "timezone_used": timezone_name
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error creating calendar event times: {e}")
        return f"Error creating calendar event times: {str(e)}"
