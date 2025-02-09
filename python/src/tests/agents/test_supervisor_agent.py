import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
from typing import List

from multi_agent_orchestrator.agents import (
    SupervisorAgent,
    SupervisorAgentOptions,
    BedrockLLMAgent,
    BedrockLLMAgentOptions,
    Agent
)
from multi_agent_orchestrator.storage import InMemoryChatStorage
from multi_agent_orchestrator.types import ConversationMessage, ParticipantRole
from multi_agent_orchestrator.utils import AgentTools, AgentTool, Logger


@pytest.fixture
def mock_boto3_client():
    with patch('boto3.client') as mock_client:
        yield mock_client

def mock_storage():
    storage = MagicMock(spec=InMemoryChatStorage)
    storage.save_chat_message = AsyncMock()
    storage.fetch_chat = AsyncMock(return_value=[])
    storage.fetch_all_chats = AsyncMock(return_value=[])
    return storage


# class MockStorage(InMemoryChatStorage):
#     @pytest.mark.asyncio
#     async def save_chat_message(self, *args, **kwargs):
#         pass

#     @pytest.mark.asyncio
#     async def fetch_chat(self, *args, **kwargs):
#         return []

#     @pytest.mark.asyncio
#     async def fetch_all_chats(self, *args, **kwargs):
#         return []

#     @pytest.mark.asyncio
#     async def fetch_chat_messages(self, *args, **kwargs):
#         return []


class MockBedrockLLMAgent(BedrockLLMAgent):
    async def process_request(self, *args, **kwargs):
        response = ConversationMessage(
            role=ParticipantRole.ASSISTANT.value,
            content=[{"text": "Mock response"}]
        )
        return response


@pytest.fixture
def supervisor_agent(mock_boto3_client):
    lead_agent = MockBedrockLLMAgent(BedrockLLMAgentOptions(
        name="Supervisor",
        description="Test lead_agent",
    ))

    team_member = MockBedrockLLMAgent(BedrockLLMAgentOptions(
        name="Team Member",
        description="Test team member"
    ))

    return SupervisorAgent(SupervisorAgentOptions(
        lead_agent=lead_agent,
        team=[team_member],
        storage=mock_storage(),
        trace=True
    ))

@pytest.mark.asyncio
async def test_supervisor_agent_initialization(mock_boto3_client):
    """Test SupervisorAgent initialization"""
    lead_agent = MockBedrockLLMAgent(BedrockLLMAgentOptions(
        name="Supervisor",
        description="Test lead_agent"
    ))

    team = [MockBedrockLLMAgent(BedrockLLMAgentOptions(
        name="Team Member",
        description="Test team member"
    ))]

    agent = SupervisorAgent(SupervisorAgentOptions(
        lead_agent=lead_agent,
        team=team
    ))

    assert agent.lead_agent == lead_agent
    assert len(agent.team) == 1
    assert isinstance(agent.storage, InMemoryChatStorage)
    assert agent.trace is None
    assert isinstance(agent.supervisor_tools, AgentTools)

@pytest.mark.asyncio
async def test_supervisor_agent_validation(mock_boto3_client):
    """Test SupervisorAgent validation"""
    with pytest.raises(ValueError, match="Supervisor must be BedrockLLMAgent or AnthropicAgent"):
        SupervisorAgent(SupervisorAgentOptions(
            lead_agent=MagicMock(spec=Agent),
            team=[]
        ))

    lead_agent = MockBedrockLLMAgent(BedrockLLMAgentOptions(
        name="Supervisor",
        description="Test lead_agent"
    ))
    lead_agent.tool_config = {'tool':{}}

    with pytest.raises(ValueError, match="Supervisor tools are managed by SupervisorAgent"):
        SupervisorAgent(SupervisorAgentOptions(
            lead_agent=lead_agent,
            team=[]
        ))

def test_send_message(supervisor_agent, mock_boto3_client):
    """Test send_message functionality"""
    agent = MockBedrockLLMAgent(BedrockLLMAgentOptions(
        name="Test Agent",
        description="Test agent"
    ))
    response = supervisor_agent.send_message(
        agent=agent,
        content="Test message",
        user_id="test_user",
        session_id="test_session",
        additional_params={}
    )

    assert "Test Agent: Mock response" in response
    assert supervisor_agent.storage.save_chat_messages.assert_awaited_once


@pytest.mark.asyncio
async def test_send_messages(supervisor_agent):
    """Test send_messages functionality"""
    messages = [
        {"recipient": "Team Member", "content": "Test message 1"},
        {"recipient": "Team Member", "content": "Test message 2"}
    ]

    response = await supervisor_agent.send_messages(messages)
    assert response
    assert "Team Member: Mock response" in response

    response = await supervisor_agent.send_messages([])
    assert response == ''

@pytest.mark.asyncio
async def test_process_request(supervisor_agent):
    """Test process_request functionality"""
    input_text = "Test input"
    user_id = "test_user"
    session_id = "test_session"
    chat_history = []

    response = await supervisor_agent.process_request(
        input_text,
        user_id,
        session_id,
        chat_history
    )

    assert response
    assert response.role == ParticipantRole.ASSISTANT.value
    assert response.content[0]["text"] == "Mock response"

@pytest.mark.asyncio
async def test_format_agents_memory(supervisor_agent):
    """Test _format_agents_memory functionality"""
    agents_history = [
        ConversationMessage(
            role=ParticipantRole.USER.value,
            content=[{"text": "User message"}]
        ),
        ConversationMessage(
            role=ParticipantRole.ASSISTANT.value,
            content=[{"text": "Assistant message"}]
        )
    ]

    memory = supervisor_agent._format_agents_memory(agents_history)
    assert "user:User message" in memory
    assert "assistant:Assistant message" in memory

@pytest.mark.asyncio
async def test_supervisor_agent_with_custom_tools(mock_boto3_client):
    """Test SupervisorAgent with custom tools"""
    def mock_tool_function(*args, **kwargs):
        return "Tool result"

    custom_tool = AgentTool(
        name="test_tool",
        description="Test tool",
        properties={
            "param": {
                "type": "string",
                "description": "Test parameter"
            }
        },
        required=["param"],
        func=mock_tool_function
    )

    lead_agent = MockBedrockLLMAgent(BedrockLLMAgentOptions(
        name="Supervisor",
        description="Test lead_agent"
    ))

    agent = SupervisorAgent(SupervisorAgentOptions(
        lead_agent=lead_agent,
        team=[],
        extra_tools=[custom_tool]
    ))

    assert len(agent.supervisor_tools.tools) > 1
    assert any(tool.name == "test_tool" for tool in agent.supervisor_tools.tools)

@pytest.mark.asyncio
async def test_supervisor_agent_with_custom_tools_(mock_boto3_client):
    """Test SupervisorAgent with custom tools"""
    def mock_tool_function(*args, **kwargs):
        return "Tool result"

    custom_tool = AgentTool(
        name="test_tool",
        description="Test tool",
        properties={
            "param": {
                "type": "string",
                "description": "Test parameter"
            }
        },
        required=["param"],
        func=mock_tool_function
    )

    lead_agent = MockBedrockLLMAgent(BedrockLLMAgentOptions(
        name="Supervisor",
        description="Test lead_agent"
    ))

    agent = SupervisorAgent(SupervisorAgentOptions(
        lead_agent=lead_agent,
        team=[],
        extra_tools=AgentTools(tools=[custom_tool])
    ))

    assert len(agent.supervisor_tools.tools) > 1
    assert any(tool.name == "test_tool" for tool in agent.supervisor_tools.tools)


@pytest.mark.asyncio
async def test_supervisor_agent_with_extra_tools(mock_boto3_client):

    lead_agent = MockBedrockLLMAgent(BedrockLLMAgentOptions(
        name="Supervisor",
        description="Test lead_agent"
    ))


    with pytest.raises(Exception, match="extra_tools must be Tools object or list of Tool objects"):
        agent = SupervisorAgent(SupervisorAgentOptions(
            lead_agent=lead_agent,
            team=[],
            extra_tools=[{'tool':'here is my tool'}]
        ))

    with pytest.raises(Exception, match="extra_tools must be Tools object or list of Tool objects"):
        agent = SupervisorAgent(SupervisorAgentOptions(
            lead_agent=lead_agent,
            team=[],
            extra_tools="here is my tool"
        ))




@pytest.mark.asyncio
async def test_supervisor_agent_error_handling(mock_boto3_client):
    """Test SupervisorAgent error handling"""
    class FailingMockAgent(MockBedrockLLMAgent):
        async def process_request(self, *args, **kwargs):
            raise Exception("Test error")

    lead_agent = FailingMockAgent(BedrockLLMAgentOptions(
        name="Failing Supervisor",
        description="Test failing lead_agent"
    ))

    agent = SupervisorAgent(SupervisorAgentOptions(
        lead_agent=lead_agent,
        team=[]
    ))

    with pytest.raises(Exception, match="Test error"):
        await agent.process_request(
            "Test input",
            "test_user",
            "test_session",
            []
        )

@pytest.mark.asyncio
async def test_supervisor_agent_parallel_processing(mock_boto3_client):
    """Test parallel processing of messages"""
    class SlowMockAgent(MockBedrockLLMAgent):
        async def process_request(self, *args, **kwargs):
            await asyncio.sleep(0.1)
            return await super().process_request(*args, **kwargs)

    team = [
        SlowMockAgent(BedrockLLMAgentOptions(name=f"Agent{i}", description=f"Test agent {i}"))
        for i in range(3)
    ]

    lead_agent = MockBedrockLLMAgent(BedrockLLMAgentOptions(
        name="Supervisor",
        description="Test lead_agent"
    ))

    agent = SupervisorAgent(SupervisorAgentOptions(
        lead_agent=lead_agent,
        team=team
    ))

    messages = [
        {"recipient": f"Agent{i}", "content": f"Test message {i}"}
        for i in range(3)
    ]

    start_time = asyncio.get_event_loop().time()
    response = await agent.send_messages(messages)
    end_time = asyncio.get_event_loop().time()

    # Should take approximately 0.1 seconds, not 0.3 seconds
    assert end_time - start_time < 0.2
    assert response.count("Mock response") == 3

@pytest.mark.asyncio
async def test_supervisor_agent_memory_management(mock_boto3_client):
    """Test memory management functionality"""
    lead_agent = MockBedrockLLMAgent(BedrockLLMAgentOptions(
        name="Supervisor",
        description="Test lead_agent"
    ))

    agent = SupervisorAgent(SupervisorAgentOptions(
        lead_agent=lead_agent,
        team=[],
        storage=mock_storage()
    ))

    # Test message storage
    user_id = "test_user"
    session_id = "test_session"
    input_text = "Test input"

    response = await agent.process_request(input_text, user_id, session_id, [])
    history = await agent.storage.fetch_all_chats(user_id, session_id)
