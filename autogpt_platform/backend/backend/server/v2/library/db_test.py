from datetime import datetime

import prisma.errors
import prisma.models
import pytest
from prisma import Prisma

import backend.data.includes
import backend.server.v2.library.db as db
import backend.server.v2.store.exceptions


@pytest.fixture(autouse=True)
async def setup_prisma():
    # Don't register client if already registered
    try:
        Prisma()
    except prisma.errors.ClientAlreadyRegisteredError:
        pass
    yield


@pytest.mark.asyncio
async def test_get_library_agents(mocker):
    # Mock data
    mock_user_created = [
        prisma.models.AgentGraph(
            id="agent1",
            version=1,
            name="Test Agent 1",
            description="Test Description 1",
            userId="test-user",
            isActive=True,
            createdAt=datetime.now(),
            isTemplate=False,
        )
    ]

    mock_library_agents = [
        prisma.models.LibraryAgent(
            id="ua1",
            userId="test-user",
            agentId="agent2",
            agentVersion=1,
            isCreatedByUser=False,
            isDeleted=False,
            isArchived=False,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            isFavorite=False,
            useGraphIsActiveVersion=True,
            Agent=prisma.models.AgentGraph(
                id="agent2",
                version=1,
                name="Test Agent 2",
                description="Test Description 2",
                userId="other-user",
                isActive=True,
                createdAt=datetime.now(),
                isTemplate=False,
            ),
        )
    ]

    # Mock prisma calls
    mock_agent_graph = mocker.patch("prisma.models.AgentGraph.prisma")
    mock_agent_graph.return_value.find_many = mocker.AsyncMock(
        return_value=mock_user_created
    )

    mock_library_agent = mocker.patch("prisma.models.LibraryAgent.prisma")
    mock_library_agent.return_value.find_many = mocker.AsyncMock(
        return_value=mock_library_agents
    )

    # Call function
    result = await db.get_library_agents("test-user")

    # Verify results
    assert len(result) == 1
    assert result[0].id == "ua1"
    assert result[0].name == "Test Agent 2"
    assert result[0].description == "Test Description 2"
    assert result[0].is_created_by_user is False
    assert result[0].is_latest_version is True
    assert result[0].is_favorite is False
    assert result[0].agent_id == "agent2"
    assert result[0].agent_version == 1
    assert result[0].preset_id is None


@pytest.mark.asyncio
async def test_add_agent_to_library(mocker):
    # Mock data
    mock_store_listing = prisma.models.StoreListingVersion(
        id="version123",
        version=1,
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
        agentId="agent1",
        agentVersion=1,
        slug="test-agent",
        name="Test Agent",
        subHeading="Test Agent Subheading",
        imageUrls=["https://example.com/image.jpg"],
        description="Test Description",
        categories=["test"],
        isFeatured=False,
        isDeleted=False,
        isAvailable=True,
        isApproved=True,
        Agent=prisma.models.AgentGraph(
            id="agent1",
            version=1,
            name="Test Agent",
            description="Test Description",
            userId="creator",
            isActive=True,
            createdAt=datetime.now(),
            isTemplate=False,
        ),
    )

    # Mock prisma calls
    mock_store_listing_version = mocker.patch(
        "prisma.models.StoreListingVersion.prisma"
    )
    mock_store_listing_version.return_value.find_unique = mocker.AsyncMock(
        return_value=mock_store_listing
    )

    mock_library_agent = mocker.patch("prisma.models.LibraryAgent.prisma")
    mock_library_agent.return_value.find_first = mocker.AsyncMock(return_value=None)
    mock_library_agent.return_value.create = mocker.AsyncMock()

    # Call function
    await db.add_store_agent_to_library("version123", "test-user")

    # Verify mocks called correctly
    mock_store_listing_version.return_value.find_unique.assert_called_once_with(
        where={"id": "version123"}, include={"Agent": True}
    )
    mock_library_agent.return_value.find_first.assert_called_once_with(
        where={
            "userId": "test-user",
            "agentId": "agent1",
            "agentVersion": 1,
        }
    )
    mock_library_agent.return_value.create.assert_called_once_with(
        data=prisma.types.LibraryAgentCreateInput(
            userId="test-user", agentId="agent1", agentVersion=1, isCreatedByUser=False
        )
    )


@pytest.mark.asyncio
async def test_add_agent_to_library_not_found(mocker):
    # Mock prisma calls
    mock_store_listing_version = mocker.patch(
        "prisma.models.StoreListingVersion.prisma"
    )
    mock_store_listing_version.return_value.find_unique = mocker.AsyncMock(
        return_value=None
    )

    # Call function and verify exception
    with pytest.raises(backend.server.v2.store.exceptions.AgentNotFoundError):
        await db.add_store_agent_to_library("version123", "test-user")

    # Verify mock called correctly
    mock_store_listing_version.return_value.find_unique.assert_called_once_with(
        where={"id": "version123"}, include={"Agent": True}
    )
