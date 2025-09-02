"""
Google Calendar MCP Client

A robust client for communicating with the Google Calendar MCP server.
Provides high-level methods for calendar operations.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from ..config.settings import settings

# Set up logging
logger = logging.getLogger(__name__)

class GoogleCalendarClient:
    """
    A client for interacting with Google Calendar through the MCP server.
    
    This client provides a high-level interface for calendar operations,
    handling the MCP communication and error handling internally.
    """
    
    def __init__(self, credentials_path: str = None):
        """
        Initialize the Google Calendar client.
        
        Args:
            credentials_path (str, optional): Path to Google OAuth credentials.
                                            Defaults to settings value.
        """
        self.credentials_path = credentials_path or settings.GOOGLE_CALENDAR_CREDENTIALS_PATH
        if not self.credentials_path:
            raise ValueError("Google Calendar credentials path not configured")
    
    async def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Call an MCP tool and return the result.
        
        Args:
            tool_name (str): Name of the MCP tool to call
            arguments (Dict[str, Any]): Arguments to pass to the tool
            
        Returns:
            str: The tool result as a string
            
        Raises:
            Exception: If the MCP call fails
        """
        server_params = StdioServerParameters(
            command="npx",
            args=["@cocal/google-calendar-mcp"],
            env={"GOOGLE_OAUTH_CREDENTIALS": self.credentials_path}
        )
        
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the server
                    await session.initialize()
                    
                    # Call the tool
                    result = await session.call_tool(tool_name, arguments)
                    
                    # Extract text content from result
                    if hasattr(result, 'content') and result.content:
                        if isinstance(result.content, list) and len(result.content) > 0:
                            content_item = result.content[0]
                            if hasattr(content_item, 'text'):
                                return content_item.text
                            elif isinstance(content_item, dict) and 'text' in content_item:
                                return content_item['text']
                        return str(result.content)
                    return str(result)
        except Exception as e:
            logger.error(f"MCP tool call failed for {tool_name}: {str(e)}")
            raise Exception(f"Calendar operation failed: {str(e)}")
    
    async def list_calendars(self) -> str:
        """
        List all available calendars.
        
        Returns:
            str: List of calendars with details
        """
        return await self._call_mcp_tool("list-calendars", {})
    
    async def list_events(self, 
                         start_date: str, 
                         end_date: str = None,
                         calendar_id: str = "primary") -> str:
        """
        List events in a date range.
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format. 
                                    Defaults to same day as start_date.
            calendar_id (str): Calendar ID to query. Defaults to "primary".
            
        Returns:
            str: List of events
        """
        if end_date is None:
            end_date = start_date
            
        start_time = f"{start_date}T00:00:00Z"
        end_time = f"{end_date}T23:59:59Z"
        
        arguments = {
            "calendarId": calendar_id,
            "timeMin": start_time,
            "timeMax": end_time
        }
        
        return await self._call_mcp_tool("list-events", arguments)
    
    async def create_event(self,
                          title: str,
                          start_datetime: str,
                          end_datetime: str,
                          description: str = None,
                          calendar_id: str = "primary") -> str:
        """
        Create a new calendar event.
        
        Args:
            title (str): Event title/summary
            start_datetime (str): Start time in ISO format (YYYY-MM-DDTHH:MM:SSZ)
            end_datetime (str): End time in ISO format (YYYY-MM-DDTHH:MM:SSZ)
            description (str, optional): Event description
            calendar_id (str): Calendar ID. Defaults to "primary".
            
        Returns:
            str: Event creation result
        """
        arguments = {
            "calendarId": calendar_id,
            "summary": title,
            "start": {"dateTime": start_datetime},
            "end": {"dateTime": end_datetime}
        }
        
        if description:
            arguments["description"] = description
            
        return await self._call_mcp_tool("create-event", arguments)
    
    async def update_event(self,
                          event_id: str,
                          title: str = None,
                          start_datetime: str = None,
                          end_datetime: str = None,
                          description: str = None,
                          calendar_id: str = "primary") -> str:
        """
        Update an existing calendar event.
        
        Args:
            event_id (str): ID of the event to update
            title (str, optional): New event title
            start_datetime (str, optional): New start time in ISO format
            end_datetime (str, optional): New end time in ISO format
            description (str, optional): New event description
            calendar_id (str): Calendar ID. Defaults to "primary".
            
        Returns:
            str: Event update result
        """
        arguments = {
            "calendarId": calendar_id,
            "eventId": event_id
        }
        
        if title:
            arguments["summary"] = title
        if start_datetime:
            arguments["start"] = {"dateTime": start_datetime}
        if end_datetime:
            arguments["end"] = {"dateTime": end_datetime}
        if description:
            arguments["description"] = description
            
        return await self._call_mcp_tool("update-event", arguments)
    
    async def delete_event(self, event_id: str, calendar_id: str = "primary") -> str:
        """
        Delete a calendar event.
        
        Args:
            event_id (str): ID of the event to delete
            calendar_id (str): Calendar ID. Defaults to "primary".
            
        Returns:
            str: Deletion result
        """
        arguments = {
            "calendarId": calendar_id,
            "eventId": event_id
        }
        
        return await self._call_mcp_tool("delete-event", arguments)
    
    async def search_events(self, query: str, calendar_id: str = "primary") -> str:
        """
        Search for events by text query.
        
        Args:
            query (str): Search query
            calendar_id (str): Calendar ID. Defaults to "primary".
            
        Returns:
            str: Search results
        """
        arguments = {
            "calendarId": calendar_id,
            "q": query
        }
        
        return await self._call_mcp_tool("search-events", arguments)
    
    async def get_free_busy(self,
                           start_time: str,
                           end_time: str,
                           calendar_ids: List[str] = None) -> str:
        """
        Get free/busy information for calendars.
        
        Args:
            start_time (str): Start time in ISO format
            end_time (str): End time in ISO format
            calendar_ids (List[str], optional): List of calendar IDs. 
                                              Defaults to ["primary"].
            
        Returns:
            str: Free/busy information
        """
        if calendar_ids is None:
            calendar_ids = ["primary"]
            
        items = [{"id": cal_id} for cal_id in calendar_ids]
        
        arguments = {
            "timeMin": start_time,
            "timeMax": end_time,
            "items": items
        }
        
        return await self._call_mcp_tool("get-freebusy", arguments)
    
    async def get_event_details(self, event_id: str, calendar_id: str = "primary") -> str:
        """
        Get detailed information about a specific event.
        
        Args:
            event_id (str): ID of the event
            calendar_id (str): Calendar ID. Defaults to "primary".
            
        Returns:
            str: Event details
        """
        arguments = {
            "calendarId": calendar_id,
            "eventId": event_id
        }
        
        return await self._call_mcp_tool("get-event", arguments)

# Singleton instance for easy access
_calendar_client = None

def get_calendar_client(credentials_path: str = None) -> GoogleCalendarClient:
    """
    Get or create the Google Calendar client instance.
    
    Args:
        credentials_path (str, optional): Path to credentials file
        
    Returns:
        GoogleCalendarClient: The client instance
    """
    global _calendar_client
    if _calendar_client is None:
        _calendar_client = GoogleCalendarClient(credentials_path)
    return _calendar_client

# Synchronous wrapper functions for use in strands tools
def run_async_calendar_operation(coro):
    """
    Run an async calendar operation synchronously.
    
    Args:
        coro: Coroutine to run
        
    Returns:
        The result of the coroutine
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(coro)
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Async calendar operation failed: {str(e)}")
        return f"Calendar operation failed: {str(e)}"
