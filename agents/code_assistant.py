import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent

class CodeAssistantAgent(BaseAgent):
    """Specialized agent for programming help and code generation"""
    
    def __init__(self, bedrock_service, tools_service=None):
        super().__init__("code_assistant", bedrock_service, tools_service)
        
    def get_system_prompt(self) -> str:
        return """You are a Code Assistant AI specialized in programming help and software development.

Your capabilities include:
- Code generation in multiple programming languages
- Debugging assistance and error resolution
- Code review and optimization suggestions
- Architecture and design pattern guidance
- API integration help
- Testing and documentation assistance
- Explaining complex programming concepts

When helping with code:
1. Provide clear, well-commented code examples
2. Explain the logic and approach used
3. Consider best practices and security implications
4. Offer alternative solutions when appropriate
5. Help with debugging by analyzing error messages
6. Suggest improvements and optimizations

Languages you're proficient in:
- Python, JavaScript, Java, C++, C#, Go, Rust
- Web technologies: HTML, CSS, React, Vue, Angular
- Databases: SQL, NoSQL, ORMs
- Cloud platforms and DevOps tools
- Machine learning and data science libraries

Always write production-ready code with proper error handling, documentation, and following industry best practices."""

    def can_handle(self, task: str, context: Dict[str, Any]) -> bool:
        """Determine if this is a code/programming-related task"""
        code_keywords = [
            'code', 'program', 'script', 'function', 'debug', 'error',
            'python', 'javascript', 'java', 'cpp', 'html', 'css',
            'react', 'vue', 'angular', 'node', 'flask', 'django',
            'sql', 'database', 'api', 'algorithm', 'class', 'method',
            'variable', 'loop', 'condition', 'syntax', 'compile',
            'runtime', 'exception', 'library', 'framework', 'git',
            'deploy', 'test', 'unit test', 'refactor', 'optimize'
        ]
        
        task_lower = task.lower()
        return any(keyword in task_lower for keyword in code_keywords)
    
    async def process_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process programming-related tasks"""
        try:
            # Analyze the type of coding assistance needed
            assistance_type = await self._analyze_coding_task(task, context)
            
            task_type = assistance_type.get('task_type')
            
            if task_type == 'code_generation':
                return await self._generate_code(task, context, assistance_type)
            elif task_type == 'debugging':
                return await self._help_debug(task, context, assistance_type)
            elif task_type == 'code_review':
                return await self._review_code(task, context, assistance_type)
            elif task_type == 'explanation':
                return await self._explain_code(task, context, assistance_type)
            elif task_type == 'tool_usage':
                return await self._handle_tool_usage(task, context, assistance_type)
            else:
                return await self._general_coding_help(task, context)
                
        except Exception as e:
            self.logger.error(f"Error processing coding task: {str(e)}")
            return self.format_error(f"I encountered an error while helping with your code: {str(e)}")
    
    async def _analyze_coding_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the coding task to determine the type of assistance needed"""
        
        analysis_prompt = f"""Analyze this programming request and determine the type of assistance needed:

User Request: "{task}"

Determine the task type and extract relevant details. Respond with JSON in this format:
{{
    "task_type": "code_generation|debugging|code_review|explanation|tool_usage|general",
    "programming_language": "detected language or null",
    "complexity": "simple|medium|complex",
    "specific_help": "specific area of help needed",
    "reasoning": "explanation of the analysis"
}}

Task type guidelines:
- code_generation: "write", "create", "generate", "build", "implement"
- debugging: "error", "bug", "fix", "debug", "not working", "exception"
- code_review: "review", "optimize", "improve", "best practices", "refactor"
- explanation: "explain", "how does", "what is", "understand", "concept"
- tool_usage: mentions of "python_repl", "editor", "shell", "journal" or wanting to run/execute code
- general: other programming questions or guidance"""

        try:
            messages = [{"role": "user", "content": analysis_prompt}]
            response = await self.generate_response(messages, max_tokens=300)
            
            import json
            analysis = json.loads(response.strip())
            return analysis
            
        except Exception as e:
            self.logger.warning(f"Error analyzing coding task: {str(e)}")
            return {
                "task_type": "general",
                "programming_language": None,
                "complexity": "medium",
                "specific_help": "general programming assistance",
                "reasoning": "Unable to analyze, treating as general help"
            }
    
    async def _generate_code(self, task: str, context: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code based on the user's request"""
        try:
            language = analysis.get('programming_language', 'Python')
            
            enhanced_prompt = f"""Generate code for this request: {task}

Requirements:
- Use {language} if specified, otherwise choose the most appropriate language
- Include clear comments explaining the code
- Follow best practices and handle edge cases
- Provide working, production-ready code
- Include example usage if applicable

Provide the code with explanations."""

            messages = context.get('messages', [])
            messages.append({"role": "user", "content": enhanced_prompt})
            
            response = await self.generate_response(messages, max_tokens=1500)
            
            return self.format_response(
                response,
                {
                    'code_generated': True,
                    'programming_language': language,
                    'action_performed': 'code_generation'
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error generating code: {str(e)}")
            return self.format_error(f"Failed to generate code: {str(e)}")
    
    async def _help_debug(self, task: str, context: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Help debug code issues"""
        try:
            debug_prompt = f"""Help debug this issue: {task}

Please provide:
1. Analysis of the problem
2. Possible causes
3. Step-by-step debugging approach
4. Corrected code if applicable
5. Prevention tips for similar issues

Be thorough and educational in your debugging assistance."""

            messages = context.get('messages', [])
            messages.append({"role": "user", "content": debug_prompt})
            
            response = await self.generate_response(messages, max_tokens=1200)
            
            return self.format_response(
                response,
                {
                    'debugging_help': True,
                    'action_performed': 'debugging'
                }
            )
            
        except Exception e:
            self.logger.error(f"Error helping with debugging: {str(e)}")
            return self.format_error(f"Failed to provide debugging help: {str(e)}")
    
    async def _review_code(self, task: str, context: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Review and provide feedback on code"""
        return await self._general_coding_help(task, context)
    
    async def _explain_code(self, task: str, context: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Explain code concepts or specific code snippets"""
        return await self._general_coding_help(task, context)
    
    async def _handle_tool_usage(self, task: str, context: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle requests involving built-in tools like python_repl, editor, etc."""
        try:
            if not self.tools_service:
                return self.format_error("Built-in tools are not available in this session.")
            
            # Determine which tool to use
            task_lower = task.lower()
            
            if 'python_repl' in task_lower or 'run python' in task_lower or 'execute python' in task_lower:
                return await self._use_python_repl(task, context)
            elif 'editor' in task_lower or 'edit file' in task_lower or 'create file' in task_lower:
                return await self._use_editor(task, context)
            elif 'shell' in task_lower or 'command' in task_lower or 'terminal' in task_lower:
                return await self._use_shell(task, context)
            elif 'journal' in task_lower or 'note' in task_lower:
                return await self._use_journal(task, context)
            else:
                return await self._general_coding_help(task, context)
                
        except Exception as e:
            self.logger.error(f"Error handling tool usage: {str(e)}")
            return self.format_error(f"Failed to use the requested tool: {str(e)}")
    
    async def _use_python_repl(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use Python REPL tool"""
        try:
            # Extract Python code from the request
            code_to_run = await self._extract_python_code(task)
            
            if code_to_run:
                result = await self.tools_service.run_python(code_to_run)
                
                response = f"**Python Code Executed:**\n```python\n{code_to_run}\n```\n\n**Output:**\n```\n{result.get('output', '')}\n```"
                
                if result.get('error'):
                    response += f"\n\n**Error:**\n```\n{result['error']}\n```"
                
                return self.format_response(
                    response,
                    {
                        'tool_used': 'python_repl',
                        'code_executed': code_to_run,
                        'execution_result': result,
                        'action_performed': 'tool_usage'
                    }
                )
            else:
                return self.format_error("I couldn't identify Python code to execute in your request.")
                
        except Exception as e:
            self.logger.error(f"Error using Python REPL: {str(e)}")
            return self.format_error(f"Failed to execute Python code: {str(e)}")
    
    async def _extract_python_code(self, task: str) -> str:
        """Extract Python code from user request"""
        # Simple extraction - look for code blocks or python-like syntax
        lines = task.split('\n')
        code_lines = []
        in_code_block = False
        
        for line in lines:
            if '```python' in line or '```py' in line:
                in_code_block = True
                continue
            elif '```' in line and in_code_block:
                in_code_block = False
                continue
            elif in_code_block:
                code_lines.append(line)
            elif any(keyword in line for keyword in ['print(', 'def ', 'import ', 'from ', '=']):
                code_lines.append(line)
        
        return '\n'.join(code_lines) if code_lines else None
    
    async def _use_editor(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use editor tool"""
        # Implementation for editor tool usage
        return self.format_response("Editor tool functionality is being implemented.")
    
    async def _use_shell(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use shell tool"""
        # Implementation for shell tool usage
        return self.format_response("Shell tool functionality is being implemented.")
    
    async def _use_journal(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use journal tool"""
        # Implementation for journal tool usage
        return self.format_response("Journal tool functionality is being implemented.")
    
    async def _general_coding_help(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide general coding assistance"""
        try:
            messages = context.get('messages', [])
            messages.append({"role": "user", "content": task})
            
            response = await self.generate_response(messages, max_tokens=1200)
            
            return self.format_response(
                response,
                {
                    'action_performed': 'general_coding_help'
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error providing general coding help: {str(e)}")
            return self.format_error(f"Failed to provide coding assistance: {str(e)}")
    
    def get_capabilities(self) -> List[str]:
        """Return code assistant capabilities"""
        return [
            "Code generation in multiple languages",
            "Debugging and error resolution",
            "Code review and optimization",
            "Programming concept explanations",
            "Algorithm and data structure help",
            "API integration assistance",
            "Testing and documentation guidance",
            "Built-in tool integration (python_repl, editor, shell, journal)"
        ]
