import asyncio
import logging
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime

from .state import WorkflowState, AgentState
from agents import PersonalAssistantAgent, CalendarAgent, SearchAgent, CodeAssistantAgent
from services import BedrockService, PerplexityService, ToolsService
import config

class MultiAgentWorkflow:
    """LangGraph-inspired multi-agent workflow orchestrator"""
    
    def __init__(self):
        self.logger = logging.getLogger("graph.workflow")
        
        # Initialize services
        self.bedrock_service = BedrockService()
        self.perplexity_service = PerplexityService()
        self.tools_service = ToolsService()
        
        # Initialize agents
        self.agents = self._initialize_agents()
        self.coordinator = self.agents["personal_assistant"]
        
        # Workflow configuration
        self.max_iterations = config.Config.MAX_AGENT_ITERATIONS
        self.timeout = config.Config.AGENT_TIMEOUT
        
        # Active workflows
        self.active_workflows: Dict[str, WorkflowState] = {}
        
        self.logger.info("Multi-agent workflow initialized")
    
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all agents"""
        agents = {}
        
        # Initialize specialized agents
        agents["calendar_agent"] = CalendarAgent(self.bedrock_service, self.tools_service)
        agents["search_agent"] = SearchAgent(self.bedrock_service, self.perplexity_service, self.tools_service)
        agents["code_assistant"] = CodeAssistantAgent(self.bedrock_service, self.tools_service)
        
        # Initialize coordinator and register specialized agents
        coordinator = PersonalAssistantAgent(self.bedrock_service, self.tools_service)
        for agent_type, agent in agents.items():
            coordinator.register_agent(agent)
        
        agents["personal_assistant"] = coordinator
        
        return agents
    
    async def process_user_input(self, user_input: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process user input through the multi-agent workflow"""
        
        # Create or get workflow state
        if not session_id:
            session_id = str(uuid.uuid4())
        
        workflow_state = self._get_or_create_workflow_state(session_id)
        
        try:
            # Add user input to workflow history
            workflow_state.add_workflow_event("user_input", "user", {"content": user_input})
            
            # Process through coordinator
            result = await self._execute_workflow(user_input, workflow_state)
            
            # Update workflow state
            workflow_state.iteration_count += 1
            workflow_state.final_result = result
            
            # Store updated state
            self.active_workflows[session_id] = workflow_state
            
            return {
                "success": True,
                "result": result,
                "session_id": session_id,
                "workflow_state": workflow_state.to_dict()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing user input: {str(e)}")
            workflow_state.add_workflow_event("error", "workflow", {"error": str(e)})
            
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "workflow_state": workflow_state.to_dict()
            }
    
    async def _execute_workflow(self, user_input: str, workflow_state: WorkflowState) -> Dict[str, Any]:
        """Execute the main workflow logic"""
        
        # Prepare context for the coordinator
        context = {
            "messages": workflow_state.get_conversation_history(),
            "global_context": workflow_state.global_context,
            "session_id": workflow_state.session_id
        }
        
        # Get or create agent state for coordinator
        coordinator_state = workflow_state.get_agent_state("personal_assistant")
        if not coordinator_state:
            coordinator_state = AgentState(
                agent_type="personal_assistant",
                session_id=workflow_state.session_id,
                context=context,
                messages=[]
            )
            workflow_state.set_agent_state("personal_assistant", coordinator_state)
        
        # Add user message to coordinator state
        coordinator_state.add_message("user", user_input)
        
        # Process task through coordinator
        workflow_state.current_agent = "personal_assistant"
        workflow_state.add_workflow_event("agent_start", "personal_assistant", {"task": user_input})
        
        try:
            result = await self.coordinator.process_task(user_input, context)
            
            # Update coordinator state
            coordinator_state.last_action = "process_task"
            coordinator_state.last_result = result
            coordinator_state.add_message("assistant", result.get("content", ""))
            
            workflow_state.add_workflow_event("agent_complete", "personal_assistant", {"result": result})
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in workflow execution: {str(e)}")
            coordinator_state.error_count += 1
            workflow_state.add_workflow_event("agent_error", "personal_assistant", {"error": str(e)})
            raise
    
    def _get_or_create_workflow_state(self, session_id: str) -> WorkflowState:
        """Get existing workflow state or create new one"""
        if session_id in self.active_workflows:
            return self.active_workflows[session_id]
        
        return WorkflowState(session_id=session_id)
    
    async def get_workflow_status(self, session_id: str) -> Dict[str, Any]:
        """Get status of a workflow"""
        if session_id not in self.active_workflows:
            return {
                "status": "not_found",
                "session_id": session_id
            }
        
        workflow_state = self.active_workflows[session_id]
        
        return {
            "status": "active" if not workflow_state.is_complete else "complete",
            "session_id": session_id,
            "current_agent": workflow_state.current_agent,
            "iteration_count": workflow_state.iteration_count,
            "agent_count": len(workflow_state.agent_states),
            "last_update": datetime.utcnow().isoformat()
        }
    
    async def clear_workflow(self, session_id: str) -> bool:
        """Clear a workflow from memory"""
        if session_id in self.active_workflows:
            del self.active_workflows[session_id]
            self.logger.info(f"Cleared workflow for session: {session_id}")
            return True
        return False
    
    def get_available_agents(self) -> List[Dict[str, Any]]:
        """Get information about available agents"""
        agent_info = []
        
        for agent_type, agent in self.agents.items():
            info = {
                "agent_type": agent_type,
                "capabilities": agent.get_capabilities(),
                "status": "active"
            }
            agent_info.append(info)
        
        return agent_info
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all services and agents"""
        health_status = {
            "workflow": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {},
            "agents": {},
            "active_workflows": len(self.active_workflows)
        }
        
        # Check services
        try:
            bedrock_health = self.bedrock_service.health_check()
            health_status["services"]["bedrock"] = bedrock_health
        except Exception as e:
            health_status["services"]["bedrock"] = {"status": "unhealthy", "error": str(e)}
        
        try:
            perplexity_health = await self.perplexity_service.health_check()
            health_status["services"]["perplexity"] = perplexity_health
        except Exception as e:
            health_status["services"]["perplexity"] = {"status": "unhealthy", "error": str(e)}
        
        # Check agents
        for agent_type, agent in self.agents.items():
            try:
                health_status["agents"][agent_type] = {
                    "status": "healthy",
                    "capabilities_count": len(agent.get_capabilities())
                }
            except Exception as e:
                health_status["agents"][agent_type] = {
                    "status": "unhealthy", 
                    "error": str(e)
                }
        
        return health_status
