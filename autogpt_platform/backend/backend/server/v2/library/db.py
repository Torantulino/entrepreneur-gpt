import logging

import prisma.errors
import prisma.fields
import prisma.models
import prisma.types

import backend.server.model
import backend.server.v2.library.model as library_model
import backend.server.v2.store.exceptions as store_exceptions

logger = logging.getLogger(__name__)


async def get_library_agents(
    user_id: str, search_query: str | None = None
) -> list[library_model.LibraryAgent]:
    logger.debug(
        f"Fetching library agents for user_id={user_id} search_query={search_query}"
    )

    if search_query and len(search_query.strip()) > 100:
        logger.warning(f"Search query too long: {search_query}")
        raise store_exceptions.DatabaseError("Search query is too long.")

    where_clause: prisma.types.LibraryAgentWhereInput = {
        "userId": user_id,
        "isDeleted": False,
        "isArchived": False,
    }

    if search_query:
        where_clause["OR"] = [
            {
                "Agent": {
                    "is": {"name": {"contains": search_query, "mode": "insensitive"}}
                }
            },
            {
                "Agent": {
                    "is": {
                        "description": {"contains": search_query, "mode": "insensitive"}
                    }
                }
            },
        ]

    try:
        library_agents = await prisma.models.LibraryAgent.prisma().find_many(
            where=where_clause,
            include={
                "Agent": {
                    "include": {
                        "AgentNodes": {"include": {"Input": True, "Output": True}}
                    }
                }
            },
            order=[{"updatedAt": "desc"}],
        )
        logger.debug(f"Retrieved {len(library_agents)} agents for user_id={user_id}.")
        return [library_model.LibraryAgent.from_db(agent) for agent in library_agents]
    except prisma.errors.PrismaError as e:
        logger.error(f"Database error fetching library agents: {e}")
        raise store_exceptions.DatabaseError("Unable to fetch library agents.")


async def create_library_agent(
    agent_id: str, agent_version: int, user_id: str
) -> prisma.models.LibraryAgent:
    """
    Adds an agent to the user's library (LibraryAgent table)
    """

    try:
        return await prisma.models.LibraryAgent.prisma().create(
            data={
                "userId": user_id,
                "agentId": agent_id,
                "agentVersion": agent_version,
                "isCreatedByUser": False,
                "useGraphIsActiveVersion": True,
            }
        )
    except prisma.errors.PrismaError as e:
        logger.error(f"Database error creating agent to library: {str(e)}")
        raise store_exceptions.DatabaseError("Failed to create agent to library") from e


async def update_agent_version_in_library(
    user_id: str, agent_id: str, agent_version: int
) -> None:
    """
    Updates the agent version in the library
    """
    try:
        library_agent = await prisma.models.LibraryAgent.prisma().find_first_or_raise(
            where={
                "userId": user_id,
                "agentId": agent_id,
                "useGraphIsActiveVersion": True,
            },
        )
        await prisma.models.LibraryAgent.prisma().update(
            where={"id": library_agent.id},
            data={
                "Agent": {
                    "connect": {
                        "graphVersionId": {"id": agent_id, "version": agent_version}
                    },
                },
            },
        )
    except prisma.errors.PrismaError as e:
        logger.error(f"Database error updating agent version in library: {str(e)}")
        raise store_exceptions.DatabaseError(
            "Failed to update agent version in library"
        ) from e


async def update_library_agent(
    library_agent_id: str,
    user_id: str,
    auto_update_version: bool = False,
    is_favorite: bool = False,
    is_archived: bool = False,
    is_deleted: bool = False,
) -> None:
    """
    Updates the library agent with the given fields
    """
    try:
        await prisma.models.LibraryAgent.prisma().update_many(
            where={"id": library_agent_id, "userId": user_id},
            data={
                "useGraphIsActiveVersion": auto_update_version,
                "isFavorite": is_favorite,
                "isArchived": is_archived,
                "isDeleted": is_deleted,
            },
        )
    except prisma.errors.PrismaError as e:
        logger.error(f"Database error updating library agent: {str(e)}")
        raise store_exceptions.DatabaseError("Failed to update library agent") from e


async def delete_library_agent_by_graph_id(graph_id: str, user_id: str) -> None:
    """
    Deletes a library agent for the given user
    """
    try:
        await prisma.models.LibraryAgent.prisma().delete_many(
            where={"agentId": graph_id, "userId": user_id}
        )
    except prisma.errors.PrismaError as e:
        logger.error(f"Database error deleting library agent: {str(e)}")
        raise store_exceptions.DatabaseError("Failed to delete library agent") from e


async def add_store_agent_to_library(
    store_listing_version_id: str, user_id: str
) -> None:
    """
    Finds the agent from the store listing version and adds it to the user's library (LibraryAgent table)
    if they don't already have it
    """
    logger.debug(
        f"Adding agent from store listing version {store_listing_version_id} to library for user {user_id}"
    )

    try:
        # Get store listing version to find agent
        store_listing_version = (
            await prisma.models.StoreListingVersion.prisma().find_unique(
                where={"id": store_listing_version_id}, include={"Agent": True}
            )
        )

        if not store_listing_version or not store_listing_version.Agent:
            logger.warning(
                f"Store listing version not found: {store_listing_version_id}"
            )
            raise store_exceptions.AgentNotFoundError(
                f"Store listing version {store_listing_version_id} not found"
            )

        agent = store_listing_version.Agent

        if agent.userId == user_id:
            logger.warning(
                f"User {user_id} cannot add their own agent to their library"
            )
            raise store_exceptions.DatabaseError("Cannot add own agent to library")

        # Check if user already has this agent
        existing_user_agent = await prisma.models.LibraryAgent.prisma().find_first(
            where={
                "userId": user_id,
                "agentId": agent.id,
                "agentVersion": agent.version,
            }
        )

        if existing_user_agent:
            logger.debug(
                f"User {user_id} already has agent {agent.id} in their library"
            )
            return

        # Create LibraryAgent entry
        await prisma.models.LibraryAgent.prisma().create(
            data={
                "userId": user_id,
                "agentId": agent.id,
                "agentVersion": agent.version,
                "isCreatedByUser": False,
            }
        )
        logger.debug(f"Added agent {agent.id} to library for user {user_id}")

    except store_exceptions.AgentNotFoundError:
        raise
    except prisma.errors.PrismaError as e:
        logger.error(f"Database error adding agent to library: {str(e)}")
        raise store_exceptions.DatabaseError("Failed to add agent to library") from e


##############################################
########### Presets DB Functions #############
##############################################


async def get_presets(
    user_id: str, page: int, page_size: int
) -> library_model.LibraryAgentPresetResponse:
    try:
        presets = await prisma.models.AgentPreset.prisma().find_many(
            where={"userId": user_id},
            skip=page * page_size,
            take=page_size,
        )

        total_items = await prisma.models.AgentPreset.prisma().count(
            where={"userId": user_id},
        )
        total_pages = (total_items + page_size - 1) // page_size

        presets = [
            library_model.LibraryAgentPreset.from_db(preset) for preset in presets
        ]

        return library_model.LibraryAgentPresetResponse(
            presets=presets,
            pagination=backend.server.model.Pagination(
                total_items=total_items,
                total_pages=total_pages,
                current_page=page,
                page_size=page_size,
            ),
        )

    except prisma.errors.PrismaError as e:
        logger.error(f"Database error getting presets: {str(e)}")
        raise store_exceptions.DatabaseError("Failed to fetch presets") from e


async def get_preset(
    user_id: str, preset_id: str
) -> library_model.LibraryAgentPreset | None:
    try:
        preset = await prisma.models.AgentPreset.prisma().find_unique(
            where={"id": preset_id}, include={"InputPresets": True}
        )
        if not preset or preset.userId != user_id:
            return None
        return library_model.LibraryAgentPreset.from_db(preset)
    except prisma.errors.PrismaError as e:
        logger.error(f"Database error getting preset: {str(e)}")
        raise store_exceptions.DatabaseError("Failed to fetch preset") from e


async def upsert_preset(
    user_id: str,
    preset: library_model.CreateLibraryAgentPresetRequest,
    preset_id: str | None = None,
) -> library_model.LibraryAgentPreset:
    try:
        if preset_id:
            # Update existing preset
            new_preset = await prisma.models.AgentPreset.prisma().update(
                where={"id": preset_id},
                data={
                    "name": preset.name,
                    "description": preset.description,
                    "isActive": preset.is_active,
                    "InputPresets": {
                        "create": [
                            {"name": name, "data": prisma.fields.Json(data)}
                            for name, data in preset.inputs.items()
                        ]
                    },
                },
                include={"InputPresets": True},
            )
            if not new_preset:
                raise ValueError(f"AgentPreset #{preset_id} not found")
        else:
            # Create new preset
            new_preset = await prisma.models.AgentPreset.prisma().create(
                data={
                    "userId": user_id,
                    "name": preset.name,
                    "description": preset.description,
                    "agentId": preset.agent_id,
                    "agentVersion": preset.agent_version,
                    "isActive": preset.is_active,
                    "InputPresets": {
                        "create": [
                            {"name": name, "data": prisma.fields.Json(data)}
                            for name, data in preset.inputs.items()
                        ]
                    },
                },
                include={"InputPresets": True},
            )
        return library_model.LibraryAgentPreset.from_db(new_preset)
    except prisma.errors.PrismaError as e:
        logger.error(f"Database error creating preset: {str(e)}")
        raise store_exceptions.DatabaseError("Failed to create preset") from e


async def delete_preset(user_id: str, preset_id: str) -> None:
    try:
        await prisma.models.AgentPreset.prisma().update_many(
            where={"id": preset_id, "userId": user_id},
            data={"isDeleted": True},
        )
    except prisma.errors.PrismaError as e:
        logger.error(f"Database error deleting preset: {str(e)}")
        raise store_exceptions.DatabaseError("Failed to delete preset") from e
