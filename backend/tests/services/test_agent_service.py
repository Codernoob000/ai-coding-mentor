import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.agent_service import AgentService

@pytest.mark.asyncio
async def test_agent_orchestration_loop(mock_gemini_service, mock_mcp_service):
    # Mock MemoryService
    mock_memory = AsyncMock()
    mock_memory.get_mentor_context.return_value = {
        "preferences": {"level": "beginner", "mentor_style": "socratic"},
        "recent_memories": [],
        "weaknesses": []
    }
    
    agent = AgentService(
        gemini_service=mock_gemini_service,
        mcp_service=mock_mcp_service,
        memory_service=mock_memory
    )
    
    # Setup mock Gemini return for agent turn
    raw_response_text = """<internal_reasoning>The user is asking about loops. I should lead them to use a for loop.</internal_reasoning>
{
  "concept_explanation": "Loops allow you to run the same code multiple times.",
  "code_examples": [],
  "key_takeaway": "Loops are for repetition.",
  "mentor_question": "Have you tried using a for loop?",
  "suggested_next_topic": "While Loops"
}"""
    mock_gemini_service.generate_agent_turn = AsyncMock(return_value={
        "blocked": False,
        "text": raw_response_text,
        "part": MagicMock()
    })
    
    response = await agent.process_message("user1", "session1", "How do I loop?")
    
    # Verify the internal reasoning was stripped out of the returned StructuredChatResponse
    assert response.mentor_question == "Have you tried using a for loop?"
    
    # Make sure internal reasoning is not in the final parsed fields
    assert "internal_reasoning" not in response.concept_explanation
    assert "asking about loops" not in response.concept_explanation
    
    mock_memory.get_mentor_context.assert_called_once_with("user1")
    
    # Ensure full transparency by persisting complete raw interaction (including reasoning)
    mock_memory.record_interaction.assert_called_once_with("user1", raw_response_text)
