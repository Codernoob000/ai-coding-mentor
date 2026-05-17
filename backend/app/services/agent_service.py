import json
import re
from typing import List, Dict, Any, Optional
from app.services.gemini_service import GeminiService
from app.services.mcp_service import MCPService
from app.services.memory_service import MemoryService
from app.core.prompts import MENTOR_SYSTEM_PROMPT
from app.api.v1.schemas.chat import StructuredChatResponse
from app.core.logger import logger

class AgentService:
    def __init__(self, gemini_service: GeminiService, mcp_service: MCPService, memory_service: MemoryService):
        self.gemini = gemini_service
        self.mcp = mcp_service
        self.memory = memory_service

    def _parse_json_safely(self, text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"(\{.*\})", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
        
        logger.error(f"Failed to parse JSON response from model. Raw text: {text[:200]}...")
        return {
            "concept_explanation": "I apologize, I had trouble formatting my response. " + text,
            "code_examples": [],
            "key_takeaway": "Error in response formatting.",
            "mentor_question": "Could you try rephrasing your question?",
            "suggested_next_topic": "General Debugging"
        }

    async def process_message(self, user_id: str, session_id: str, message: str) -> StructuredChatResponse:
        logger.info(f"Orchestrating structured response for session: {session_id}")
        
        context = await self.memory.get_mentor_context(user_id)
        
        system_instruction = MENTOR_SYSTEM_PROMPT.safe_substitute(
            coding_level=context["preferences"]["level"],
            mentor_style=context["preferences"]["mentor_style"],
            weaknesses="\n".join(context["weaknesses"]) if context["weaknesses"] else "None.",
            memories="\n".join(context["recent_memories"]) if context["recent_memories"] else "No history."
        )
        
        # CRITICAL FIX: Use the native tool definition list directly
        # The Gemini SDK expects a list of FunctionDeclarations or a single Tool object.
        tools = self.mcp.get_tool_definitions()
        
        contents = [{"role": "user", "parts": [message]}]
        
        max_steps = 5
        for step in range(max_steps):
            response = await self.gemini.generate_agent_turn(
                contents=contents,
                system_instruction=system_instruction,
                tools=tools
            )
            
            if response.get("blocked"):
                return StructuredChatResponse(
                    concept_explanation="I cannot assist with this request due to safety filters.",
                    key_takeaway="Safety block triggered.",
                    mentor_question="How else can I help you learn coding?",
                    suggested_next_topic="Safety in AI",
                    session_id=session_id
                )
            
            response_part = response["part"]
            contents.append({"role": "model", "parts": [response_part]})
            
            if response.get("function_call"):
                fc = response["function_call"]
                tool_name = fc.name
                tool_args = dict(fc.args) 
                
                tool_result = await self.mcp.execute_tool(tool_name, tool_args)
                
                contents.append({
                    "role": "user",
                    "parts": [{
                        "function_response": {
                            "name": tool_name,
                            "response": {"result": tool_result}
                        }
                    }]
                })
            else:
                raw_text = response["text"]
                structured_data = self._parse_json_safely(raw_text)
                
                # Update memory
                await self.memory.record_interaction(user_id, raw_text)
                
                return StructuredChatResponse(
                    **structured_data,
                    session_id=session_id
                )
                
        return StructuredChatResponse(
            concept_explanation="The reasoning loop timed out. Please simplify your query.",
            key_takeaway="Complexity limit reached.",
            mentor_question="Would you like to focus on one specific part of the code?",
            suggested_next_topic="Modular Programming",
            session_id=session_id
        )
