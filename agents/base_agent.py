import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the multi-agent system.
    
    This class establishes the core interface and shared functionality that all
    specialized agents must implement. It provides:
    
    1. Agent Identity: Unique agent type identification and metadata
    2. Capability Declaration: Abstract method for declaring agent capabilities
    3. Task Handling: Abstract methods for task routing and processing
    4. Response Formatting: Standardized response and error formatting
    5. LLM Integration: Common interface for language model interactions
    6. Logging: Structured logging for debugging and monitoring
    
    The base agent follows the Strategy pattern, where each specialized agent
    implements specific task handling strategies while sharing common infrastructure.
    
    Agent Lifecycle:
    1. Initialization with required services (Bedrock, Tools, etc.)
    2. Registration with the workflow coordinator
    3. Task evaluation via can_handle() method
    4. Task processing via process_task() method
    5. Response formatting and delivery
    
    Design Principles:
    - Single Responsibility: Each agent has a focused domain of expertise
    - Open/Closed: Extensible for new agent types without modifying existing code
    - Dependency Injection: Services provided via constructor for testability
    - Error Handling: Graceful error handling with structured error responses
    """
    
    def __init__(self, agent_type: str, bedrock_service, tools_service=None):
        """
        Initialize base agent with required services and configuration.
        
        Args:
            agent_type: Unique identifier for this agent type (e.g., 'calendar_agent')
            bedrock_service: Amazon Bedrock service for LLM interactions
            tools_service: Optional tools service for built-in development tools
        """
        self.agent_type = agent_type
        self.bedrock_service = bedrock_service
        self.tools_service = tools_service
        self.logger = logging.getLogger(f"agents.{agent_type}")
        
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Return the system prompt that defines this agent's behavior and capabilities.
        
        This prompt is sent to the LLM to establish the agent's role, expertise,
        and behavioral guidelines. It should include:
        - Agent's primary purpose and domain expertise
        - Available capabilities and tools
        - Interaction guidelines and constraints
        - Output format specifications
        
        Returns:
            str: The system prompt for this agent
        """
        pass
    
    @abstractmethod
    def can_handle(self, task: str, context: Dict[str, Any]) -> bool:
        """
        Determine if this agent can handle the given task.
        
        This method implements the agent's task routing logic, analyzing
        the user's request to determine if it falls within this agent's
        domain of expertise. Uses keyword matching, context analysis,
        and domain-specific patterns.
        
        Args:
            task: The user's request or task description
            context: Additional context including conversation history
            
        Returns:
            bool: True if this agent should handle the task, False otherwise
        """
        pass
    
    @abstractmethod
    async def process_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the given task and return structured results.
        
        This is the main processing method where the agent performs its
        specialized work. The implementation should:
        1. Parse and analyze the task requirements
        2. Execute the necessary operations (API calls, database queries, etc.)
        3. Format the results in a standardized response structure
        4. Handle errors gracefully with appropriate error responses
        
        Args:
            task: The user's request to process
            context: Processing context including session data and history
            
        Returns:
            Dict[str, Any]: Standardized response with content, metadata, and status
        """
        pass
    
    def get_capabilities(self) -> List[str]:
        """Return a list of capabilities this agent provides"""
        return []
    
    def format_response(self, content: str, additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format the agent's response in a standard way"""
        response = {
            'agent_type': self.agent_type,
            'content': content,
            'timestamp': datetime.utcnow().isoformat(),
            'success': True
        }
        
        if additional_data:
            response.update(additional_data)
            
        return response
    
    def format_error(self, error_message: str, error_type: str = "processing_error") -> Dict[str, Any]:
        """Format an error response"""
        return {
            'agent_type': self.agent_type,
            'content': f"Error: {error_message}",
            'error_type': error_type,
            'timestamp': datetime.utcnow().isoformat(),
            'success': False
        }
    
    async def generate_response(self, messages: List[Dict[str, str]], max_tokens: int = 1000) -> str:
        """Generate a response using the bedrock service"""
        try:
            system_prompt = self.get_system_prompt()
            response = await self.bedrock_service.generate_response(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=max_tokens
            )
            return response
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            raise
    
    def log_interaction(self, task: str, response: Dict[str, Any]):
        """Log the interaction for debugging purposes"""
        self.logger.info(f"Task: {task[:100]}...")
        self.logger.info(f"Response: {response.get('content', '')[:100]}...")
