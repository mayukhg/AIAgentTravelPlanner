import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent

class SearchAgent(BaseAgent):
    """Specialized agent for web search and information retrieval using Perplexity"""
    
    def __init__(self, bedrock_service, perplexity_service, tools_service=None):
        super().__init__("search_agent", bedrock_service, tools_service)
        self.perplexity_service = perplexity_service
        
    def get_system_prompt(self) -> str:
        return """You are a Search Assistant AI specialized in finding and providing current information from the web.

Your capabilities include:
- Conducting web searches for current information
- Finding factual data and recent news
- Research assistance across various topics
- Providing accurate, cited information
- Summarizing search results clearly
- Distinguishing between reliable and unreliable sources

When processing search requests:
1. Identify the core information need
2. Use web search to find current, accurate information
3. Synthesize multiple sources when appropriate
4. Provide clear, well-structured responses
5. Include source citations when relevant
6. Indicate when information might be time-sensitive

Always prioritize accuracy and recency of information. If you cannot find reliable information on a topic, clearly state this limitation.

For search queries, be precise and use appropriate keywords to get the best results."""

    def can_handle(self, task: str, context: Dict[str, Any]) -> bool:
        """Determine if this is a search-related task"""
        search_keywords = [
            'search', 'find', 'look up', 'research', 'what is', 'who is',
            'when did', 'where is', 'how much', 'latest', 'current',
            'news', 'recent', 'today', 'information about', 'tell me about',
            'weather', 'stock', 'price', 'compare', 'reviews', 'facts'
        ]
        
        task_lower = task.lower()
        return any(keyword in task_lower for keyword in search_keywords)
    
    async def process_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process search-related tasks using Perplexity API"""
        try:
            # Determine if this needs a web search or can be answered directly
            needs_search = await self._analyze_search_need(task, context)
            
            if needs_search:
                return await self._perform_web_search(task, context)
            else:
                return await self._handle_direct_response(task, context)
                
        except Exception as e:
            self.logger.error(f"Error processing search task: {str(e)}")
            return self.format_error(f"I encountered an error while searching for information: {str(e)}")
    
    async def _analyze_search_need(self, task: str, context: Dict[str, Any]) -> bool:
        """Analyze if the task requires web search for current information"""
        
        # Keywords that typically require web search
        current_info_keywords = [
            'current', 'latest', 'recent', 'today', 'now', 'news',
            'weather', 'stock', 'price', 'market', 'update',
            'this year', 'this month', 'this week'
        ]
        
        # Topics that often need current information
        time_sensitive_topics = [
            'weather', 'stocks', 'news', 'events', 'prices',
            'schedule', 'status', 'availability', 'hours'
        ]
        
        task_lower = task.lower()
        
        # Check for explicit current information requests
        if any(keyword in task_lower for keyword in current_info_keywords):
            return True
            
        # Check for time-sensitive topics
        if any(topic in task_lower for topic in time_sensitive_topics):
            return True
            
        # Check for question words that often need current info
        question_patterns = ['what is the current', 'what are the latest', 'how much does', 'when is the next']
        if any(pattern in task_lower for pattern in question_patterns):
            return True
            
        # Default to search for factual questions
        if task_lower.startswith(('what', 'who', 'when', 'where', 'how', 'which')):
            return True
            
        return False
    
    async def _perform_web_search(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform web search using Perplexity API"""
        try:
            # Use Perplexity for web search
            search_result = await self.perplexity_service.search(
                query=task,
                system_prompt="You are a helpful assistant that provides accurate, current information. Be concise but comprehensive. Include relevant details and cite sources when appropriate."
            )
            
            if search_result.get('success'):
                content = search_result.get('content', '')
                citations = search_result.get('citations', [])
                
                # Format the response with citations
                formatted_response = content
                if citations:
                    formatted_response += "\n\n**Sources:**\n"
                    for i, citation in enumerate(citations[:5], 1):  # Limit to top 5 citations
                        formatted_response += f"{i}. {citation}\n"
                
                return self.format_response(
                    formatted_response,
                    {
                        'search_performed': True,
                        'citations': citations,
                        'action_performed': 'web_search'
                    }
                )
            else:
                # Fallback to direct response if search fails
                self.logger.warning("Web search failed, falling back to direct response")
                return await self._handle_direct_response(task, context)
                
        except Exception as e:
            self.logger.error(f"Error performing web search: {str(e)}")
            # Fallback to direct response
            return await self._handle_direct_response(task, context)
    
    async def _handle_direct_response(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the task with direct AI response (no web search)"""
        try:
            messages = context.get('messages', [])
            messages.append({"role": "user", "content": task})
            
            # Add context about not having current web data
            enhanced_messages = messages + [{
                "role": "system", 
                "content": "Note: You are responding based on your training data and do not have access to current web information for this response. If the user needs current/live information, suggest they ask for a web search."
            }]
            
            response = await self.generate_response(enhanced_messages)
            
            return self.format_response(
                response,
                {
                    'search_performed': False,
                    'action_performed': 'direct_response',
                    'note': 'Response based on training data, not current web search'
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error handling direct response: {str(e)}")
            return self.format_error(f"Failed to process your request: {str(e)}")
    
    async def _format_search_response(self, search_result: str, citations: List[str]) -> str:
        """Format search results with proper citations"""
        formatted_response = search_result
        
        if citations:
            formatted_response += "\n\n**Sources:**\n"
            for i, citation in enumerate(citations[:5], 1):  # Limit to 5 citations
                formatted_response += f"{i}. [{citation}]({citation})\n"
        
        return formatted_response
    
    def get_capabilities(self) -> List[str]:
        """Return search agent capabilities"""
        return [
            "Web search for current information",
            "Research assistance and fact-finding",
            "News and current events updates",
            "Market data and pricing information",
            "Weather and location-based queries",
            "Comparative analysis and reviews",
            "Source verification and citation"
        ]
