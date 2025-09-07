"""
Google Calendar API Client

A robust client for communicating with the Google Calendar API.
Provides high-level methods for calendar operations.
"""

import os
import logging
import json
from typing import Dict, Any
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import tempfile # Added for temporary file creation

from ..config.settings import settings

# Set up logging
logger = logging.getLogger(__name__)

def get_calendar_status() -> Dict[str, Any]:
    """Check if Google Calendar is configured and ready."""
    # Check if client secret is available in DB or .env
    client_secret_content = settings.get_google_client_secret()
    if not client_secret_content:
        return {"configured": False, "ready": False, "reason": "Google Calendar client secret not found in database or .env."} # Updated message
        
    return {"configured": True, "ready": True, "reason": "OK"}

# Scopes for the Google Calendar API
SCOPES = ["https://www.googleapis.com/auth/calendar"]

class GoogleCalendarClient:
    """
    A client for interacting with the Google Calendar API.
    """

    def __init__(self):
        """
        Initialize the Google Calendar client.
        """
        self.creds = self._get_credentials()
        self.service = build("calendar", "v3", credentials=self.creds)

    def _get_credentials(self) -> Credentials:
        """
        Get credentials for the Google Calendar API.
        """
        creds = None
        token_path = "token.json"
        # creds_path = settings.GOOGLE_CALENDAR_CREDENTIALS_PATH # Removed

        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                client_secret_content = settings.get_google_client_secret()
                if not client_secret_content:
                    raise Exception("Google Calendar client secret not found in database. Please configure it.")
                
                # Write client secret to a temporary file
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
                    temp_file.write(client_secret_content)
                    temp_file_path = temp_file.name
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(temp_file_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                finally:
                    os.remove(temp_file_path) # Clean up temporary file
            
            with open(token_path, "w") as token:
                token.write(creds.to_json())
        
        return creds

    def list_events(self, start_date: str, end_date: str = None, calendar_id: str = "primary", user_id: str = None) -> str:
        """
        List events in a date range, optionally filtered by user_id.
        If user_id is None, returns all events (admin function).
        If user_id is provided, returns only events owned by that user.
        """
        try:
            start_time = f"{start_date}T00:00:00Z"
            end_time = f"{end_date}T23:59:59Z" if end_date else start_time

            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            
            events = events_result.get("items", [])
            if not events:
                return "No upcoming events found."
            
            # Filter events by user_id only if user_id is provided
            if user_id is not None:
                user_events = []
                for event in events:
                    # Check if event belongs to user (stored in description or extended properties)
                    event_user_id = event.get('extendedProperties', {}).get('private', {}).get('user_id')
                    if event_user_id == user_id:
                        user_events.append(event)
                events = user_events
                
                if not events:
                    return f"No events found for user {user_id}."
            
            return json.dumps(events)
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return f"An error occurred: {error}"

    def create_event(self, title: str, start_datetime: str, end_datetime: str, description: str = None, calendar_id: str = "primary", user_id: str = None, timezone: str = None) -> str:
        """
        Create a new calendar event with proper timezone handling.
        """
        # Build the event with proper timezone handling
        event = {
            "summary": title,
            "description": description,
        }
        
        # Handle start time with proper timezone
        if self._is_timezone_aware_datetime(start_datetime):
            event["start"] = {
                "dateTime": start_datetime
            }
        else:
            event["start"] = {
                "dateTime": start_datetime,
                "timeZone": timezone or "Asia/Singapore"
            }
        
        # Handle end time with proper timezone  
        if self._is_timezone_aware_datetime(end_datetime):
            event["end"] = {
                "dateTime": end_datetime
            }
        else:
            event["end"] = {
                "dateTime": end_datetime,
                "timeZone": timezone or "Asia/Singapore"
            }
        
        # Add user ownership information (skip for simplified approach)
        if user_id:
            event["extendedProperties"] = {
                "private": {
                    "user_id": user_id
                }
            }
            # Also add to description for visibility
            if description:
                event["description"] = f"{description}\n\n[Owner: {user_id}]"
            else:
                event["description"] = f"[Owner: {user_id}]"

        try:
            event = self.service.events().insert(calendarId=calendar_id, body=event).execute()
            event_id = event.get('id')
            event_link = event.get('htmlLink')
            return f"Event created successfully! Event ID: {event_id}, Link: {event_link}"
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return f"An error occurred: {error}"

    def update_event(self, event_id: str, title: str = None, start_datetime: str = None, end_datetime: str = None, description: str = None, calendar_id: str = "primary", user_id: str = None, timezone: str = None) -> str:
        """
        Update an existing calendar event with proper timezone handling.
        """
        try:
            event = self.service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            
            # Verify user ownership if user_id is provided (skip for simplified approach)
            if user_id:
                event_user_id = event.get('extendedProperties', {}).get('private', {}).get('user_id')
                if event_user_id != user_id:
                    return f"Error: Access denied. Event {event_id} does not belong to user {user_id}."

            if title:
                event['summary'] = title
                
            if description:
                # Preserve user ownership in description
                if user_id:
                    if description:
                        event['description'] = f"{description}\n\n[Owner: {user_id}]"
                    else:
                        event['description'] = f"[Owner: {user_id}]"
                else:
                    event['description'] = description
                    
            # Handle datetime updates with proper timezone handling
            if start_datetime:
                if self._is_timezone_aware_datetime(start_datetime):
                    # Timezone-aware datetime (has Z or +/-HH:MM)
                    event['start'] = {
                        "dateTime": start_datetime
                    }
                else:
                    # Timezone-naive datetime - use separate timeZone property
                    event['start'] = {
                        "dateTime": start_datetime,
                        "timeZone": timezone or "Asia/Singapore"
                    }
                    
            if end_datetime:
                if self._is_timezone_aware_datetime(end_datetime):
                    # Timezone-aware datetime (has Z or +/-HH:MM)
                    event['end'] = {
                        "dateTime": end_datetime
                    }
                else:
                    # Timezone-naive datetime - use separate timeZone property
                    event['end'] = {
                        "dateTime": end_datetime,
                        "timeZone": timezone or "Asia/Singapore"
                    }

            updated_event = self.service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
            return f"Event updated successfully: {updated_event.get('htmlLink')}"
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return f"An error occurred: {error}"
    
    def _is_timezone_aware_datetime(self, datetime_str: str) -> bool:
        """
        Check if a datetime string is timezone-aware (has Z or +/-HH:MM).
        """
        import re
        # Check for timezone indicators: Z or +/-HH:MM
        timezone_pattern = r'(Z|[+-]\d{2}:\d{2})$'
        return bool(re.search(timezone_pattern, datetime_str))

    def delete_event(self, event_id: str, calendar_id: str = "primary", user_id: str = None) -> str:
        """
        Delete a calendar event with user ownership verification.
        """
        try:
            # Verify user ownership if user_id is provided
            if user_id:
                event = self.service.events().get(calendarId=calendar_id, eventId=event_id).execute()
                event_user_id = event.get('extendedProperties', {}).get('private', {}).get('user_id')
                if event_user_id != user_id:
                    return f"Error: Access denied. Event {event_id} does not belong to user {user_id}."
            
            self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            return f"Event deleted by user {user_id}."
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return f"An error occurred: {error}"

    def search_events(self, query: str, calendar_id: str = "primary", user_id: str = None) -> str:
        """
        Search for events, optionally filtered by user_id.
        If user_id is None, returns all matching events (admin function).
        If user_id is provided, returns only events owned by that user.
        """
        try:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                q=query,
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            
            events = events_result.get("items", [])
            if not events:
                return "No events found."
            
            # Filter events by user_id only if user_id is provided
            if user_id is not None:
                user_events = []
                for event in events:
                    event_user_id = event.get('extendedProperties', {}).get('private', {}).get('user_id')
                    if event_user_id == user_id:
                        user_events.append(event)
                events = user_events
                
                if not events:
                    return f"No events found for user {user_id} matching query '{query}'."
            
            return str(events)
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return f"An error occurred: {error}"

    def get_event_details(self, event_id: str, calendar_id: str = "primary", user_id: str = None) -> str:
        """
        Get details of a specific event with user ownership verification.
        """
        try:
            event = self.service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            
            # Verify user ownership if user_id is provided
            if user_id:
                event_user_id = event.get('extendedProperties', {}).get('private', {}).get('user_id')
                if event_user_id != user_id:
                    return f"Error: Access denied. Event {event_id} does not belong to user {user_id}."
            
            return str(event)
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return f"An error occurred: {error}"

    def list_calendars(self, user_id: str = None) -> str:
        """
        List all calendars, optionally filtered by user access.
        """
        try:
            calendar_list = self.service.calendarList().list().execute()
            calendars = calendar_list.get("items", [])
            if not calendars:
                return "No calendars found."
            
            # For now, return all calendars but note user context
            if user_id:
                return f"Calendars accessible to user {user_id}: {str(calendars)}"
            else:
                return str(calendars)
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return f"An error occurred: {error}"

# Singleton instance for easy access
_calendar_client = None

def get_calendar_client() -> GoogleCalendarClient:
    """
    Get or create the Google Calendar client instance.
    """
    global _calendar_client
    if _calendar_client is None:
        _calendar_client = GoogleCalendarClient()
    return _calendar_client
