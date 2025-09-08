# Kakak Agent - Intelligent Multi-Channel Customer Support System

**Team:** Three Musketeers -Ewen Cheung,Ng Shi Yang, Saw Yong Xuen

**Competition:** AI Hackathon 2025  

---

## 🎯 Problem Statement

Most chatbot only handles preset answers, so if a customer phrases a question differently, the bot gets stuck

Staff then have to manually check documents, reply, and update calendars — leading to delayed responses, missed bookings, and frustrated customers

- Handle multiple channels (Telegram, future: WhatsApp, Web Chat) 
- Understand context and maintain conversation memory
- Access and search through company knowledge bases
- Manage appointments and calendar scheduling
- Create and track support tickets
- Provide daily business insights and summaries

**Why This Matters:**
- 67% of customers expect 24/7 support availability
- Poor customer service costs businesses $75 billion annually in the US alone
- SMEs lose 30% of potential customers due to delayed response times
- Manual ticket management reduces productivity by 40%

---

## 💡 Solution Overview

**Kakak Agent** is an intelligent, multi-agent AI system that provides comprehensive customer support automation for businesses. Built on a sophisticated orchestrator-agent architecture, it seamlessly handles customer inquiries across multiple channels while integrating with business systems.

### Key Capabilities:
🤖 **Multi-Agent Intelligence** - Specialized agents for scheduling, ticketing, web search, and business insights  
📚 **Knowledge Base Integration** - RAG-powered document search and AI-driven responses  
🧠 **Conversation Memory** - Persistent context awareness across sessions using Mem0  
🌐 **Real-time Information** - Web search capabilities for current events and data  
�️ **Multi-Language Support** - Native conversations in 15+ languages powered by Claude 3.7 Sonnet
�📅 **Calendar Management** - Google Calendar integration for appointment scheduling  
🎫 **Smart Ticketing** - Automated ticket creation, tracking, and escalation  
📊 **Business Dashboard** - Real-time analytics and daily digest reports  
🔗 **Multi-Channel Support** - Telegram (implemented) with extensible architecture  
⚡ **Asynchronous Processing** - Background worker for optimal performance  

---

## 🛠️ Methodology

### Agent-Based Architecture
The system employs a **hierarchical multi-agent approach** where each agent specializes in specific domains:

1. **Orchestrator Agent**: Central coordinator with memory awareness that analyzes user intent and delegates to specialist agents
2. **Scheduler Agent**: Manages calendar operations and appointment booking with Google Calendar integration
3. **Ticketing Agent**: Creates, updates, and tracks support tickets with priority management
4. **Web Search Agent**: Retrieves real-time information from the internet when knowledge base is insufficient
5. **Daily Digest Agent**: Generates business insights and summaries from tickets and calendar events

### AI Technologies Used:
- **Large Language Models**: Amazon Bedrock (Claude 3 Haiku) for natural language processing
- **Vector Embeddings**: Amazon Titan Embed for semantic search
- **RAG (Retrieval-Augmented Generation)**: ChromaDB for knowledge base search
- **Document Processing**: Docling for PDF parsing and chunking
- **Agent Framework**: Strands AI for agent orchestration
- **Memory System**: Mem0 for conversation memory and user context persistence
- **Real-time Search**: Tavily API for current information retrieval

### Integration Strategy:
- **Telegram Bot API** for real-time messaging
- **Google Calendar API** for scheduling management  
- **SQLite Database** for data persistence and conversation memory
- **FastAPI** for scalable backend architecture
- **React Frontend** for business dashboard
- **Background Worker** for asynchronous message processing
- **Memory System (Mem0)** for conversation context and user preferences

---

## 🏗️ Technical Architecture

### System Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend (React)"
        Dashboard[Business Dashboard]
        Config[Configuration Panel]
        KB[Knowledge Base Upload]
        Channel[Channel Linking]
    end
    
    subgraph "Backend (FastAPI)"
        API[API Gateway]
        Worker[Background Worker]
        Queue[(Message Queue)]
        
        subgraph "Orchestrator Layer"
            Orchestrator[Memory-Aware Orchestrator]
            Memory[Mem0 Memory System]
        end
        
        subgraph "Specialist Agents"
            Scheduler[Scheduler Agent]
            Ticketing[Ticketing Agent]
            WebSearch[Web Search Agent]
            Digest[Daily Digest Agent]
        end
        
        subgraph "Data Layer"
            SQLite[(SQLite DB)]
            Vector[(ChromaDB)]
            Files[File Storage]
        end
    end
    
    subgraph "External Services"
        Telegram[Telegram API]
        GCal[Google Calendar API]
        Bedrock[Amazon Bedrock]
        Tavily[Tavily Search API]
    end
    
    subgraph "End Users"
        Customer[Customer via Telegram]
    end
    
    Customer --> Telegram
    Telegram --> API
    API --> Queue
    Worker --> Queue
    Worker --> Orchestrator
    
    Orchestrator --> Memory
    Orchestrator --> Scheduler
    Orchestrator --> Ticketing
    Orchestrator --> WebSearch
    Orchestrator --> Digest
    
    Scheduler --> GCal
    WebSearch --> Tavily
    Orchestrator --> Telegram
    
    Dashboard --> API
    Config --> API
    KB --> API
    Channel --> API
    
    Scheduler --> SQLite
    Ticketing --> SQLite
    Digest --> SQLite
    Orchestrator --> SQLite
    
    Orchestrator --> Vector
    Orchestrator --> Bedrock
    Scheduler --> Bedrock
    Ticketing --> Bedrock
    Digest --> Bedrock
    WebSearch --> Bedrock
    Memory --> Bedrock
```

### Technology Stack

#### Backend:
- **Framework**: FastAPI with async/await support
- **AI Platform**: Amazon Bedrock (Claude 3 Haiku, Titan Embeddings)
- **Agent Framework**: Strands AI for agent orchestration
- **Memory System**: Mem0 for conversation memory and context persistence
- **Vector Database**: ChromaDB for semantic search
- **Database**: SQLite with SQLAlchemy ORM
- **Document Processing**: Docling for PDF parsing
- **Real-time Search**: Tavily API for current information retrieval
- **Background Processing**: Async worker for message queue processing
- **API Integration**: Google Calendar API, Telegram Bot API

#### Frontend:
- **Framework**: React 18 with functional components
- **Styling**: Tailwind CSS for responsive design
- **State Management**: React hooks (useState, useEffect)
- **Routing**: React Router for SPA navigation
- **HTTP Client**: Fetch API for backend communication

#### Infrastructure:
- **Development**: Python 3.11+, Node.js, npm
- **Environment**: Virtual environment management
- **Configuration**: Environment variables and database-stored configs
- **File Handling**: Multi-file upload with content type detection
- **Message Processing**: SQLite-based queue with background worker
- **Memory Storage**: Persistent conversation context via Mem0

---

## 🎁 Benefits Delivered

### For End Customers:
- **24/7 Availability**: Instant responses to inquiries anytime
- **Intelligent Responses**: Context-aware conversations with access to company knowledge
- **Seamless Scheduling**: Easy appointment booking through natural language
- **Multi-Channel Access**: Consistent experience across communication platforms

### Technical Benefits:
- **Modular Architecture**: Easy to extend with new agents and channels
- **Cloud-Native**: Leverages AWS services for scalability and reliability
- **API-First Design**: Enables integration with existing business systems
- **Real-Time Processing**: Asynchronous background tasks for optimal performance
- **Secure Configuration**: Database-stored credentials and environment-based settings
- **Memory-Aware**: Persistent conversation context for personalized interactions
- **Current Information**: Real-time web search for up-to-date responses

---

## 🛣️ Roadmap and Future Potential

### Phase 1 (Current) - Foundation ✅
- Multi-agent architecture implementation
- Memory-aware orchestrator with Mem0 integration
- Telegram integration with background worker processing
- Knowledge base RAG system with ChromaDB
- Real-time web search capabilities via Tavily
- Calendar management with Google Calendar API
- Support ticket system with priority management
- Business dashboard with daily digest functionality
- Native conversations in 15+ languages including English, Chinese, and Spanish

### Phase 2 - Enhanced Intelligence & Multi-Channel 🧠
- **Advanced Sentiment Analysis**: Automatic escalation based on customer emotion and urgency
- **Voice Integration**: WhatsApp voice message processing and voice-to-text capabilities
- **Multi-Modal AI**: Process images, documents, and voice messages intelligently
- **Predictive Customer Service**: ML models predicting customer needs and proactive support
- **Smart Document Processing**: Automatic parsing of contracts, invoices, and business documents
- **Cross-Channel Orchestration**: Seamless customer journey across WhatsApp, Email, and Web Chat
- **Advanced Analytics Dashboard**: Real-time insights, customer behavior analysis, and business metrics
- **Custom Business Intelligence**: AI-powered BI dashboards tailored for each company's KPIs and metrics

### Phase 3 - Enterprise Integration & AI Workforce 🚀
- **Enterprise Connectors**: Native integration with Salesforce, HubSpot, Slack, and major CRM systems
- **Custom AI Agent Creation**: Build specialized agents for specific business functions
- **Advanced Workflow Automation**: AI-driven business process automation and optimization
- **Computer Vision Suite**: Automatic processing of receipts, IDs, and business documents
- **Federated Learning**: AI that learns across customer interactions while preserving privacy
- **White-label Solution**: Complete platform for businesses to deploy their own AI support system
- **Advanced Compliance**: Industry-specific compliance monitoring (GDPR, HIPAA, financial regulations)
- **API Marketplace**: Extensible platform with third-party integrations and custom plugins
- **Enterprise BI Suite**: Comprehensive business intelligence platform with custom dashboards, automated reporting, and AI-driven insights for executive decision-making

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 16+
- AWS Account (for Bedrock access)
- Google Cloud Account (for Calendar API)
- Telegram Bot Token
- Tavily API Key (for web search functionality)
- Mem0 configuration (for memory system)

### Quick Setup

1. **Clone Repository**
```bash
git clone https://github.com/EwenCheung/Agentic-AI-Kakak-Agent.git
cd Agentic-AI-Kakak-Agent
```

2. **Backend Setup**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. **Environment Configuration**
```bash
# Create .env file with required credentials
cp .env.example .env
# Edit .env with your API keys
```

5. **Start Backend**
```bash
cd ../backend
source .venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```
```bash
# Open another tab
cd ../backend
source .venv/bin/activate
python -m src.worker
```

4. **Frontend Setup**
```bash
cd ../frontend
npm install
npm start
```

### Configuration
1. **Access Dashboard**: Navigate to `http://localhost:3000` in your browser

2. **Configure API Credentials**: 
   - Add your Telegram bot token
   - Set up Google Calendar API credentials

3. **Upload Knowledge Base**: Upload your company documents (PDFs, docs) for AI training

4. **Customize Settings**: Set tone, language preferences, and business-specific configurations

5. **Test Integration**: Send a test message via Telegram to verify everything works

6. **🎉 Your personalized AI assistant is ready to serve customers!**

### Next Steps
- Start chatting with your AI agent via Telegram
- Monitor customer interactions through the business dashboard
- Review daily digest reports for business insights
- Scale by adding more knowledge base documents as neededYou

---