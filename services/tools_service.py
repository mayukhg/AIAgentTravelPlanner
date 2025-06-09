import subprocess
import tempfile
import os
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

class ToolsService:
    """Service for built-in tools: python_repl, editor, shell, journal"""
    
    def __init__(self):
        self.logger = logging.getLogger("services.tools")
        self.journal_file = "assistant_journal.txt"
        
    async def run_python(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute Python code using python_repl equivalent"""
        try:
            # Create a temporary file for the Python code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Execute the Python code
                result = subprocess.run(
                    ['python3', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=os.getcwd()
                )
                
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.returncode != 0 else None,
                    "return_code": result.returncode
                }
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass
                    
        except subprocess.TimeoutExpired:
            self.logger.error("Python code execution timed out")
            return {
                "success": False,
                "output": "",
                "error": f"Code execution timed out after {timeout} seconds",
                "return_code": -1
            }
            
        except Exception as e:
            self.logger.error(f"Error executing Python code: {str(e)}")
            return {
                "success": False,
                "output": "",
                "error": f"Execution error: {str(e)}",
                "return_code": -1
            }
    
    async def run_shell_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute a shell command"""
        try:
            # Basic security check - restrict dangerous commands
            dangerous_commands = ['rm -rf', 'sudo', 'passwd', 'chmod 777', 'dd if=']
            if any(dangerous in command.lower() for dangerous in dangerous_commands):
                return {
                    "success": False,
                    "output": "",
                    "error": "Command blocked for security reasons",
                    "return_code": -1
                }
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.getcwd()
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            self.logger.error("Shell command timed out")
            return {
                "success": False,
                "output": "",
                "error": f"Command timed out after {timeout} seconds",
                "return_code": -1
            }
            
        except Exception as e:
            self.logger.error(f"Error executing shell command: {str(e)}")
            return {
                "success": False,
                "output": "",
                "error": f"Command execution error: {str(e)}",
                "return_code": -1
            }
    
    async def edit_file(self, file_path: str, content: str, operation: str = "write") -> Dict[str, Any]:
        """Edit a file (write, append, or read)"""
        try:
            # Security check - prevent access to sensitive files
            dangerous_paths = ['/etc/', '/usr/', '/bin/', '/sbin/', '/root/']
            if any(dangerous in file_path for dangerous in dangerous_paths):
                return {
                    "success": False,
                    "error": "Access to this file path is restricted",
                    "operation": operation
                }
            
            # Ensure we're working in the current directory or subdirectories
            safe_path = os.path.abspath(file_path)
            current_dir = os.path.abspath(os.getcwd())
            
            if not safe_path.startswith(current_dir):
                return {
                    "success": False,
                    "error": "File path must be within the current directory",
                    "operation": operation
                }
            
            if operation == "read":
                if not os.path.exists(safe_path):
                    return {
                        "success": False,
                        "error": "File does not exist",
                        "operation": operation
                    }
                
                with open(safe_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                
                return {
                    "success": True,
                    "content": file_content,
                    "file_path": file_path,
                    "operation": operation
                }
                
            elif operation == "write":
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(safe_path), exist_ok=True)
                
                with open(safe_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return {
                    "success": True,
                    "message": f"File '{file_path}' written successfully",
                    "file_path": file_path,
                    "operation": operation
                }
                
            elif operation == "append":
                with open(safe_path, 'a', encoding='utf-8') as f:
                    f.write(content)
                
                return {
                    "success": True,
                    "message": f"Content appended to '{file_path}' successfully",
                    "file_path": file_path,
                    "operation": operation
                }
                
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "operation": operation
                }
                
        except Exception as e:
            self.logger.error(f"Error editing file: {str(e)}")
            return {
                "success": False,
                "error": f"File operation error: {str(e)}",
                "file_path": file_path,
                "operation": operation
            }
    
    async def journal_entry(self, entry: str, operation: str = "add") -> Dict[str, Any]:
        """Add entries to or read from the assistant journal"""
        try:
            if operation == "add":
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                journal_entry = f"[{timestamp}] {entry}\n"
                
                with open(self.journal_file, 'a', encoding='utf-8') as f:
                    f.write(journal_entry)
                
                return {
                    "success": True,
                    "message": "Journal entry added successfully",
                    "timestamp": timestamp,
                    "operation": operation
                }
                
            elif operation == "read":
                if not os.path.exists(self.journal_file):
                    return {
                        "success": True,
                        "content": "",
                        "message": "Journal is empty",
                        "operation": operation
                    }
                
                with open(self.journal_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                return {
                    "success": True,
                    "content": content,
                    "operation": operation
                }
                
            elif operation == "clear":
                if os.path.exists(self.journal_file):
                    os.remove(self.journal_file)
                
                return {
                    "success": True,
                    "message": "Journal cleared successfully",
                    "operation": operation
                }
                
            else:
                return {
                    "success": False,
                    "error": f"Unknown journal operation: {operation}",
                    "operation": operation
                }
                
        except Exception as e:
            self.logger.error(f"Error with journal operation: {str(e)}")
            return {
                "success": False,
                "error": f"Journal operation error: {str(e)}",
                "operation": operation
            }
    
    def get_available_tools(self) -> Dict[str, Any]:
        """Get information about available tools"""
        return {
            "python_repl": {
                "description": "Execute Python code",
                "available": True,
                "timeout": 30
            },
            "shell": {
                "description": "Execute shell commands",
                "available": True,
                "timeout": 30,
                "security_note": "Dangerous commands are blocked"
            },
            "editor": {
                "description": "Read, write, and modify files",
                "available": True,
                "security_note": "Access restricted to current directory"
            },
            "journal": {
                "description": "Persistent journal for notes and logging",
                "available": True,
                "file": self.journal_file
            }
        }
