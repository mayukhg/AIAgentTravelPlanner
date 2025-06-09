import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class AgentState:
    """State for individual agents"""
    agent_type: str
    session_id: str
    context: Dict[str, Any]
    messages: List[Dict[str, str]]
    last_action: Optional[str] = None
    last_result: Optional[Dict[str, Any]] = None
    error_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentState':
        """Create from dictionary"""
        return cls(**data)
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_recent_messages(self, count: int = 10) -> List[Dict[str, str]]:
        """Get recent messages for context"""
        return self.messages[-count:] if self.messages else []

@dataclass 
class WorkflowState:
    """Overall workflow state for multi-agent coordination"""
    session_id: str
    current_agent: Optional[str] = None
    agent_states: Dict[str, AgentState] = None
    global_context: Dict[str, Any] = None
    workflow_history: List[Dict[str, Any]] = None
    iteration_count: int = 0
    is_complete: bool = False
    final_result: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize mutable fields"""
        if self.agent_states is None:
            self.agent_states = {}
        if self.global_context is None:
            self.global_context = {}
        if self.workflow_history is None:
            self.workflow_history = []
    
    def get_agent_state(self, agent_type: str) -> Optional[AgentState]:
        """Get state for a specific agent"""
        return self.agent_states.get(agent_type)
    
    def set_agent_state(self, agent_type: str, state: AgentState):
        """Set state for a specific agent"""
        self.agent_states[agent_type] = state
    
    def add_workflow_event(self, event_type: str, agent_type: str, data: Dict[str, Any]):
        """Add an event to the workflow history"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "agent_type": agent_type,
            "iteration": self.iteration_count,
            "data": data
        }
        self.workflow_history.append(event)
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get combined conversation history from all agents"""
        all_messages = []
        
        for agent_state in self.agent_states.values():
            all_messages.extend(agent_state.messages)
        
        # Sort by timestamp if available
        try:
            all_messages.sort(key=lambda x: x.get('timestamp', ''))
        except:
            # If sorting fails, return as-is
            pass
            
        return all_messages
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "session_id": self.session_id,
            "current_agent": self.current_agent,
            "agent_states": {k: v.to_dict() for k, v in self.agent_states.items()},
            "global_context": self.global_context,
            "workflow_history": self.workflow_history,
            "iteration_count": self.iteration_count,
            "is_complete": self.is_complete,
            "final_result": self.final_result
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowState':
        """Create from dictionary"""
        # Convert agent_states dict back to AgentState objects
        agent_states = {}
        if "agent_states" in data and data["agent_states"]:
            for k, v in data["agent_states"].items():
                agent_states[k] = AgentState.from_dict(v)
        
        return cls(
            session_id=data["session_id"],
            current_agent=data.get("current_agent"),
            agent_states=agent_states,
            global_context=data.get("global_context", {}),
            workflow_history=data.get("workflow_history", []),
            iteration_count=data.get("iteration_count", 0),
            is_complete=data.get("is_complete", False),
            final_result=data.get("final_result")
        )
    
    def serialize(self) -> str:
        """Serialize to JSON string"""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def deserialize(cls, json_str: str) -> 'WorkflowState':
        """Deserialize from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
