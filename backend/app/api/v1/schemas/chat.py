from pydantic import BaseModel, Field
from typing import Optional, List

class CodeExample(BaseModel):
    title: str = Field(..., description="A short title for the code snippet.")
    language: str = Field(..., description="The programming language (e.g., 'python', 'javascript').")
    code: str = Field(..., description="The actual code snippet.")

class StructuredChatResponse(BaseModel):
    concept_explanation: str = Field(..., description="Detailed explanation of the concept in plain text/paragraphs.")
    code_examples: List[CodeExample] = Field(default_factory=list, description="List of relevant code examples.")
    key_takeaway: str = Field(..., description="A concise one-sentence summary of the lesson.")
    mentor_question: str = Field(..., description="A Socratic question to lead the user to the next realization.")
    suggested_next_topic: str = Field(..., description="A recommendation for what to study next.")
    session_id: str = Field(..., description="The session ID associated with the chat.")

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000, description="The user's message.")
    session_id: Optional[str] = Field(None, description="Optional session ID.")

class HealthResponse(BaseModel):
    status: str
    environment: str
    api_key_configured: bool
