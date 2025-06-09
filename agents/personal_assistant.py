import json
import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent

class PersonalAssistantAgent(BaseAgent):
    """Main coordinator agent that delegates tasks to specialized agents"""
    
    def __init__(self, bedrock_service, tools_service=None):
        super().__init__("personal_assistant", bedrock_service, tools_service)
        self.available_agents = {}
        
    def register_agent(self, agent):
        """Register a specialized agent"""
        self.available_agents[agent.agent_type] = agent
        self.logger.info(f"Registered agent: {agent.agent_type}")
        
    def get_system_prompt(self) -> str:
        agent_capabilities = []
        for agent_type, agent in self.available_agents.items():
            capabilities = agent.get_capabilities()
            agent_capabilities.append(f"- {agent_type}: {', '.join(capabilities)}")
        
        capabilities_text = "\n".join(agent_capabilities)
        
        return f"""You are a Personal Assistant AI that coordinates with specialized agents to help users.

Available Specialized Agents:
{capabilities_text}

Your role is to:
1. Understand user requests and determine which specialized agent(s) can best help
2. Coordinate between multiple agents when needed
3. Provide direct assistance for general queries that don't require specialized agents
4. Maintain context across multi-turn conversations
5. Ensure user requests are handled efficiently and accurately

When you need to delegate to a specialized agent, clearly indicate which agent should handle the task and why.
For simple questions or general conversation, you can respond directly.

Be helpful, conversational, and proactive in understanding user needs."""

    def can_handle(self, task: str, context: Dict[str, Any]) -> bool:
        """Personal assistant can handle any task by delegating or responding directly"""
        return True
        
    async def process_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process task by either delegating to specialized agents or handling directly"""
        try:
            # Analyze the task to determine if delegation is needed
            delegation_decision = await self._analyze_delegation_need(task, context)
            
            if delegation_decision.get('needs_delegation'):
                # Delegate to specialized agent(s)
                return await self._delegate_task(task, context, delegation_decision)
            else:
                # Handle directly as general assistant
                return await self._handle_directly(task, context)
                
        except Exception as e:
            self.logger.error(f"Error processing task: {str(e)}")
            return self.format_error(f"I encountered an error while processing your request: {str(e)}")
    
    async def _analyze_delegation_need(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze if the task needs to be delegated to specialized agents"""
        
        # Create a prompt to analyze the task
        analysis_prompt = f"""Analyze this user request and determine if it needs specialized agent assistance:

User Request: "{task}"

Available Specialized Agents:
- calendar_agent: Schedule management, event creation, meeting planning, date/time queries
- search_agent: Web search, current information, research questions, factual queries
- code_assistant: Programming help, code generation, debugging, technical questions

Respond with JSON in this format:
{{
    "needs_delegation": true/false,
    "recommended_agent": "agent_type" or null,
    "reasoning": "explanation of decision",
    "task_type": "description of task category"
}}

Consider delegation if the request involves:
- Scheduling, calendar, or time-based activities
- Need for current/real-time information or web search
- Programming, coding, or technical development questions

Respond directly (no delegation) for:
- General conversation
- Simple questions you can answer directly
- Personal advice or opinions
- Creative writing or brainstorming"""

        try:
            messages = [{"role": "user", "content": analysis_prompt}]
            response = await self.generate_response(messages, max_tokens=300)
            
            # Parse JSON response
            analysis = json.loads(response.strip())
            return analysis
            
        except (json.JSONDecodeError, Exception) as e:
            self.logger.warning(f"Error analyzing delegation need: {str(e)}")
            # Default to no delegation if analysis fails
            return {
                "needs_delegation": False,
                "recommended_agent": None,
                "reasoning": "Unable to analyze, handling directly",
                "task_type": "general"
            }
    
    async def _delegate_task(self, task: str, context: Dict[str, Any], delegation_decision: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate task to appropriate specialized agent"""
        
        recommended_agent = delegation_decision.get('recommended_agent')
        
        if recommended_agent and recommended_agent in self.available_agents:
            agent = self.available_agents[recommended_agent]
            
            # Check if the agent can handle this task
            if agent.can_handle(task, context):
                self.logger.info(f"Delegating task to {recommended_agent}")
                result = await agent.process_task(task, context)
                
                # Add delegation information to the response
                result['delegated_to'] = recommended_agent
                result['delegation_reasoning'] = delegation_decision.get('reasoning')
                
                return result
            else:
                self.logger.warning(f"Recommended agent {recommended_agent} cannot handle task")
        
        # If delegation fails, handle directly
        return await self._handle_directly(task, context)
    
    async def _handle_directly(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the task directly as a general assistant"""
        
        try:
            # Get conversation history from context
            messages = context.get('messages', [])
            
            # Add the current user message
            messages.append({"role": "user", "content": task})
            
            # Generate response
            response = await self.generate_response(messages)
            
            return self.format_response(response, {
                'handled_directly': True,
                'task_type': 'general_assistance'
            })
            
        except Exception as e:
            self.logger.error(f"Error handling task directly: {str(e)}")
            return self.format_error(f"I'm sorry, I encountered an error while processing your request: {str(e)}")
    
    def get_capabilities(self) -> List[str]:
        """Return capabilities of the personal assistant"""
        capabilities = [
            "General conversation and assistance",
            "Task coordination and delegation",
            "Multi-agent workflow management"
        ]
        
        # Add capabilities from registered agents
        for agent in self.available_agents.values():
            agent_caps = agent.get_capabilities()
            capabilities.extend([f"{cap} (via {agent.agent_type})" for cap in agent_caps])
            
        return capabilities
