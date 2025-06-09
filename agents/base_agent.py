import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

class BaseAgent(ABC):
    """Base class for all agents in the multi-agent system"""
    
    def __init__(self, agent_type: str, bedrock_service, tools_service=None):
        self.agent_type = agent_type
        self.bedrock_service = bedrock_service
        self.tools_service = tools_service
        self.logger = logging.getLogger(f"agents.{agent_type}")
        
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass
    
    @abstractmethod
    def can_handle(self, task: str, context: Dict[str, Any]) -> bool:
        """Determine if this agent can handle the given task"""
        pass
    
    @abstractmethod
    async def process_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the given task and return results"""
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
