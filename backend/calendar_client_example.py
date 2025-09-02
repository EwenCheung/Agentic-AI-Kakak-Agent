"""
Google Calendar MCP Client Usage Example

This example demonstrates how to use the Google Calendar client
to perform various calendar operations.
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append('/Users/alvinsaw/Documents/GitHub/Agentic-AI-Kakak-Agent/backend')

from src.services.calendar_client import get_calendar_client
from datetime import datetime, timedelta

async def main():
    """
    Example usage of the Google Calendar MCP client.
    """
    print("🗓️ Google Calendar MCP Client Example")
    print("=" * 50)
    
    # Initialize the client
    client = get_calendar_client()
    
    try:
        # 1. List all calendars
        print("\n📅 1. Listing all calendars:")
        calendars = await client.list_calendars()
        print(calendars)
        
        # 2. List today's events
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"\n📋 2. Events for today ({today}):")
        events = await client.list_events(today)
        print(events)
        
        # 3. Check free/busy for next 2 hours
        now = datetime.now()
        start_time = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time = (now + timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        print(f"\n⏰ 3. Free/busy status from {start_time} to {end_time}:")
        freebusy = await client.get_free_busy(start_time, end_time)
        print(freebusy)
        
        # 4. Create a test event (uncomment to actually create)
        # tomorrow = (datetime.now() + timedelta(days=1))
        # start_datetime = tomorrow.replace(hour=14, minute=0, second=0).strftime('%Y-%m-%dT%H:%M:%SZ')
        # end_datetime = tomorrow.replace(hour=15, minute=0, second=0).strftime('%Y-%m-%dT%H:%M:%SZ')
        # 
        # print(f"\n📝 4. Creating test event for tomorrow:")
        # result = await client.create_event(
        #     title="Test Event from MCP Client",
        #     start_datetime=start_datetime,
        #     end_datetime=end_datetime,
        #     description="This is a test event created using the MCP client"
        # )
        # print(result)
        
        # 5. Search for events
        print(f"\n🔍 5. Searching for events containing 'meeting':")
        search_results = await client.search_events("meeting")
        print(search_results)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n✅ Client example completed successfully!")
    return True

def sync_example():
    """
    Example of how to use the client in synchronous code.
    """
    from src.services.calendar_client import run_async_calendar_operation
    
    print("\n🔄 Synchronous Usage Example:")
    print("=" * 40)
    
    try:
        client = get_calendar_client()
        
        # Use the synchronous wrapper
        today = datetime.now().strftime('%Y-%m-%d')
        result = run_async_calendar_operation(
            client.list_events(today)
        )
        print(f"Today's events: {result}")
        
    except Exception as e:
        print(f"❌ Error in sync example: {e}")

if __name__ == "__main__":
    # Set up environment
    os.environ.setdefault(
        'GOOGLE_CALENDAR_CREDENTIALS_PATH',
        '/Users/alvinsaw/Documents/GitHub/Agentic-AI-Kakak-Agent/backend/google-cloud-credential/client_secret_810895084057-vet4ghnhkk03j68k1994d7gobjm7tecl.apps.googleusercontent.com.json'
    )
    
    # Run async example
    success = asyncio.run(main())
    
    if success:
        # Run sync example
        sync_example()
    
    print("\n🎉 All examples completed!")
