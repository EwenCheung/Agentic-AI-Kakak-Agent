Project Name : Kakak Agent ?? Extension

We do B to B , customer is B to C

We need a management platform for our customer, our customer can link their whatsapp and telegram etc by our platform.
Our customer is business ( they can set limitation on what AI can do ) ( tick box , can auto book slot ) 


Business Use Case
AI helper tool, provide the agent documents and link agent to do auto response for whatsapp ( whatsapp, RAG )

Create schedule arrangement ( tool google calendar or outlook ) 
Example:
Customer: can i meet you on friday 7-9
“Agent check calender”
Agent : Yes I am free, book schedule , send confirmation

Ai Agent can’t solve then create a ticket, file the ticket and contact number, ticket shown in summarise ) ,  ( We make some restriction for AI , if hit restriction then connect to human. ) 

Summarise what is happening in the day, Agent will notify the user on what are the events for today and what’s important. ( Memory system)
	



Nice, Ewen 👍 your idea of Kakak Agent ?? Extension already has a strong foundation (WhatsApp auto-response + RAG + scheduling + escalation + daily summary). To stand out at a hackathon, you’ll want to add features that are creative, practical, and easy to demo live. Here are more ideas you can blend in:

🔑 Extra Creative & Helpful Features
1. Smart Contextual Replies
Instead of just RAG (retrieving documents), the agent can remember past conversations and reply in a personalized tone.


Example:


Customer: “Can I meet you Friday?”


Agent: “Sure! I remember last time you preferred morning slots—shall I book 9am?”



2. Multi-Channel Agent
Don’t limit to WhatsApp—your agent can auto-respond in Telegram, Slack, or Email too (cross-platform assistant).


Same memory + same schedule integration across all channels.



3. Voice + WhatsApp Integration
People can send a voice note, the agent transcribes and replies.



4. Smart Ticketing System with Priority
When AI cannot answer and escalates, it can tag ticket urgency:


🔴 Urgent: Customer complaint / critical bug


🟡 Medium: Booking request


🟢 Low: FAQ / info


Auto-create a summary for the human operator with the key details, saving time.



5. Daily Digest & Insights
Beyond just listing today’s meetings, agent can:


Highlight urgent tickets.


Show “customer sentiment trend” (positive vs negative).


Suggest “You forgot to reply to X yesterday.”


Almost like a morning briefing.




7. Fun / Personality Mode
Hackathon judges often like creativity + fun.


Give your Kakak Agent a local cultural twist (like Kakak = “big sis”).


Normal mode: Professional tone.


Kakak mode: Casual + warm, uses Singlish/Malay phrases. Example:


“Eh bro, you got meeting at 2pm, don’t be late hor 😆”




8. Knowledge Expansion
Users can upload PDFs or links, and Kakak Agent auto-digests into Q&A form for WhatsApp use.


E.g. product manual → AI chatbot instantly answers customer queries.



9. Multi-Agent Collaboration
Have “mini agents” for different jobs:


📅 Scheduler Agent ( outlook ) 


📝 Note-taking Agent 


🎟️ Ticketing Agent 


📢 Notification Agent 


They work together, like a team. This will impress hackathon judges because it shows modular design.



10. Analytics Dashboard
Simple web dashboard showing:


Number of queries handled.


Top customer questions.


Calendar view + ticket view.



🎯 Hackathon Edge
To impress:
Show a live demo: Judge sends WhatsApp msg → Kakak Agent replies → auto-books in Google Calendar → escalates a tricky one → dashboard updates instantly.


Add personality + fun factor. Judges like when it’s practical and memorable.















Division

Perfect 💡 you’ve got the right team mix (Frontend / AI / Backend).
 For hackathon success, the trick is clear modular division so you can move fast in parallel without blocking each other.
Here’s a breakdown tailored to your team skills:

🔧 3 Core Components
1. Frontend Platform (Shi Yang – SE/Web Expert)
🎯 Goal: Provide businesses (your customers) a management dashboard to configure & monitor Kakak Agent.
Core Features


WhatsApp / Telegram account linking (UI + API integration)


Configuration UI: checkboxes/sliders to set AI limits


✅ Auto-book schedule


✅ Auto-response scope (FAQ only vs free chat)


✅ Escalation rules


Ticket view (list of unresolved tickets with urgency colors)


Calendar view (synced with Google/Outlook)


Daily Digest page (summary of events, tickets, and insights)


Deliverables


Web UI mockup → then frontend pages


Defines the API contracts (what data to send to backend, what to receive back)



2. AI Agent Layer (Ewen – AI Engineer)
🎯 Goal: Build the brains of Kakak Agent using LangGraph/LangChain + memory.
Core Features


RAG pipeline: answer FAQs / business docs


Scheduling agent: check Google/Outlook API availability, confirm/book slots


Escalation logic: if restricted → create ticket in backend


Summarizer: generate daily digest (meetings, tickets, important updates)


Memory system: recall past customer chats for context


Fun Mode (Kakak personality toggle)


Deliverables


Modular agents:


📅 Scheduler Agent


📝 Knowledge QnA Agent


🎟️ Ticketing Agent


📢 Notification Agent


API endpoints → return structured responses to backend (JSON, not free text, so backend can format)



3. Backend Integration Layer (Alvin – Backend APIs)
🎯 Goal: Glue Frontend ↔ AI Layer ↔ External APIs together.
Core Features


Connectors:


WhatsApp API (Twilio/Meta Business API)


Telegram Bot API


Google Calendar / Outlook API


Ticket DB (store unresolved queries, escalation logs)


Message routing:


Receive WhatsApp/Telegram message → call AI Agent → send reply back


If escalation → save in DB + notify human via dashboard


Deliverables


REST APIs / WebSocket endpoints


Database schema for:


Users


Messages


Tickets


Events


Simple analytics aggregation (counts, trends)


Note : 
When the AI response to the user, do call of api to ( whatsapp those ) , reflect what the agent ask to do , i will ask agent to return in json format on what you need. You have to reflect the response from AI to UI. 

🔗 Workflow Example (End-to-End)
Customer sends (WhatsApp msg → backend receives)-(alvin) → (passes to AI Agent)-(ewen).


AI Agent decides (reply / book / escalate) - ewen.


Backend stores outcome in DB(TBC) + pushes result to Frontend dashboard(alvin).


Frontend shows business the live status (tickets, calendar, digest)(shiyang).





Priority : 
ShiYang : Draw UI
Alvin : Check on what format of input and output is for all the tools ( api / mcp ) 
Ewen : check on framework

