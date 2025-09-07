# Kakak Agent Architecture and Workflow Plan

This document outlines the architecture, message flow, and responsibilities of the Kakak AI Agent system, clarifying interactions between end-users, the agent, and business users.

## 1. Overall Workflow

The Kakak Agent system serves as a customer support solution for businesses, enabling them to automate interactions with their end-users.

**Key User Types:**

*   **End-User:** The customer of the business (e.g., a person messaging via Telegram).
*   **Business User:** Our client, who purchases and configures the Kakak Agent, and monitors its performance via a dashboard.

**High-Level Flow:**

```mermaid
graph TD
    EndUser[End-User (Telegram)] --> TelegramAPI[Telegram API]
    TelegramAPI --> Webhook[Webhook (FastAPI Endpoint)]
    Webhook --> OrchestratorAgent[Orchestrator Agent]
    OrchestratorAgent --> SubAgent[Specialized Sub-Agent]
    SubAgent --> TelegramAPI_Out[Telegram API (Outgoing)]
    TelegramAPI_Out --> EndUser

    OrchestratorAgent --> Database[Agent Database]
    SubAgent --> Database
    Database --> BusinessDashboard[Business Dashboard]
    BusinessDashboard --> BusinessUser[Business User]
```

## 2. Message Flow

Messages enter the system via Telegram webhooks, are processed by the orchestrator and sub-agents, and responses are delivered back to the end-user via Telegram. Business users monitor activity through a separate dashboard.

**Detailed Message Flow:**

1.  **Incoming End-User Message (Telegram):**
    *   An End-User sends a message to the configured Telegram bot.
    *   Telegram, via a pre-configured webhook, sends this message as an update to a specific FastAPI endpoint in our application (`/telegram_webhook`).
2.  **API Endpoint Reception:**
    *   The FastAPI application receives the incoming message data from Telegram at the `/telegram_webhook` endpoint.
    *   The endpoint first checks if the update contains a text message. Other message types are currently ignored.
    *   It extracts the `chat_id`, message `text`, and the user's `first_name`.
3.  **Customer and Message Logging:**
    *   The endpoint queries the database for a `Customer` with the given `telegram_chat_id`. If no customer is found, a new one is created.
    *   The incoming text message is logged in the `ConversationMessage` table and associated with the customer.
4.  **Orchestrator Agent Activation (Background Task):**
    *   To ensure a fast response to the Telegram webhook, the endpoint triggers the `orchestrator_assistant` as a background task.
    *   The user's message `text` is passed as the `query` to the orchestrator.
5.  **Intent Analysis & Delegation:**
    *   The `orchestrator_agent` analyzes the query using its system prompt and available sub-agents to determine the End-User's intent.
    *   It then directly calls the appropriate sub-agent's function (e.g., `chat_assistant`, `ticketing_assistant`).
6.  **Sub-Agent Execution & Response Generation:**
    *   The chosen sub-agent executes the task using its specialized tools.
    *   If a response to the end-user is required, the `chat_agent` is typically invoked.
7.  **Response Delivery (to End-User):**
    *   The `chat_agent` uses its `send_message` tool, which leverages the Telegram Bot API, to send the reply directly back to the End-User.
    *   The `send_message` tool also logs the outgoing agent message to the `ConversationMessage` table.
    *   The initial webhook call returns a quick HTTP 200 OK to Telegram, while the actual agent response is delivered asynchronously.
8.  **Business Dashboard Monitoring:**
    *   Business users access a separate dashboard application.
    *   This dashboard retrieves data (e.g., daily digests, ticket statistics, customer conversation summaries) directly from our `agent.db` database or via dedicated API endpoints in our FastAPI application, such as:
        *   `/dashboard/tickets/open`: To get a list of all open tickets.
        *   `/dashboard/customers/summaries`: To get a list of customers with their conversation summaries.
    *   The agents themselves are not directly involved in rendering the dashboard.

## 3. Agent Breakdown

The system comprises a central orchestrator agent and several specialized sub-agents.

### 3.1. Orchestrator Agent (`orchestrator_agent`)

*   **Role/Purpose:** The central coordinator. Understands End-User requests, determines intent, and delegates tasks to the most appropriate specialist sub-agent. It ensures a smooth workflow and facilitates the End-User's interaction with the specialized agents.
*   **Key Functions/Capabilities:**
    *   Analyzes End-User messages to determine intent.
    *   Delegates tasks by directly calling sub-agent functions.
    *   Manages the overall interaction flow from incoming message to sub-agent processing.
*   **Tools:** The orchestrator agent has access to all sub-agent functions as its tools.
    *   `chat_assistant`: Delegates general conversation, knowledge base queries, and customer conversation summary requests.
    *   `scheduler_assistant`: Delegates calendar management tasks (scheduling, rescheduling, canceling events).
    *   `ticketing_assistant`: Delegates support ticket management tasks (creating, updating, tracking, closing tickets).
    *   `daily_digest_assistant`: Delegates requests for daily summaries of events and tickets.

### 3.2. Chat Agent (`chat_agent`)

*   **Role/Purpose:** Handles general conversations, answers questions from the knowledge base, and manages customer conversation logging and summarization. It is the primary agent for direct communication with End-Users via Telegram.
*   **Key Functions/Capabilities:**
    *   Interacts with Telegram (sending/receiving messages).
    *   Logs all incoming and outgoing messages to the database.
    *   Generates summaries of customer conversations.
*   **Tools:**
    *   **Telegram Tool (from `telegram_tools.py`):**
        *   `send_message`: Send a message to a specific chat using the Telegram Bot API (logs outgoing messages).
    *   **Summarization Tool (from `summarization_tools.py`):**
        *   `summarize_customer_conversation`: Summarizes the conversation history for a given customer and updates their record in the database.

### 3.3. Scheduler Agent (`scheduler_agent`)

*   **Role/Purpose:** Manages calendar events, including scheduling, rescheduling, and canceling.
*   **Key Functions/Capabilities:**
    *   Interacts with Google Calendar.
    *   Checks availability and finds empty slots.
*   **Tools (from `calendar_tools.py`):**
    *   `current_time`: Gets the current date and time.
    *   `check_availability`: Checks if a specific date is available.
    *   `schedule_event`: Schedules a new calendar event.
    *   `list_events`: Lists all events on a specific date.
    *   `get_empty_slots`: Finds empty slots on a specific date.
    *   `cancel_event`: Cancels a calendar event.
    *   `get_event_details`: Retrieves comprehensive details about a specific calendar event.
    *   `update_event`: Updates an existing calendar event.
    *   `search_events`: Searches for calendar events by a text query.
    *   `list_calendars`: Lists all available calendars.

### 3.4. Ticketing Agent (`ticketing_agent`)

*   **Role/Purpose:** Manages support tickets, including creation, status checks, updates, and escalation.
*   **Key Functions/Capabilities:**
    *   Interacts with the custom ticketing database (`agent.db`).
    *   Performs CRUD operations on tickets.
*   **Tools (from `ticketing_tools.py`):**
    *   `create_ticket`: Creates a new support ticket.
    *   `check_ticket_status`: Checks the status of a ticket.
    *   `update_ticket`: Updates a ticket with new information.
    *   `close_ticket`: Closes a ticket.
    *   `list_open_tickets`: Lists all open tickets.
    *   `assign_ticket`: Assigns a ticket to an agent.
    *   `escalate_ticket`: Escalates a ticket to high priority.
    *   `get_ticket_details`: Retrieves detailed information about a ticket.
    *   `check_for_existing_ticket`: Checks if a similar ticket already exists.

### 3.5. Daily Digest Agent (`daily_digest_agent`)

*   **Role/Purpose:** Provides a concise summary of the day's important events, open tickets, and high-priority communications. This content is primarily for Business Users via the dashboard.
*   **Key Functions/Capabilities:**
    *   Gathers information from the ticketing database and calendar.
    *   Summarizes key daily highlights.
*   **Tools (from `daily_digest_tools.py`):**
    *   `get_todays_events`: Retrieves a summary of today's calendar events (directly from Google Calendar).
    *   `get_open_tickets_summary`: Retrieves a summary of open support tickets from the database.
    *   `get_recent_high_priority_communications`: Retrieves a summary of recent high-priority communications (currently, new high-priority tickets from the database).

## 4. Database Usage (`agent.db`)

The system utilizes a SQLite database named `agent.db` (located in `src/database/sql_database/`) to store persistent data for various agent operations.

*   **`Ticket` Table:** Stores information about support tickets.
*   **`Customer` Table:** Stores customer details, including their `telegram_chat_id` and name. This table also contains the conversation memory:
    *   `conversation_history`: A `TEXT` field that stores the raw, running log of the most recent back-and-forth messages.
    *   `conversation_summary`: A `TEXT` field that stores a condensed summary of older parts of the conversation. As the `conversation_history` grows, it is periodically summarized and merged into this field, keeping the context manageable for the agent.

This comprehensive plan outlines the current state and intended functionality of the Kakak Agent system.