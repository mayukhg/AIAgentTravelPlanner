# Multi-Agent Assistant System - System Design Document

## Architecture Overview

The Multi-Agent Assistant System follows a sophisticated microservices-inspired architecture with coordinated AI agents, built on Flask and implementing LangGraph-style workflow orchestration.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE LAYER                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  Web Browser Client                                                         │
│  ├── Chat Interface (templates/chat.html)                                  │
│  ├── Landing Page (templates/index.html)                                   │
│  └── JavaScript Client (static/js/chat.js)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                            WEB FRAMEWORK LAYER                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  Flask Application (app.py)                                                │
│  ├── Main Routes (routes/main.py)                                          │
│  │   ├── GET /          → Landing page                                     │
│  │   ├── GET /chat      → Chat interface                                   │
│  │   └── GET /health    → Simple health check                              │
│  └── API Routes (routes/api.py)                                            │
│      ├── POST /api/chat          → Multi-agent chat processing             │
│      ├── GET /api/workflow/status → Workflow status monitoring             │
│      ├── GET /api/agents         → Available agents information            │
│      ├── GET /api/health         → Comprehensive health check              │
│      └── DELETE /api/clear       → Session cleanup                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                        WORKFLOW ORCHESTRATION LAYER                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  Multi-Agent Workflow Engine (graph/workflow.py)                           │
│  ├── Session Management                                                    │
│  │   ├── WorkflowState → Overall session state and history                │
│  │   └── AgentState   → Individual agent context and messages             │
│  ├── Agent Registration & Discovery                                        │
│  ├── Task Routing & Delegation Logic                                       │
│  ├── Inter-Agent Communication Protocol                                    │
│  └── Health Monitoring & Status Reporting                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                            AGENT LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  Base Agent Framework (agents/base_agent.py)                               │
│  ├── Abstract base class with common functionality                         │
│  ├── Standardized response formatting                                      │
│  └── Shared LLM integration interface                                      │
│                                                                             │
│  Personal Assistant Agent (agents/personal_assistant.py)                   │
│  ├── Main coordinator and task delegator                                   │
│  ├── Conversation management and context maintenance                       │
│  ├── Agent selection and delegation logic                                  │
│  └── Direct response for general queries                                   │
│                                                                             │
│  Calendar Agent (agents/calendar_agent.py)                                 │
│  ├── Event creation and management                                         │
│  ├── Scheduling conflict detection                                         │
│  ├── Natural language date/time parsing                                    │
│  └── Calendar queries and availability finding                             │
│                                                                             │
│  Search Agent (agents/search_agent.py)                                     │
│  ├── Web search via Perplexity API                                        │
│  ├── Information research and fact-finding                                 │
│  ├── Source citation and verification                                      │
│  └── Current events and real-time data                                     │
│                                                                             │
│  Code Assistant Agent (agents/code_assistant.py)                           │
│  ├── Code generation and review                                            │
│  ├── Programming assistance and debugging                                  │
│  ├── Built-in development tools integration                                │
│  └── Educational programming support                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                            SERVICE LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  Bedrock Service (services/bedrock_service.py)                             │
│  ├── Amazon Bedrock LLM integration                                        │
│  ├── Claude model inference                                                │
│  ├── Request formatting and response parsing                               │
│  └── Error handling and retry logic                                        │
│                                                                             │
│  Perplexity Service (services/perplexity_service.py)                       │
│  ├── Real-time web search capabilities                                     │
│  ├── Current information retrieval                                         │
│  ├── Source citation extraction                                            │
│  └── Search result formatting                                              │
│                                                                             │
│  Tools Service (services/tools_service.py)                                 │
│  ├── Python REPL execution environment                                     │
│  ├── File system operations (read/write/edit)                              │
│  ├── Shell command execution                                               │
│  └── Persistent journal functionality                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                          DATA PERSISTENCE LAYER                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  SQLite Database (models.py)                                               │
│  ├── CalendarEvent → Event storage and management                          │
│  ├── ChatSession  → Session tracking and metadata                          │
│  ├── ChatMessage  → Message history with agent attribution                 │
│  └── AgentState   → Persistent agent state storage                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                           EXTERNAL SERVICES                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  Amazon Bedrock                │  Perplexity AI                           │
│  ├── Claude 3 Sonnet           │  ├── Real-time web search                │
│  ├── LLM inference             │  ├── Current information                 │
│  └── Natural language          │  └── Source citations                    │
│      processing                │                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Interactions

### 1. Request Flow Architecture

```
User Request → Web Interface → Flask Routes → Workflow Engine → Agent Selection → Task Processing → Response Delivery

1. User Input:
   - User types message in chat interface
   - JavaScript client validates and sends via POST /api/chat

2. Request Processing:
   - Flask API route receives and validates request
   - Session management creates or retrieves workflow state
   - Request forwarded to MultiAgentWorkflow.process_user_input()

3. Agent Coordination:
   - Personal Assistant Agent analyzes request
   - Delegation decision made based on task classification
   - Appropriate specialized agent selected and invoked

4. Task Execution:
   - Selected agent processes task using its domain expertise
   - External services called as needed (Bedrock, Perplexity, Tools)
   - Results formatted in standardized response structure

5. Response Delivery:
   - Workflow engine aggregates and formats final response
   - Response sent back through Flask API
   - JavaScript client displays formatted response with metadata
```

### 2. Agent Communication Protocol

```
Personal Assistant (Coordinator)
    ↓ (Delegation Analysis)
    ├── Calendar Agent
    │   ├── → SQLite Database (Event Operations)
    │   └── → Bedrock Service (Natural Language Processing)
    ├── Search Agent  
    │   ├── → Perplexity Service (Web Search)
    │   └── → Bedrock Service (Response Enhancement)
    └── Code Assistant
        ├── → Tools Service (Code Execution)
        └── → Bedrock Service (Code Generation)
```

### 3. Data Flow Patterns

**Session State Management:**
```
WorkflowState (Session-level)
├── session_id: Unique session identifier
├── current_agent: Active agent reference
├── global_context: Shared session data
├── workflow_history: Event timeline
└── agent_states: Individual agent contexts
    ├── AgentState (Personal Assistant)
    ├── AgentState (Calendar Agent)
    ├── AgentState (Search Agent)
    └── AgentState (Code Assistant)
```

**Message Processing Pipeline:**
```
Raw User Input
    ↓ (Validation & Sanitization)
Processed Input
    ↓ (Task Classification)
Agent Selection
    ↓ (Context Injection)
Agent Processing
    ↓ (Response Formatting)
Structured Response
    ↓ (Web Interface Rendering)
User-Facing Output
```

## Technology Stack

### Backend Technologies
- **Flask 3.0+**: Web framework providing REST API and web interface
- **SQLAlchemy**: Database ORM for data persistence and management
- **SQLite**: Lightweight database for development and small deployments
- **Gunicorn**: WSGI HTTP server for production deployment
- **asyncio**: Asynchronous programming for non-blocking operations

### Frontend Technologies
- **Bootstrap 5.3**: CSS framework with Replit dark theme
- **Vanilla JavaScript**: Client-side functionality without heavy frameworks
- **Feather Icons**: Lightweight icon library for UI elements
- **WebSocket-ready**: Architecture supports real-time communication

### AI/ML Services
- **Amazon Bedrock**: Claude 3 Sonnet for natural language processing
- **Perplexity AI**: Real-time web search and information retrieval
- **Custom LLM Integration**: Extensible service layer for additional models

### Development Tools
- **Python 3.11+**: Modern Python with latest language features
- **Type Hints**: Comprehensive type annotations for code clarity
- **Logging**: Structured logging with multiple severity levels
- **Environment Variables**: Configuration management via environment

## Deployment Architecture

### Development Setup
```
Local Development Environment
├── Python 3.11+ Runtime
├── SQLite Database (file-based)
├── Environment Variables (.env file)
├── Hot-reload Development Server
└── Debug Logging Enabled
```

### Production Deployment
```
Production Environment
├── Gunicorn WSGI Server (multi-worker)
├── PostgreSQL Database (recommended)
├── Reverse Proxy (Nginx/Apache)
├── SSL/TLS Termination
├── Environment Variable Management
├── Log Aggregation System
└── Health Monitoring Dashboard
```

### Scalability Considerations

**Horizontal Scaling:**
- Stateless agent design enables multiple instance deployment
- Session state can be externalized to Redis or database
- Load balancing across multiple application instances

**Vertical Scaling:**
- Multi-worker Gunicorn configuration
- Database connection pooling
- Async/await patterns for I/O-bound operations

**Service Isolation:**
- Agents can be deployed as separate microservices
- Service mesh integration for inter-service communication
- Container orchestration with Docker/Kubernetes

## Security Architecture

### Authentication & Authorization
- Session-based authentication for web interface
- API key validation for external service access
- Role-based access control for administrative functions

### Input Validation & Sanitization
- Comprehensive input validation at API layer
- SQL injection prevention via parameterized queries
- XSS protection with output encoding
- Command injection prevention in tools service

### External Service Security
- API key management via environment variables
- TLS encryption for all external communications
- Rate limiting and timeout controls
- Service health monitoring and failover

## Monitoring & Observability

### Health Monitoring
- `/api/health` endpoint provides comprehensive system status
- Service-level health checks for all external dependencies
- Resource usage monitoring (memory, CPU, disk)
- Active session and workflow tracking

### Logging Strategy
- Structured JSON logging for machine readability
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Agent-specific log namespaces for debugging
- Security event logging for audit trails

### Error Handling
- Graceful degradation when services are unavailable
- User-friendly error messages with technical details hidden
- Automatic retry mechanisms with exponential backoff
- Circuit breaker patterns for external service failures

This system design provides a robust, scalable, and maintainable foundation for the Multi-Agent Assistant System, supporting both current functionality and future enhancements.