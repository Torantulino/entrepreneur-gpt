import datetime

import prisma.fields
import prisma.models

import backend.data.block
import backend.server.model
import backend.server.v2.library.model


def test_library_agent():
    agent = backend.server.v2.library.model.LibraryAgent(
        id="test-agent-123",
        agent_id="agent-123",
        agent_version=1,
        preset_id=None,
        updated_at=datetime.datetime.now(),
        name="Test Agent",
        description="Test description",
        input_schema={"type": "object", "properties": {}},
        output_schema={"type": "object", "properties": {}},
        is_favorite=False,
        is_created_by_user=False,
        is_latest_version=True,
    )
    assert agent.id == "test-agent-123"
    assert agent.agent_id == "agent-123"
    assert agent.agent_version == 1
    assert agent.name == "Test Agent"
    assert agent.description == "Test description"
    assert agent.is_favorite is False
    assert agent.is_created_by_user is False
    assert agent.is_latest_version is True
    assert agent.input_schema == {"type": "object", "properties": {}}
    assert agent.output_schema == {"type": "object", "properties": {}}


def test_library_agent_with_user_created():
    agent = backend.server.v2.library.model.LibraryAgent(
        id="user-agent-456",
        agent_id="agent-456",
        agent_version=2,
        preset_id=None,
        updated_at=datetime.datetime.now(),
        name="User Created Agent",
        description="An agent created by the user",
        input_schema={"type": "object", "properties": {}},
        output_schema={"type": "object", "properties": {}},
        is_favorite=False,
        is_created_by_user=True,
        is_latest_version=True,
    )
    assert agent.id == "user-agent-456"
    assert agent.agent_id == "agent-456"
    assert agent.agent_version == 2
    assert agent.name == "User Created Agent"
    assert agent.description == "An agent created by the user"
    assert agent.is_favorite is False
    assert agent.is_created_by_user is True
    assert agent.is_latest_version is True
    assert agent.input_schema == {"type": "object", "properties": {}}
    assert agent.output_schema == {"type": "object", "properties": {}}


def test_library_agent_preset():
    preset = backend.server.v2.library.model.LibraryAgentPreset(
        id="preset-123",
        name="Test Preset",
        description="Test preset description",
        agent_id="test-agent-123",
        agent_version=1,
        is_active=True,
        inputs={
            "dictionary": {"key1": "Hello", "key2": "World"},
            "selected_value": "key2",
        },
        updated_at=datetime.datetime.now(),
    )
    assert preset.id == "preset-123"
    assert preset.name == "Test Preset"
    assert preset.description == "Test preset description"
    assert preset.agent_id == "test-agent-123"
    assert preset.agent_version == 1
    assert preset.is_active is True
    assert preset.inputs == {
        "dictionary": {"key1": "Hello", "key2": "World"},
        "selected_value": "key2",
    }


def test_library_agent_preset_response():
    preset = backend.server.v2.library.model.LibraryAgentPreset(
        id="preset-123",
        name="Test Preset",
        description="Test preset description",
        agent_id="test-agent-123",
        agent_version=1,
        is_active=True,
        inputs={
            "dictionary": {"key1": "Hello", "key2": "World"},
            "selected_value": "key2",
        },
        updated_at=datetime.datetime.now(),
    )

    pagination = backend.server.model.Pagination(
        total_items=1, total_pages=1, current_page=1, page_size=10
    )

    response = backend.server.v2.library.model.LibraryAgentPresetResponse(
        presets=[preset], pagination=pagination
    )

    assert len(response.presets) == 1
    assert response.presets[0].id == "preset-123"
    assert response.pagination.total_items == 1
    assert response.pagination.total_pages == 1
    assert response.pagination.current_page == 1
    assert response.pagination.page_size == 10


def test_create_library_agent_preset_request():
    request = backend.server.v2.library.model.CreateLibraryAgentPresetRequest(
        name="New Preset",
        description="New preset description",
        agent_id="agent-123",
        agent_version=1,
        is_active=True,
        inputs={
            "dictionary": {"key1": "Hello", "key2": "World"},
            "selected_value": "key2",
        },
    )

    assert request.name == "New Preset"
    assert request.description == "New preset description"
    assert request.agent_id == "agent-123"
    assert request.agent_version == 1
    assert request.is_active is True
    assert request.inputs == {
        "dictionary": {"key1": "Hello", "key2": "World"},
        "selected_value": "key2",
    }


def test_library_agent_from_db():
    # Create mock DB agent
    db_agent = prisma.models.AgentPreset(
        id="test-agent-123",
        createdAt=datetime.datetime.now(),
        updatedAt=datetime.datetime.now(),
        agentId="agent-123",
        agentVersion=1,
        name="Test Agent",
        description="Test agent description",
        isActive=True,
        userId="test-user-123",
        isDeleted=False,
        InputPresets=[
            prisma.models.AgentNodeExecutionInputOutput(
                id="input-123",
                time=datetime.datetime.now(),
                name="input1",
                data=prisma.fields.Json({"type": "string", "value": "test value"}),
            )
        ],
    )

    # Convert to LibraryAgentPreset
    agent = backend.server.v2.library.model.LibraryAgentPreset.from_db(db_agent)

    assert agent.id == "test-agent-123"
    assert agent.agent_version == 1
    assert agent.is_active is True
    assert agent.name == "Test Agent"
    assert agent.description == "Test agent description"
    assert agent.inputs == {"input1": {"type": "string", "value": "test value"}}
