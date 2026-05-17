import os
from typing import Optional, List, Dict, Any
import google.generativeai as genai
from app.core.filesystem import SafeFileSystem
from app.core.logger import logger

class MCPService:
    """
    Model Context Protocol (MCP) Service Layer.
    Orchestrates filesystem tools for the Gemini Agent.
    """
    
    def __init__(self, workspace_root: Optional[str] = None):
        root = workspace_root or os.getenv("WORKSPACE_ROOT", "./workspace")
        self.fs = SafeFileSystem(root)
        logger.info(f"MCP Service initialized with workspace: {root}")

    def get_tool_definitions(self) -> List[genai.types.FunctionDeclaration]:
        """
        Returns Gemini-native FunctionDeclaration objects.
        Explicitly using the SDK classes avoids TypeError during model initialization.
        """
        return [
            genai.types.FunctionDeclaration(
                name="read_source_code",
                description="Read the content of a source code file for analysis.",
                parameters={
                    "type": "OBJECT",
                    "properties": {
                        "file_path": {
                            "type": "STRING",
                            "description": "Path to the file relative to the project root."
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            genai.types.FunctionDeclaration(
                name="list_files",
                description="List all code files in the project to understand structure.",
                parameters={
                    "type": "OBJECT",
                    "properties": {
                        "directory": {
                            "type": "STRING",
                            "description": "Directory to list, defaults to root '.'."
                        }
                    }
                }
            )
        ]

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        logger.info(f"MCP Tool Executing: {name}", extra={"args": list(arguments.keys())})
        
        try:
            if name == "read_source_code":
                path = arguments.get("file_path")
                if not path:
                    return "Error: file_path argument is required."
                content = await self.fs.read_file_safe(path)
                return f"Content of {path} retrieved ({len(content)} chars):\n\n{content}"
                
            elif name == "list_files":
                directory = arguments.get("directory", ".")
                files = await self.fs.list_project_files(directory)
                return f"Files found ({len(files)} items):\n" + "\n".join(files)
                
            else:
                return f"Error: Tool '{name}' not found."
                
        except FileNotFoundError as e:
            return f"Error: {str(e)}"
        except ValueError as e:
            return f"Security Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected MCP tool error: {e}", exc_info=True)
            return "Error: An unexpected system error occurred while accessing the filesystem."
