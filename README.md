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
🤖 **Multi-Agent Intelligence** - Specialized agents for chat, scheduling, ticketing, and business insights  
📚 **Knowledge Base Integration** - RAG-powered document search and AI-driven responses  
📅 **Calendar Management** - Google Calendar integration for appointment scheduling  
🎫 **Smart Ticketing** - Automated ticket creation, tracking, and escalation  
📊 **Business Dashboard** - Real-time analytics and daily digest reports  
🔗 **Multi-Channel Support** - Telegram (implemented) with extensible architecture  

---

## 🛠️ Methodology

### Agent-Based Architecture
The system employs a **hierarchical multi-agent approach** where each agent specializes in specific domains:

1. **Orchestrator Agent**: Central coordinator that analyzes user intent and delegates to specialist agents
2. **Chat Agent**: Handles general conversations and knowledge base queries  
3. **Scheduler Agent**: Manages calendar operations and appointment booking
4. **Ticketing Agent**: Creates, updates, and tracks support tickets
5. **Daily Digest Agent**: Generates business insights and summaries

### AI Technologies Used:
- **Large Language Models**: Amazon Bedrock (Claude 3 Haiku) for natural language processing
- **Vector Embeddings**: Amazon Titan Embed for semantic search
- **RAG (Retrieval-Augmented Generation)**: ChromaDB for knowledge base search
- **Document Processing**: Docling for PDF parsing and chunking
- **Agent Framework**: Strands AI for agent orchestration

### Integration Strategy:
- **Telegram Bot API** for real-time messaging
- **Google Calendar API** for scheduling management  
- **SQLite Database** for data persistence and conversation memory
- **FastAPI** for scalable backend architecture
- **React Frontend** for business dashboard

---

## 🏗️ Technical Architecture

### System Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend (React)"
        Dashboard[Business Dashboard]
        Config[Configuration Panel]
        KB[Knowledge Base Upload]
    end
    
    subgraph "Backend (FastAPI)"
        API[API Gateway]
        Orchestrator[Orchestrator Agent]
        
        subgraph "Specialist Agents"
            Chat[Chat Agent]
            Scheduler[Scheduler Agent]
            Ticketing[Ticketing Agent]
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
        GCal[Google Calendar]
        Bedrock[Amazon Bedrock]
    end
    
    subgraph "End Users"
        Customer[Customer via Telegram]
    end
    
    Customer --> Telegram
    Telegram --> API
    API --> Orchestrator
    Orchestrator --> Chat
    Orchestrator --> Scheduler
    Orchestrator --> Ticketing
    Orchestrator --> Digest
    
    Chat --> Telegram
    Scheduler --> GCal
    
    Dashboard --> API
    Config --> API
    KB --> API
    
    Chat --> SQLite
    Scheduler --> SQLite
    Ticketing --> SQLite
    
    Chat --> Vector
    Chat --> Bedrock
    Orchestrator --> Bedrock
```

### Technology Stack

#### Backend:
- **Framework**: FastAPI with async/await support
- **AI Platform**: Amazon Bedrock (Claude 3 Haiku, Titan Embeddings)
- **Agent Framework**: Strands AI for agent orchestration
- **Vector Database**: ChromaDB for semantic search
- **Database**: SQLite with SQLAlchemy ORM
- **Document Processing**: Docling for PDF parsing
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

---

## 🛣️ Roadmap and Future Potential

### Phase 1 (Current) - Foundation ✅
- Multi-agent architecture implementation
- Telegram integration
- Knowledge base RAG system
- Calendar management
- Support ticket system
- Business dashboard

### Phase 2 - Enhanced Intelligence
- **Advanced NLP**: Fine-tuned models for domain-specific responses
- **Sentiment Analysis**: Automatic escalation based on customer emotion
- **Multi-Language Support**: Expand to serve global customer base
- **Voice Integration**: WhatsApp voice message processing

### Phase 3 - Multi-Channel Expansion
- **Computer Vision** for document and image processing
- **Predictive Customer Service** using historical data
- **Custom AI Model Training** on company-specific data
- **Advanced Personalization** using customer behavior analysis

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 16+
- AWS Account (for Bedrock access)
- Google Cloud Account (for Calendar API)
- Telegram Bot Token

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

4. **Frontend Setup**
```bash
cd ../frontend
npm install
npm start
```

5. **Start Backend**
```bash
cd ../backend
source .venv/bin/activate
python -m src.main
```

### Configuration
1. Access the dashboard at `http://localhost:3000`
2. Configure Telegram bot token and Google Calendar credentials
3. Upload knowledge base documents
4. Test the system via Telegram

---

