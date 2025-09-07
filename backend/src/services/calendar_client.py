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

from ..config.settings import settings

# Set up logging
logger = logging.getLogger(__name__)

def get_calendar_status() -> Dict[str, Any]:
    """Check if Google Calendar is configured and ready."""
    creds_path = settings.GOOGLE_CALENDAR_CREDENTIALS_PATH
    if not creds_path:
        return {"configured": False, "ready": False, "reason": "Missing GOOGLE_CALENDAR_CREDENTIALS_PATH"}
    
    if not os.path.exists(creds_path):
        return {"configured": True, "ready": False, "reason": f"Credentials file not found at: {creds_path}"}
        
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
        creds_path = settings.GOOGLE_CALENDAR_CREDENTIALS_PATH

        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(token_path, "w") as token:
                token.write(creds.to_json())
        
        return creds

    def list_events(self, start_date: str, end_date: str = None, calendar_id: str = "primary") -> str:
        """
        List events in a date range.
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
            
            return json.dumps(events)
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return f"An error occurred: {error}"

    def create_event(self, title: str, start_datetime: str, end_datetime: str, description: str = None, calendar_id: str = "primary") -> str:
        """
        Create a new calendar event.
        """
        event = {
            "summary": title,
            "description": description,
            "start": {
                "dateTime": start_datetime,
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": end_datetime,
                "timeZone": "UTC",
            },
        }

        try:
            event = self.service.events().insert(calendarId=calendar_id, body=event).execute()
            return f"Event created: {event.get('htmlLink')}"
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return f"An error occurred: {error}"

    def update_event(self, event_id: str, title: str = None, start_datetime: str = None, end_datetime: str = None, description: str = None, calendar_id: str = "primary") -> str:
        """
        Update an existing calendar event.
        """
        try:
            event = self.service.events().get(calendarId=calendar_id, eventId=event_id).execute()

            if title:
                event['summary'] = title
            if description:
                event['description'] = description
            if start_datetime:
                event['start']['dateTime'] = start_datetime
            if end_datetime:
                event['end']['dateTime'] = end_datetime

            updated_event = self.service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
            return f"Event updated: {updated_event.get('htmlLink')}"
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return f"An error occurred: {error}"

    def delete_event(self, event_id: str, calendar_id: str = "primary") -> str:
        """
        Delete a calendar event.
        """
        try:
            self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            return "Event deleted."
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return f"An error occurred: {error}"

    def search_events(self, query: str, calendar_id: str = "primary") -> str:
        """
        Search for events.
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
            
            return str(events)
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return f"An error occurred: {error}"

    def get_event_details(self, event_id: str, calendar_id: str = "primary") -> str:
        """
        Get details of a specific event.
        """
        try:
            event = self.service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            return str(event)
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return f"An error occurred: {error}"

    def list_calendars(self) -> str:
        """
        List all calendars.
        """
        try:
            calendar_list = self.service.calendarList().list().execute()
            calendars = calendar_list.get("items", [])
            if not calendars:
                return "No calendars found."
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
