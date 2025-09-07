"""
Time Handler for Scheduler Agent - Cleaned Version

Provides essential timezone handling and datetime utilities for calendar operations.
Contains only the functions actually used by the scheduler agent.
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
    def has_timezone_in_datetime(datetime_str: str) -> bool:
        """
        Check if a datetime string contains timezone information.
        
        Args:
            datetime_str: Datetime string to check
            
        Returns:
            True if timezone info is present, False otherwise
        """
        # Check for timezone patterns like +05:30, -08:00, Z, etc.
        timezone_patterns = [
            r'[+-]\d{2}:\d{2}$',  # +05:30, -08:00
            r'[+-]\d{4}$',        # +0530, -0800
            r'Z$',                # UTC indicator
            r'\s+[A-Z]{3,4}$'     # PST, EST, etc.
        ]
        
        return any(re.search(pattern, datetime_str.strip()) for pattern in timezone_patterns)
    
    def normalize_datetime(self, datetime_str: str, timezone_name: Optional[str] = None, timezone_aware: bool = False) -> str:
        """
        Normalize a datetime string to ISO format.
        
        Args:
            datetime_str: Input datetime string
            timezone_name: Optional timezone to apply if datetime has no timezone info
            timezone_aware: If True, return UTC timezone-aware string; if False, return timezone-naive string
            
        Returns:
            ISO formatted datetime string (timezone-aware or timezone-naive based on parameter)
        """
        try:
            fallback_timezone = timezone_name or self.default_timezone
            
            # If already has timezone info, parse and convert to UTC
            if self.has_timezone_in_datetime(datetime_str):
                try:
                    # Try parsing with timezone info
                    dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                    if timezone_aware:
                        return dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
                    else:
                        # Convert to target timezone and return timezone-naive
                        target_tz = ZoneInfo(fallback_timezone)
                        dt_target = dt.astimezone(target_tz)
                        return dt_target.replace(tzinfo=None).isoformat()
                except ValueError:
                    # Fallback parsing for other formats
                    pass
            
            # Handle timezone-naive datetime
            # Try different parsing strategies
            dt_naive = None
            
            # Handle simple time formats like "4pm", "16:00", "4:30pm"
            time_patterns = [
                (r'^(\d{1,2}):(\d{2})\s*(am|pm)$', self._parse_12hour_time),  # 4:30pm
                (r'^(\d{1,2})\s*(am|pm)$', self._parse_12hour_time_simple),   # 4pm
                (r'^(\d{1,2}):(\d{2})$', self._parse_24hour_time),            # 16:30
                (r'^(\d{1,2})$', self._parse_hour_only),                      # 16
            ]
            
            # Check for simple time patterns first
            datetime_str_clean = datetime_str.lower().strip()
            for pattern, parser in time_patterns:
                match = re.match(pattern, datetime_str_clean)
                if match:
                    # Create datetime for today with the parsed time
                    from datetime import date
                    today = date.today()
                    time_obj = parser(match)
                    dt_naive = datetime.combine(today, time_obj)
                    break
            
            # If not a simple time, try full datetime formats
            if dt_naive is None:
                # Common ISO formats
                iso_formats = [
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%dT%H:%M',
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d %H:%M',
                    '%Y-%m-%d'
                ]
                
                for fmt in iso_formats:
                    try:
                        dt_naive = datetime.strptime(datetime_str, fmt)
                        break
                    except ValueError:
                        continue
            
            if dt_naive is None:
                raise ValueError(f"Could not parse datetime: {datetime_str}")
            
            if timezone_aware:
                # Apply fallback timezone and convert to UTC
                tz = ZoneInfo(fallback_timezone)
                dt_with_tz = dt_naive.replace(tzinfo=tz)
                return dt_with_tz.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
            else:
                # Return timezone-naive datetime string
                return dt_naive.isoformat()
                
        except Exception as e:
            raise ValueError(f"Failed to normalize datetime '{datetime_str}': {str(e)}")
    
    def _parse_12hour_time(self, match):
        """Parse 12-hour time like '4:30pm' """
        from datetime import time
        hour = int(match.group(1))
        minute = int(match.group(2))
        period = match.group(3).lower()
        
        if period == 'pm' and hour != 12:
            hour += 12
        elif period == 'am' and hour == 12:
            hour = 0
            
        return time(hour, minute)
    
    def _parse_12hour_time_simple(self, match):
        """Parse simple 12-hour time like '4pm' """
        from datetime import time
        hour = int(match.group(1))
        period = match.group(2).lower()
        
        if period == 'pm' and hour != 12:
            hour += 12
        elif period == 'am' and hour == 12:
            hour = 0
            
        return time(hour, 0)
    
    def _parse_24hour_time(self, match):
        """Parse 24-hour time like '16:30' """
        from datetime import time
        hour = int(match.group(1))
        minute = int(match.group(2))
        return time(hour, minute)
    
    def _parse_hour_only(self, match):
        """Parse hour only like '16' """
        from datetime import time
        hour = int(match.group(1))
        return time(hour, 0)
            
    def normalize_datetime_with_timezone(self, datetime_str: str, timezone_name: Optional[str] = None) -> str:
        """
        Normalize datetime to timezone-naive format for use with separate timezone parameter.
        This is the preferred method for Google Calendar API.
        """
        return self.normalize_datetime(datetime_str, timezone_name, timezone_aware=False)


# Create global instance
timezone_handler = TimezoneHandler()
# Global instance
timezone_handler = TimezoneHandler(default_timezone="Asia/Singapore")


@tool
def get_current_time_with_timezone(timezone_name: str = "Asia/Singapore") -> str:
    """
    Get the current time in a specific timezone.
    
    Args:
        timezone_name: IANA timezone name (e.g., 'Asia/Singapore', 'America/New_York')
        
    Returns:
        Current time in the specified timezone as ISO string
    """
    try:
        if not timezone_handler.is_valid_timezone(timezone_name):
            return f"Error: Invalid timezone '{timezone_name}'. Please use IANA timezone names like 'Asia/Singapore'."
        
        tz = ZoneInfo(timezone_name)
        current_time = datetime.now(tz)
        
        return f"Current time in {timezone_name}: {current_time.isoformat()}"
        
    except Exception as e:
        return f"Error getting current time: {str(e)}"


@tool
def validate_and_normalize_datetime(datetime_str: str, timezone_name: str = "Asia/Singapore") -> str:
    """
    Validate and normalize a datetime string for calendar operations.
    
    Args:
        datetime_str: Input datetime string in various formats
        timezone_name: Timezone to apply if input has no timezone info
        
    Returns:
        Normalized ISO datetime string with UTC timezone or error message
    """
    try:
        if not timezone_handler.is_valid_timezone(timezone_name):
            return f"Error: Invalid timezone '{timezone_name}'. Please use IANA timezone names like 'Asia/Singapore'."
        
        normalized = timezone_handler.normalize_datetime_with_timezone(datetime_str, timezone_name)
        return f"Normalized datetime: {normalized} (timezone-naive, use with timezone: {timezone_name})"
        
    except Exception as e:
        return f"Error validating datetime: {str(e)}"
