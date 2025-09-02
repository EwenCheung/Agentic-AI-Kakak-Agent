# Google Calendar MCP Integration Setup

This document explains how to set up the Google Calendar MCP integration for your scheduler agent.

## Prerequisites

1. Node.js (for the MCP server)
2. Google Cloud Project with Calendar API enabled
3. OAuth 2.0 credentials for Desktop Application

## Setup Steps

### 1. Google Cloud Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the [Google Calendar API](https://console.cloud.google.com/apis/library/calendar-json.googleapis.com)
4. Create OAuth 2.0 credentials:
   - Go to "Credentials" → "Create Credentials" → "OAuth client ID"
   - Choose "Desktop app" as the application type
   - Download the credentials JSON file
5. Add your email as a test user in the OAuth consent screen

### 2. Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update the `.env` file with your credentials:
   ```
   GOOGLE_CALENDAR_CREDENTIALS_PATH=/absolute/path/to/your/gcp-oauth.keys.json
   ```

### 3. Install Dependencies

```bash
# Install Python dependencies
source venv/bin/activate
pip install -r requirements.txt

# Install Google Calendar MCP server globally
npm install -g @cocal/google-calendar-mcp
```

### 4. Authentication

Run the authentication flow:
```bash
export GOOGLE_OAUTH_CREDENTIALS="/path/to/your/gcp-oauth.keys.json"
npx @cocal/google-calendar-mcp auth
```

Follow the browser prompt to complete OAuth authentication.

### 5. Test the Integration

You can now use your scheduler agent with real Google Calendar integration. The following tools are available:

- `check_availability(date, time)` - Check if a time slot is available
- `schedule_event(title, date, time, duration)` - Create new events
- `get_empty_slots(date)` - Find free time slots
- `cancel_event(event_id)` - Delete events
- `list_events(date)` - List events for a date
- `update_event(event_id, ...)` - Update existing events
- `search_events(query)` - Search for events

## Available MCP Tools

The integration uses the following MCP tools:
- `get-freebusy` - Check availability
- `create-event` - Create events
- `delete-event` - Delete events
- `list-events` - List events
- `update-event` - Update events
- `search-events` - Search events

## Troubleshooting

1. **Authentication Issues**: 
   - Ensure credentials file path is absolute
   - Make sure you're added as a test user
   - Try deleting tokens and re-authenticating

2. **MCP Connection Issues**:
   - Verify Node.js is installed
   - Check that npx can find the MCP server
   - Ensure environment variables are set correctly

3. **Permission Errors**:
   - Verify Google Calendar API is enabled
   - Check OAuth scopes include calendar access
   - Ensure credentials are for Desktop Application type

## Moving to Production

To avoid weekly token expiration:
1. Go to Google Cloud Console → "APIs & Services" → "OAuth consent screen"
2. Click "PUBLISH APP" and confirm
3. Tokens will no longer expire weekly (but Google will show unverified app warning)
