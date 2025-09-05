# Google Calendar MCP Client Documentation

## Overview

The Google Calendar MCP Client provides a clean, high-level interface for interacting with Google Calendar through the Model Context Protocol (MCP) server. This client handles all the complexity of MCP communication and provides simple async/sync methods for calendar operations.

## Architecture

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Calendar Tools    │───▶│  Calendar Client     │───▶│   MCP Server        │
│  (Strands Tools)    │    │  (Python)            │    │  (Node.js)          │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
                                       │                           │
                                       ▼                           ▼
                           ┌──────────────────────┐    ┌─────────────────────┐
                           │   Async Operations   │    │  Google Calendar    │
                           │   Sync Wrappers      │    │      API            │
                           └──────────────────────┘    └─────────────────────┘
```

## Client Features

### ✅ **Core Functionality**
- **Calendar Management**: List and access multiple calendars
- **Event Operations**: Create, read, update, delete events
- **Availability Checking**: Free/busy queries
- **Event Search**: Text-based event searching
- **Async/Sync Support**: Both async and synchronous interfaces

### 🔧 **Technical Features**
- **Error Handling**: Robust error handling with meaningful messages
- **Logging**: Built-in logging for debugging
- **Singleton Pattern**: Efficient resource management
- **MCP Abstraction**: Hides MCP complexity from users

## Usage Examples

### Basic Usage

```python
from src.services.calendar_client import get_calendar_client
import asyncio

async def example():
    client = get_calendar_client()
    
    # List events for today
    events = await client.list_events("2025-09-02")
    print(events)
    
    # Create an event
    result = await client.create_event(
        title="Meeting with Client",
        start_datetime="2025-09-03T14:00:00Z",
        end_datetime="2025-09-03T15:00:00Z"
    )
```

### Synchronous Usage (for Strands Tools)

```python
from src.services.calendar_client import get_calendar_client, run_async_calendar_operation

def sync_function():
    client = get_calendar_client()
    
    # Use the sync wrapper
    result = run_async_calendar_operation(
        client.list_events("2025-09-02")
    )
    return result
```

## Available Methods

### Calendar Operations

#### `list_calendars()`
Lists all available calendars with details.

**Returns:** String with calendar information including IDs, names, timezones, and permissions.

#### `list_events(start_date, end_date=None, calendar_id="primary")`
Lists events in a date range.

**Parameters:**
- `start_date` (str): Start date in YYYY-MM-DD format
- `end_date` (str, optional): End date, defaults to start_date
- `calendar_id` (str): Calendar ID, defaults to "primary"

**Returns:** String with event details

#### `create_event(title, start_datetime, end_datetime, description=None, calendar_id="primary")`
Creates a new calendar event.

**Parameters:**
- `title` (str): Event title
- `start_datetime` (str): Start time in ISO format (YYYY-MM-DDTHH:MM:SSZ)
- `end_datetime` (str): End time in ISO format
- `description` (str, optional): Event description
- `calendar_id` (str): Target calendar ID

**Returns:** Event creation confirmation

#### `update_event(event_id, title=None, start_datetime=None, end_datetime=None, description=None, calendar_id="primary")`
Updates an existing event.

**Parameters:**
- `event_id` (str): ID of event to update
- Other parameters are optional updates

**Returns:** Update confirmation

#### `delete_event(event_id, calendar_id="primary")`
Deletes a calendar event.

**Returns:** Deletion confirmation

#### `search_events(query, calendar_id="primary")`
Searches for events by text query.

**Returns:** Search results

#### `get_free_busy(start_time, end_time, calendar_ids=None)`
Gets free/busy information for calendars.

**Parameters:**
- `start_time` (str): Start time in ISO format
- `end_time` (str): End time in ISO format
- `calendar_ids` (List[str], optional): Calendar IDs to check

**Returns:** Free/busy information

#### `get_event_details(event_id, calendar_id="primary")`
Gets detailed information about a specific event.

**Returns:** Detailed event information

## Configuration

### Environment Setup

The client requires the Google Calendar credentials path to be configured:

```bash
# In .env file
GOOGLE_CALENDAR_CREDENTIALS_PATH=/path/to/your/credentials.json
```

### Dependencies

- `mcp`: Model Context Protocol library
- `asyncio`: For async operations
- Google Calendar MCP Server (Node.js package)

## Error Handling

The client provides comprehensive error handling:

```python
try:
    result = await client.create_event(...)
except Exception as e:
    print(f"Calendar operation failed: {e}")
```

## Integration with Strands Tools

The calendar tools in `src/agent/scheduler_agent/tools/calendar_tools.py` use this client:

```python
@tool
def list_events(date: str) -> str:
    client = get_calendar_client()
    return run_async_calendar_operation(
        client.list_events(date)
    )
```

## Best Practices

1. **Use the singleton**: Always use `get_calendar_client()` instead of creating new instances
2. **Handle errors**: Wrap calendar operations in try-catch blocks
3. **Use ISO format**: Always use ISO datetime format for timestamps
4. **Async preferred**: Use async methods when possible for better performance
5. **Logging**: Enable logging to troubleshoot issues

## Troubleshooting

### Common Issues

1. **"Credentials not found"**: Check `GOOGLE_CALENDAR_CREDENTIALS_PATH` environment variable
2. **"MCP server failed"**: Ensure Node.js and the MCP server are installed
3. **"Authentication failed"**: Re-run the auth flow: `npx @cocal/google-calendar-mcp auth`
4. **"TaskGroup errors"**: Usually indicates parameter format issues

### Debug Mode

Enable logging for detailed debugging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## File Structure

```
backend/
├── src/
│   ├── services/
│   │   └── calendar_client.py          # Main client implementation
│   └── agent/scheduler_agent/tools/
│       └── calendar_tools.py           # Strands tools using the client
├── calendar_client_example.py          # Usage examples
└── .env                                # Configuration
```

## Dependencies Installation

```bash
# Install Python dependencies
pip install mcp

# Install Node.js MCP server
npm install -g @cocal/google-calendar-mcp
```

This client provides a robust, production-ready interface for Google Calendar integration in your AI agent system.
