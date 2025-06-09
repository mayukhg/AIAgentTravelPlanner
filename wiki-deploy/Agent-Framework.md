# Agent Framework

Comprehensive guide to the multi-agent system architecture, agent capabilities, and workflow orchestration.

## Framework Overview

The Multi-Agent Assistant System implements a sophisticated agent framework based on the Strategy and Coordinator patterns, enabling intelligent task routing and specialized processing capabilities.

### Core Principles

1. **Specialized Expertise**: Each agent focuses on a specific domain
2. **Intelligent Routing**: Automatic task delegation based on content analysis
3. **Unified Interface**: Consistent interaction patterns across all agents
4. **Extensible Design**: Easy addition of new agents and capabilities
5. **Context Preservation**: Conversation history and state maintenance

## Agent Architecture

### Base Agent Framework

All agents inherit from the `BaseAgent` abstract class, ensuring consistent behavior:

```python
class BaseAgent(ABC):
    def __init__(self, agent_type: str, bedrock_service, tools_service=None):
        self.agent_type = agent_type
        self.bedrock_service = bedrock_service
        self.tools_service = tools_service
        self.logger = logging.getLogger(f"agents.{agent_type}")
    
    @abstractmethod
    def can_handle(self, task: str, context: Dict[str, Any]) -> bool:
        """Determine if this agent can handle the given task"""
        pass
    
    @abstractmethod
    async def process_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the given task and return structured results"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return a list of capabilities this agent provides"""
        pass
```

### Agent Lifecycle

```
1. Registration    → Agent registers with the workflow engine
2. Initialization  → Agent loads configuration and establishes connections
3. Task Evaluation → Agent evaluates incoming tasks via can_handle()
4. Task Processing → Agent processes assigned tasks via process_task()
5. Response Format → Agent formats responses using standard structure
6. State Update    → Agent updates internal state and context
```

## Individual Agent Specifications

### Personal Assistant Agent

**Role**: Central coordinator and primary interface

**Capabilities**:
- Task analysis and intent classification
- Agent selection and delegation
- Conversation continuity management
- General assistance and fallback handling

**Decision Matrix**:
```python
def can_handle(self, task: str, context: Dict[str, Any]) -> bool:
    # Personal Assistant can handle any task by delegating or responding directly
    return True

async def _analyze_delegation_need(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
    analysis_prompt = f"""
    Analyze this user request and determine if it needs specialized agent handling:
    
    Request: {task}
    
    Available specialized agents:
    - Calendar Agent: scheduling, events, appointments, time management
    - Search Agent: web search, current information, research, facts
    - Code Assistant: programming, debugging, code generation, technical explanations
    
    Respond with JSON:
    {{
        "needs_delegation": boolean,
        "recommended_agent": "agent_type or null",
        "confidence": float (0-1),
        "reasoning": "explanation"
    }}
    """
```

**Example Interactions**:
- "What can you help me with?" → Direct response
- "Schedule a meeting tomorrow" → Delegate to Calendar Agent
- "Write Python code for sorting" → Delegate to Code Assistant

### Calendar Agent

**Role**: Schedule and event management specialist

**Capabilities**:
- Event creation, modification, and deletion
- Schedule conflict detection and resolution
- Free time slot identification
- Natural language date/time parsing
- Recurring event management

**Task Detection Keywords**:
```python
calendar_keywords = [
    'schedule', 'calendar', 'meeting', 'appointment', 'event',
    'book', 'reserve', 'plan', 'remind', 'available', 'free time',
    'conflict', 'reschedule', 'cancel', 'busy', 'agenda'
]

time_patterns = [
    r'\b(today|tomorrow|yesterday)\b',
    r'\b\d{1,2}:\d{2}\s*(AM|PM|am|pm)?\b',
    r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
    r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b'
]
```

**Core Functions**:

1. **Event Creation**:
```python
async def _create_event(self, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    event_data = analysis.get('event_details', {})
    
    # Parse date/time with natural language processing
    parsed_time = await self._parse_datetime(event_data.get('time_expression'))
    
    # Check for conflicts
    conflicts = self._check_conflicts(parsed_time['start'], parsed_time['end'])
    
    if conflicts:
        return self._handle_conflict_resolution(conflicts, event_data)
    
    # Create event in database
    event = CalendarEvent(
        title=event_data['title'],
        start_time=parsed_time['start'],
        end_time=parsed_time['end'],
        description=event_data.get('description'),
        location=event_data.get('location')
    )
```

2. **Conflict Detection**:
```python
def _check_conflicts(self, start_time: datetime, end_time: datetime) -> List[CalendarEvent]:
    return CalendarEvent.query.filter(
        CalendarEvent.start_time < end_time,
        CalendarEvent.end_time > start_time
    ).all()
```

### Search Agent

**Role**: Real-time information retrieval and research

**Capabilities**:
- Real-time web search via Perplexity API
- Information synthesis and summarization
- Source citation and credibility assessment
- Multi-query research coordination
- Current events and fact-checking

**Task Detection**:
```python
search_keywords = [
    'search', 'find', 'look up', 'research', 'information', 'what is',
    'who is', 'where is', 'when did', 'how to', 'latest', 'current',
    'news', 'recent', 'update', 'facts', 'statistics', 'compare'
]

def can_handle(self, task: str, context: Dict[str, Any]) -> bool:
    task_lower = task.lower()
    
    # Direct search indicators
    if any(keyword in task_lower for keyword in self.search_keywords):
        return True
    
    # Question patterns that require current information
    question_patterns = [
        r'\bwhat.*(?:latest|current|recent|new|today)',
        r'\bwho.*(?:current|now|today)',
        r'\bwhen.*(?:latest|recent|last)',
        r'\bhow.*(?:current|latest|now)'
    ]
    
    return any(re.search(pattern, task_lower) for pattern in question_patterns)
```

**Search Process**:
```python
async def _perform_search(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
    # Execute Perplexity API search
    search_response = await self.perplexity_service.search(
        query=query,
        model='llama-3.1-sonar-small-128k-online',
        temperature=0.2
    )
    
    # Extract and validate sources
    sources = self._extract_sources(search_response)
    
    # Synthesize information
    synthesis = await self._synthesize_information(search_response, query)
    
    return {
        'answer': synthesis,
        'sources': sources,
        'confidence': self._assess_confidence(search_response),
        'search_metadata': {
            'query': query,
            'timestamp': datetime.utcnow().isoformat(),
            'source_count': len(sources)
        }
    }
```

### Code Assistant Agent

**Role**: Programming assistance and technical guidance

**Capabilities**:
- Code generation and refactoring
- Debugging assistance and error analysis
- Technical documentation and explanations
- Educational programming support
- Integration with development tools

**Task Detection**:
```python
programming_keywords = [
    'code', 'program', 'script', 'function', 'class', 'method',
    'debug', 'error', 'bug', 'compile', 'run', 'execute',
    'algorithm', 'data structure', 'api', 'database', 'framework',
    'python', 'javascript', 'java', 'c++', 'sql', 'html', 'css'
]

technical_patterns = [
    r'\b(?:write|create|generate|build)\s+(?:a\s+)?(?:function|class|script|program)',
    r'\b(?:debug|fix|solve)\s+(?:this\s+)?(?:error|bug|issue|problem)',
    r'\b(?:explain|how\s+does)\s+.*(?:work|algorithm|function)',
    r'\b(?:python|javascript|java|sql)\b.*(?:code|function|script)'
]
```

**Core Functions**:

1. **Code Generation**:
```python
async def _generate_code(self, task: str, context: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
    code_prompt = f"""
    Generate {analysis['language']} code for the following request:
    {task}
    
    Requirements:
    - Include comprehensive comments
    - Follow best practices and conventions
    - Handle edge cases and errors
    - Provide usage examples
    """
    
    code_response = await self.bedrock_service.generate_response([
        {"role": "user", "content": code_prompt}
    ], max_tokens=2000)
    
    return {
        'code': self._extract_code_blocks(code_response),
        'explanation': self._extract_explanation(code_response),
        'language': analysis['language'],
        'complexity': analysis.get('complexity', 'medium')
    }
```

2. **Debugging Assistance**:
```python
async def _help_debug(self, task: str, context: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
    debug_prompt = f"""
    Analyze this code issue and provide debugging assistance:
    
    Problem: {task}
    Code: {analysis.get('code_snippet', 'Not provided')}
    Error: {analysis.get('error_message', 'Not provided')}
    
    Provide:
    1. Root cause analysis
    2. Step-by-step debugging approach
    3. Corrected code if applicable
    4. Prevention strategies
    """
```

## Workflow Orchestration

### Agent Registration

```python
class WorkflowEngine:
    def __init__(self):
        self.agents = {}
        self.session_states = {}
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the workflow engine"""
        self.agents[agent.agent_type] = agent
        self.logger.info(f"Registered agent: {agent.agent_type}")
    
    def get_agent_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all registered agents"""
        return {
            agent_type: agent.get_capabilities() 
            for agent_type, agent in self.agents.items()
        }
```

### Task Routing Logic

```python
async def route_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Route task to appropriate agent"""
    
    # Start with Personal Assistant for coordination
    coordinator = self.agents['personal_assistant']
    
    # Let coordinator analyze and delegate
    result = await coordinator.process_task(task, context)
    
    # Update session state
    self._update_session_state(context['session_id'], result)
    
    return result

def _select_best_agent(self, task: str, context: Dict[str, Any]) -> BaseAgent:
    """Select the best agent for a given task"""
    agent_scores = {}
    
    for agent_type, agent in self.agents.items():
        if agent.can_handle(task, context):
            # Calculate confidence score
            score = self._calculate_agent_score(agent, task, context)
            agent_scores[agent_type] = score
    
    # Return agent with highest confidence score
    best_agent_type = max(agent_scores.items(), key=lambda x: x[1])[0]
    return self.agents[best_agent_type]
```

### Inter-Agent Communication

```python
class AgentCommunicationProtocol:
    async def delegate_task(self, from_agent: str, to_agent: str, task: Dict) -> Dict:
        """Delegate task between agents"""
        delegation_record = {
            'from_agent': from_agent,
            'to_agent': to_agent,
            'task': task,
            'timestamp': datetime.utcnow(),
            'status': 'pending'
        }
        
        # Execute delegation
        target_agent = self.workflow_engine.agents[to_agent]
        result = await target_agent.process_task(task['content'], task['context'])
        
        delegation_record['status'] = 'completed'
        delegation_record['result'] = result
        
        return delegation_record
```

## State Management

### Session State Structure

```python
@dataclass
class WorkflowState:
    session_id: str
    created_at: datetime
    last_activity: datetime
    message_history: List[Dict]
    agent_states: Dict[str, Any]
    context: Dict[str, Any]
    
    def add_message(self, role: str, content: str, agent_type: str = None):
        """Add message to history"""
        self.message_history.append({
            'role': role,
            'content': content,
            'agent_type': agent_type,
            'timestamp': datetime.utcnow()
        })
        self.last_activity = datetime.utcnow()
```

### Agent State Persistence

```python
class AgentStateManager:
    def save_agent_state(self, session_id: str, agent_type: str, state_data: Dict):
        """Save agent state to database"""
        agent_state = AgentState.query.filter_by(
            session_id=session_id,
            agent_type=agent_type
        ).first()
        
        if agent_state:
            agent_state.state_data = json.dumps(state_data)
            agent_state.updated_at = datetime.utcnow()
        else:
            agent_state = AgentState(
                session_id=session_id,
                agent_type=agent_type,
                state_data=json.dumps(state_data)
            )
            db.session.add(agent_state)
        
        db.session.commit()
```

## Performance Optimization

### Agent Response Caching

```python
class AgentResponseCache:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def get_cached_response(self, agent_type: str, task_hash: str) -> Optional[Dict]:
        """Get cached response if available and not expired"""
        cache_key = f"{agent_type}:{task_hash}"
        
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.utcnow() - cached_data['timestamp'] < timedelta(seconds=self.cache_ttl):
                return cached_data['response']
        
        return None
```

### Parallel Agent Processing

```python
async def process_multiple_agents(self, tasks: List[Dict]) -> List[Dict]:
    """Process multiple tasks in parallel"""
    tasks_with_agents = [
        (task, self._select_best_agent(task['content'], task['context']))
        for task in tasks
    ]
    
    # Process in parallel
    results = await asyncio.gather(*[
        agent.process_task(task['content'], task['context'])
        for task, agent in tasks_with_agents
    ])
    
    return results
```

## Monitoring and Analytics

### Agent Performance Metrics

```python
class AgentMetrics:
    def __init__(self):
        self.metrics = {
            'response_times': defaultdict(list),
            'success_rates': defaultdict(int),
            'task_counts': defaultdict(int),
            'error_counts': defaultdict(int)
        }
    
    def record_agent_performance(self, agent_type: str, response_time: float, success: bool):
        """Record agent performance metrics"""
        self.metrics['response_times'][agent_type].append(response_time)
        self.metrics['task_counts'][agent_type] += 1
        
        if success:
            self.metrics['success_rates'][agent_type] += 1
        else:
            self.metrics['error_counts'][agent_type] += 1
```

This comprehensive agent framework provides the foundation for building sophisticated multi-agent AI systems with intelligent task routing, specialized processing capabilities, and robust state management.