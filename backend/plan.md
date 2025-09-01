# Kakak Agent Improvement Plan

This document outlines a clear plan for improving the structure, workflow, and tool allocation of the Kakak Agent system.

## 1. Agent Roles and Responsibilities

### Orchestrator Agent ("Kakak")
- **Purpose:** To act as the central coordinator, understanding user intent and delegating tasks to the appropriate specialist agent.
- **Responsibilities:**
    - Analyze incoming user requests to determine their intent.
    - Route requests to the correct specialist agent (Chat, Scheduler, Ticketing, or Daily Digest).
    - Manage the conversation flow between the user and the specialist agents.
    - Consolidate responses from specialist agents and present them to the user.
    - Ensure that all actions are aligned with the user's goals and company policies.

### Chat Agent
- **Purpose:** To handle direct conversations with the user, answer general questions, and provide information from the knowledge base.
- **Responsibilities:**
    - Engage in friendly and professional conversation with users.
    - Use the knowledge base to answer frequently asked questions.
    - Escalate complex requests to the Orchestrator for delegation to specialist agents.
    - Maintain the context of the conversation.

### Scheduler Agent
- **Purpose:** To manage all scheduling-related tasks, including creating, modifying, and canceling events.
- **Responsibilities:**
    - Check for calendar availability.
    - Schedule new events and appointments.
    - Reschedule or cancel existing events.
    - List upcoming events for a given day or week.

### Ticketing Agent
- **Purpose:** To manage the entire lifecycle of support tickets, from creation to resolution.
- **Responsibilities:**
    - Create new support tickets based on user issues.
    - Check the status of existing tickets.
    - Update tickets with new information.
    - Close tickets upon resolution.
    - Escalate tickets to human agents when necessary.

### Daily Digest Agent
- **Purpose:** To provide users with a summary of their daily activities and important information.
- **Responsibilities:**
    - Gather information about the user's schedule, open tickets, and recent communications.
    - Consolidate the information into a concise and easy-to-read daily digest.
    - Present the digest to the user upon request.

## 2. Workflow

### High-Level Workflow
1.  A user sends a message via WhatsApp or another channel.
2.  The **Orchestrator Agent** receives the message and analyzes its intent.
3.  The **Orchestrator** delegates the task to the appropriate specialist agent.
4.  The specialist agent executes the task using its tools.
5.  The specialist agent returns the result to the **Orchestrator**.
6.  The **Orchestrator** formats the response and sends it to the user.

### Detailed Workflow Example (Booking a Meeting)
1.  **User:** "Hi, I'd like to book a meeting with the sales team tomorrow at 10 am."
2.  **Orchestrator:** Analyzes the intent as "scheduling" and delegates to the **Scheduler Agent**.
3.  **Scheduler Agent:** Uses the `check_availability` tool to see if 10 am is free.
4.  **Scheduler Agent:** The slot is available. It uses the `schedule_event` tool to book the meeting.
5.  **Scheduler Agent:** Returns a confirmation message to the **Orchestrator**.
6.  **Orchestrator:** Sends a confirmation message to the user: "Your meeting with the sales team has been booked for tomorrow at 10 am."

## 3. Tool Allocation and Refinements

### Orchestrator Agent
- **Tools:** `src/agent/orchestrator_agent/tools/orchestrator_tools.py`
    - **`delegate_task(agent_name: str, task: str)`:** To send a task to a specialist agent.
    - **`send_user_response(message: str)`:** To send a final response to the user.
- **Rationale:** The Orchestrator should only have tools for delegation and communication. It should not have direct access to the tools of the specialist agents.

### Chat Agent
- **Tools:** `src/agent/chat_agent/tools/chat_tools.py`
    - **`search_knowledge_base(query: str)`:** To answer general questions.
    - **`retrieve_conversation_history(phone_number: str)`:** To retrieve the past conversation history with the user.
- **Rationale:** The Chat Agent's primary role is to provide information and maintain conversational context. It should not have tools for scheduling, ticketing, or other specialized tasks. It should also not be able to send messages directly, but rather return a proposed message to the orchestrator.

### Scheduler Agent
- **Tools:** `src/agent/scheduler_agent/tools/calendar_tools.py`
    - `check_availability(date: str, time: str)`
    - `schedule_event(title: str, date: str, time: str, duration: int)`
    - `get_empty_slots(date: str)`
    - `cancel_event(event_id: str)`
    - `list_events(date: str)`
    - `update_event(event_id: str, title: str = None, date: str = None, time: str = None, duration: int = None)`
- **Rationale:** This is a comprehensive and appropriate set of tools for a scheduling agent. The `update_event` tool is optional and could be replaced by a combination of `cancel_event` and `schedule_event`.

### Ticketing Agent
- **Tools:** `src/agent/ticketing_agent/tools/ticketing_tools.py`
    - `create_ticket(issue: str, priority: str)`
    - `check_ticket_status(ticket_id: str)`
    - `update_ticket(ticket_id: str, update_info: str)`
    - `close_ticket(ticket_id: str)`
    - `list_open_tickets()`
    - `assign_ticket(ticket_id: str, agent_name: str)`
    - `escalate_ticket(ticket_id: str, reason: str)`
    - `get_ticket_details(ticket_id: str)`
    - `check_for_existing_ticket(issue_description: str)`
- **Rationale:** This is a comprehensive and appropriate set of tools for a ticketing agent. The `check_for_existing_ticket` tool is crucial to prevent duplicate tickets.

### Daily Digest Agent
- **Tools:** `src/agent/daily_digest_agent/tools/daily_digest_tools.py`
    - `get_todays_events()`
    - `get_open_tickets_summary()`
    - `get_recent_high_priority_communications()`
- **Rationale:** These tools are well-suited for gathering the information needed for a daily digest.

### Shared Toolkit
- **`guardrail.py`:** `src/agent/toolkit/guardrail.py`
    - **`check_guardrail(response: str)`:** This tool should be used by the Orchestrator to check all responses before they are sent to the user.

## 4. Comparison with Current Tools

- **Chat Agent:**
    - **Previously:** `sent_whatsapp_message`, `check_previous_messages`.
    - **Proposed:** `search_knowledge_base`, `retrieve_conversation_history`.
    - **Reasoning:** The Chat Agent should not be able to send messages directly. This should be the responsibility of the Orchestrator. The ability to retrieve conversation history is important for maintaining context.
- **Daily Digest Agent:**
    - **Current:** `get_todays_events`, `get_open_tickets_summary`, `get_recent_high_priority_communications`.
    - **Proposed:** No changes. The current tools are appropriate.
- **Scheduler Agent:**
    - **Current & Proposed:** No changes. The current tools are appropriate, with the note that `update_event` could be simplified.
- **Ticketing Agent:**
    - **Current & Proposed:** Added `check_for_existing_ticket` to prevent duplicate tickets.

## 5. Next Steps

1.  **Implement the `plan.md` changes:**
    - Consolidate the chat agent's tools into `src/agent/chat_agent/tools/chat_tools.py`.
    - Add the `phone_number` parameter to the `retrieve_conversation_history` tool and update the relevant agent functions.
    - Add the `check_for_existing_ticket` tool to the Ticketing Agent.
    - Update the Orchestrator's prompt to use the `check_for_existing_ticket` tool before creating a new ticket.
    - Create tools for the Orchestrator agent.
2.  **Implement Tool Logic:**
    - Implement the actual logic for each tool (e.g., connect to Google Calendar API, a ticketing system, etc.).
3.  **Develop Backend Integration:**
    - Build the backend logic to handle incoming messages, route them to the Orchestrator, and manage the agent lifecycle.
4.  **Develop Frontend Dashboard:**
    - Create the frontend dashboard for businesses to configure and monitor the Kakak Agent.
5.  **Testing:**
    - Thoroughly test the entire system to ensure it is working as expected.
