# System Architecture

Comprehensive overview of the Multi-Agent Assistant System architecture, design patterns, and component interactions.

## Architecture Overview

The Multi-Agent Assistant System follows a layered microservices-inspired architecture with intelligent workflow orchestration:

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
│  ├── Agent selection and workflow orchestration                            │
│  └── Fallback handling for general queries                                 │
│                                                                             │
│  Calendar Agent (agents/calendar_agent.py)                                 │
│  ├── Event creation, modification, and deletion                            │
│  ├── Schedule conflict detection and resolution                            │
│  ├── Free time slot identification                                         │
│  └── Natural language date/time parsing                                    │
│                                                                             │
│  Search Agent (agents/search_agent.py)                                     │
│  ├── Real-time web search via Perplexity API                              │
│  ├── Information synthesis and summarization                               │
│  ├── Source citation and credibility assessment                            │
│  └── Multi-query research coordination                                     │
│                                                                             │
│  Code Assistant Agent (agents/code_assistant.py)                           │
│  ├── Code generation and refactoring                                       │
│  ├── Debugging assistance and error analysis                               │
│  ├── Technical documentation and explanations                              │
│  └── Educational programming support                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                            SERVICE LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  Bedrock Service (services/bedrock_service.py)                             │
│  ├── Claude 3.5 Sonnet v4 integration                                     │
│  ├── Request formatting and response parsing                               │
│  ├── Error handling and retry logic                                        │
│  └── Health monitoring and performance metrics                             │
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
│  PostgreSQL Database (models.py)                                           │
│  ├── CalendarEvent → Event storage and management                          │
│  ├── ChatSession  → Session tracking and metadata                          │
│  ├── ChatMessage  → Message history with agent attribution                 │
│  └── AgentState   → Persistent agent state storage                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                           EXTERNAL SERVICES                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  Amazon Bedrock                │  Perplexity AI                           │
│  ├── Claude 3.5 Sonnet v4      │  ├── Real-time web search                │
│  ├── LLM inference             │  ├── Current information                 │
│  └── Natural language          │  └── Source citations                    │
│      processing                │                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Design Patterns

### 1. Multi-Agent Coordinator Pattern

The system implements a sophisticated coordinator pattern where the Personal Assistant Agent acts as the central orchestrator:

```python
class PersonalAssistantAgent(BaseAgent):
    """Main coordinator implementing delegation pattern"""
    
    def __init__(self):
        self.specialized_agents = {}
        self.delegation_analyzer = DelegationAnalyzer()
    
    async def process_task(self, task, context):
        # Analyze delegation need
        delegation_decision = await self._analyze_delegation_need(task, context)
        
        if delegation_decision['needs_delegation']:
            return await self._delegate_task(task, context, delegation_decision)
        else:
            return await self._handle_directly(task, context)
```

### 2. Strategy Pattern for Agent Selection

Each agent implements the same interface but with specialized strategies:

```python
class BaseAgent(ABC):
    @abstractmethod
    async def can_handle(self, task: str, context: Dict) -> bool:
        """Strategy for determining task compatibility"""
        pass
    
    @abstractmethod
    async def process_task(self, task: str, context: Dict) -> Dict:
        """Strategy for task processing"""
        pass
```

### 3. Factory Pattern for Service Creation

Services are created using a factory pattern for dependency injection:

```python
class ServiceFactory:
    @staticmethod
    def create_bedrock_service():
        return BedrockService()
    
    @staticmethod
    def create_workflow_engine():
        return WorkflowEngine(
            bedrock_service=ServiceFactory.create_bedrock_service(),
            tools_service=ServiceFactory.create_tools_service()
        )
```

## Component Interactions

### Request Flow Architecture

```
User Request → Web Interface → Flask Routes → Workflow Engine → Agent Selection → Task Processing → Response Delivery

1. User Input:
   - User types message in chat interface
   - JavaScript client validates and sends via POST /api/chat

2. Request Processing:
   - Flask route receives request and extracts message/context
   - Session management creates or retrieves existing session
   - Request forwarded to Workflow Engine

3. Agent Selection:
   - Personal Assistant Agent analyzes request intent
   - Delegation decision made based on task classification
   - Appropriate specialized agent selected or direct handling

4. Task Execution:
   - Selected agent processes the request
   - External services called as needed (Bedrock, Perplexity)
   - Database operations performed for state persistence

5. Response Generation:
   - Agent formats response with metadata
   - Response sent back through Flask to client
   - Session state updated with interaction history
```

### Inter-Agent Communication

Agents communicate through a standardized protocol:

```python
class AgentCommunicationProtocol:
    async def delegate_task(self, from_agent: str, to_agent: str, task: Dict):
        """Delegate task between agents"""
        
    async def request_information(self, requesting_agent: str, target_agent: str, query: str):
        """Request information from another agent"""
        
    async def notify_completion(self, agent: str, task_id: str, result: Dict):
        """Notify completion of delegated task"""
```

## Data Flow Architecture

### Session Management

```
Session Creation → Context Building → Agent State Management → Response Tracking → Session Persistence

1. Session Initialization:
   - Unique session ID generated
   - Initial context established
   - Agent states initialized

2. Context Management:
   - Message history maintained
   - Agent-specific context preserved
   - Cross-agent information sharing

3. State Persistence:
   - Session data stored in PostgreSQL
   - Agent states serialized and cached
   - Message history with attribution
```

### Database Schema Design

```sql
-- Core session management
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Message history with agent attribution
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) REFERENCES chat_sessions(session_id),
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    agent_type VARCHAR(50),
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Agent state persistence
CREATE TABLE agent_states (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    agent_type VARCHAR(50) NOT NULL,
    state_data TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Calendar events for Calendar Agent
CREATE TABLE calendar_events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    location VARCHAR(200),
    all_day BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Security Architecture

### Input Validation Layer

```python
class SecurityValidator:
    def validate_user_input(self, message: str) -> bool:
        """Validate user input for security threats"""
        
    def sanitize_command(self, command: str) -> str:
        """Sanitize shell commands for safe execution"""
        
    def check_file_access(self, file_path: str) -> bool:
        """Validate file access permissions"""
```

### Rate Limiting and Access Control

```python
class RateLimiter:
    def __init__(self):
        self.limits = {
            'chat': 60,  # requests per minute
            'api': 120   # requests per minute
        }
    
    def check_rate_limit(self, session_id: str, endpoint: str) -> bool:
        """Check if request is within rate limits"""
```

## Scalability Considerations

### Horizontal Scaling

The architecture supports horizontal scaling through:

1. **Stateless Agent Design**: Agents maintain minimal state
2. **Database-Backed Sessions**: Session data persisted externally
3. **Service Layer Abstraction**: External services can be load-balanced
4. **Microservices Compatibility**: Components can be deployed separately

### Performance Optimization

```python
class PerformanceOptimizer:
    def __init__(self):
        self.cache = RedisCache()
        self.connection_pool = ConnectionPool()
    
    async def cached_llm_request(self, prompt: str) -> str:
        """Cache LLM responses for common requests"""
        
    async def batch_database_operations(self, operations: List) -> List:
        """Batch database operations for efficiency"""
```

## Monitoring and Observability

### Health Check Architecture

```python
class HealthMonitor:
    async def comprehensive_health_check(self) -> Dict:
        return {
            'status': 'healthy|degraded|unhealthy',
            'services': await self._check_external_services(),
            'agents': await self._check_agent_status(),
            'metrics': await self._collect_performance_metrics()
        }
```

### Logging Strategy

```python
import logging

# Structured logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

class StructuredLogger:
    def log_agent_interaction(self, agent_type: str, task: str, response: Dict):
        """Log agent interactions with structured data"""
        
    def log_performance_metrics(self, endpoint: str, response_time: float):
        """Log performance metrics for monitoring"""
```

## Configuration Management

### Environment-Based Configuration

```python
class Config:
    # AI Model Configuration
    BEDROCK_MODEL_ID = 'anthropic.claude-3-5-sonnet-20241022-v2:0'
    
    # Service Endpoints
    PERPLEXITY_API_URL = 'https://api.perplexity.ai'
    
    # Performance Tuning
    MAX_AGENT_ITERATIONS = 10
    AGENT_TIMEOUT = 30
    CONNECTION_POOL_SIZE = 20
```

### Feature Flags

```python
class FeatureFlags:
    ENABLE_ADVANCED_SEARCH = True
    ENABLE_CODE_EXECUTION = True
    ENABLE_CALENDAR_INTEGRATION = True
    DEBUG_MODE = False
```

## Extension Points

### Adding New Agents

```python
class CustomAgent(BaseAgent):
    def __init__(self, bedrock_service, tools_service=None):
        super().__init__('custom_agent', bedrock_service, tools_service)
    
    def can_handle(self, task: str, context: Dict) -> bool:
        # Custom task detection logic
        return 'custom_keyword' in task.lower()
    
    async def process_task(self, task: str, context: Dict) -> Dict:
        # Custom task processing logic
        pass
```

### Custom Service Integration

```python
class CustomService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = CustomAPIClient(api_key)
    
    async def process_request(self, request: Dict) -> Dict:
        # Custom service logic
        pass
```

This architecture provides a solid foundation for a scalable, maintainable, and extensible multi-agent assistant system.