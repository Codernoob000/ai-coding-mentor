import google.generativeai as genai
from google.generativeai.types import RequestOptions, HarmCategory, HarmBlockThreshold
from google.api_core import exceptions as google_exceptions
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Optional, AsyncGenerator, List, Dict, Any
from app.core.config import settings
from app.core.logger import logger

class GeminiService:
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.GEMINI_MODEL_NAME
        genai.configure(api_key=settings.GEMINI_API_KEY.get_secret_value())
        
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }
        
        # Initialize default model once
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            safety_settings=self.safety_settings
        )

    async def health_check(self) -> bool:
        try:
            await genai.get_model_async(f"models/{self.model_name}")
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def generate_response(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        # Standard implementation kept for direct chat (singleton-safe)
        retryer = AsyncRetrying(
            retry=retry_if_exception_type((
                google_exceptions.InternalServerError,
                google_exceptions.ResourceExhausted,
                google_exceptions.ServiceUnavailable,
            )),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            stop=stop_after_attempt(settings.LLM_MAX_RETRIES),
            reraise=True
        )

        async for attempt in retryer:
            with attempt:
                model = self.model
                if system_instruction:
                    model = genai.GenerativeModel(
                        model_name=self.model_name,
                        system_instruction=system_instruction,
                        safety_settings=self.safety_settings
                    )
                response = await model.generate_content_async(
                    prompt,
                    request_options=RequestOptions(timeout=settings.GEMINI_TIMEOUT_SECONDS)
                )
                return response.text

    async def generate_agent_turn(
        self, 
        contents: List[Dict[str, Any]], 
        system_instruction: Optional[str] = None,
        tools: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes a single turn with tool support. 
        Note: Model re-initialization is currently required by SDK when tools/instructions change per-turn.
        """
        retryer = AsyncRetrying(
            retry=retry_if_exception_type((
                google_exceptions.InternalServerError,
                google_exceptions.ResourceExhausted,
                google_exceptions.ServiceUnavailable,
            )),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            stop=stop_after_attempt(settings.LLM_MAX_RETRIES),
            reraise=True
        )

        async for attempt in retryer:
            with attempt:
                try:
                    # In production, we'd use model.start_chat for better history management
                    model = genai.GenerativeModel(
                        model_name=self.model_name,
                        system_instruction=system_instruction,
                        safety_settings=self.safety_settings,
                        tools=tools if tools else None
                    )

                    response = await model.generate_content_async(
                        contents,
                        request_options=RequestOptions(timeout=settings.GEMINI_TIMEOUT_SECONDS)
                    )

                    if not response.candidates:
                        return {"blocked": True, "text": "No response generated. The model may have filtered your request."}
                    
                    candidate = response.candidates[0]
                    finish_reason = getattr(candidate, 'finish_reason', None)
                    if finish_reason and hasattr(finish_reason, 'name') and finish_reason.name == "SAFETY":
                        return {"blocked": True, "text": "Safety filter blocked response."}

                    part = candidate.content.parts[0]
                    
                    # Detect function calls: empty FunctionCall proto is truthy, so check .name
                    fc = part.function_call
                    has_function_call = fc and hasattr(fc, 'name') and fc.name
                    
                    return {
                        "blocked": False,
                        "function_call": fc if has_function_call else None,
                        "text": getattr(part, 'text', None),
                        "part": part
                    }

                except Exception as e:
                    logger.error(f"Gemini API Turn Error: {e}", exc_info=True)
                    raise
