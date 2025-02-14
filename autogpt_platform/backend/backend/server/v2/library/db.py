import logging
from typing import Optional

import fastapi
import prisma.errors
import prisma.fields
import prisma.models
import prisma.types

import backend.data.includes
import backend.server.model
import backend.server.v2.library.model as library_model
import backend.server.v2.store.exceptions as store_exceptions
import backend.server.v2.store.image_gen as store_image_gen
import backend.server.v2.store.media as store_media

logger = logging.getLogger(__name__)


async def get_library_agents(
    user_id: str,
    search_term: Optional[str] = None,
    sort_by: library_model.LibraryAgentSort = library_model.LibraryAgentSort.UPDATED_AT,
    page: int = 1,
    page_size: int = 50,
) -> library_model.LibraryAgentResponse:
    """
    Retrieves a paginated list of LibraryAgent records for a given user.

    Args:
        user_id: The ID of the user whose LibraryAgents we want to retrieve.
        search_term: Optional string to filter agents by name/description.
        sort_by: Sorting field (createdAt, updatedAt, isFavorite, isCreatedByUser).
        page: Current page (1-indexed).
        page_size: Number of items per page.

    Returns:
        A LibraryAgentResponse containing the list of agents and pagination details.

    Raises:
        DatabaseError: If there is an issue fetching from Prisma.
    """
    logger.debug(
        f"Fetching library agents for user_id={user_id}, "
        f"search_term={repr(search_term)}, "
        f"sort_by={sort_by}, page={page}, page_size={page_size}"
    )

    if page < 1 or page_size < 1:
        logger.warning(f"Invalid pagination: page={page}, page_size={page_size}")
        raise store_exceptions.DatabaseError("Invalid pagination input")

    if search_term and len(search_term.strip()) > 100:
        logger.warning(f"Search term too long: {repr(search_term)}")
        raise store_exceptions.DatabaseError("Search term is too long")

    where_clause: prisma.types.LibraryAgentWhereInput = {
        "userId": user_id,
        "isDeleted": False,
        "isArchived": False,
    }

    # Build search filter if applicable
    if search_term:
        where_clause["OR"] = [
            {
                "Agent": {
                    "is": {"name": {"contains": search_term, "mode": "insensitive"}}
                }
            },
            {
                "Agent": {
                    "is": {
                        "description": {"contains": search_term, "mode": "insensitive"}
                    }
                }
            },
        ]

    # Determine sorting
    order_by: prisma.types.LibraryAgentOrderByInput | None = None

    if sort_by == library_model.LibraryAgentSort.CREATED_AT:
        order_by = {"createdAt": "asc"}
    elif sort_by == library_model.LibraryAgentSort.UPDATED_AT:
        order_by = {"updatedAt": "desc"}

    try:
        library_agents = await prisma.models.LibraryAgent.prisma().find_many(
            where=where_clause,
            include={
                "Agent": {
                    "include": {
                        **backend.data.includes.AGENT_GRAPH_INCLUDE,
                        "AgentGraphExecution": {"where": {"userId": user_id}},
                    }
                },
                "Creator": True,
            },
            order=order_by,
            skip=(page - 1) * page_size,
            take=page_size,
        )
        agent_count = await prisma.models.LibraryAgent.prisma().count(
            where=where_clause
        )

        logger.debug(
            f"Retrieved {len(library_agents)} library agents for user #{user_id}"
        )
        return library_model.LibraryAgentResponse(
            agents=[
                library_model.LibraryAgent.from_db(agent) for agent in library_agents
            ],
            pagination=backend.server.model.Pagination(
                total_items=agent_count,
                total_pages=(agent_count + page_size - 1) // page_size,
                current_page=page,
                page_size=page_size,
            ),
        )

    except prisma.errors.PrismaError as e:
        logger.error(f"Database error fetching library agents: {e}")
        raise store_exceptions.DatabaseError("Failed to fetch library agents") from e


async def create_library_agent(
    agent_id: str,
    agent_version: int,
    user_id: str,
) -> prisma.models.LibraryAgent:
    """
    Adds an agent to the user's library (LibraryAgent table).

    Args:
        agent_id: The ID of the agent to add.
        agent_version: The version of the agent to add.
        user_id: The user to whom the agent will be added.

    Returns:
        The newly created LibraryAgent record.

    Raises:
        AgentNotFoundError: If the specified agent does not exist.
        DatabaseError: If there's an error during creation or if image generation fails.
    """
    logger.info(
        f"Creating library agent for graph #{agent_id} v{agent_version}; "
        f"user #{user_id}"
    )

    # Fetch agent graph
    try:
        agent = await prisma.models.AgentGraph.prisma().find_unique(
            where={"graphVersionId": {"id": agent_id, "version": agent_version}}
        )
    except prisma.errors.PrismaError as e:
        logger.exception("Database error fetching agent")
        raise store_exceptions.DatabaseError("Failed to fetch agent") from e

    if not agent:
        raise store_exceptions.AgentNotFoundError(
            f"Agent #{agent_id} v{agent_version} not found"
        )

    # Use .jpeg here since we are generating JPEG images
    filename = f"agent_{agent_id}.jpeg"
    try:
        if not (image_url := await store_media.check_media_exists(user_id, filename)):
            # Generate agent image as JPEG
            image = await store_image_gen.generate_agent_image(agent=agent)

            # Create UploadFile with the correct filename and content_type
            image_file = fastapi.UploadFile(file=image, filename=filename)

            image_url = await store_media.upload_media(
                user_id=user_id, file=image_file, use_file_name=True
            )
    except Exception as e:
        logger.error(f"Error generating and uploading agent image: {e}")
        raise store_exceptions.DatabaseError(
            "Failed to generate and upload agent image"
        ) from e

    try:
        return await prisma.models.LibraryAgent.prisma().create(
            data={
                "image_url": image_url,
                "userId": user_id,
                "agentId": agent_id,
                "agentVersion": agent_version,
                "isCreatedByUser": (user_id == agent.userId),
                "useGraphIsActiveVersion": True,
                "User": {"connect": {"id": agent.userId}},
                "Creator": {"connect": {"id": agent.userId}},
                "Agent": {
                    "connect": {
                        "graphVersionId": {"id": agent_id, "version": agent_version}
                    }
                },
            }
        )
    except prisma.errors.PrismaError as e:
        logger.error(f"Database error creating agent in library: {e}")
        raise store_exceptions.DatabaseError("Failed to create agent in library") from e


async def update_agent_version_in_library(
    user_id: str,
    agent_id: str,
    agent_version: int,
) -> None:
    """
    Updates the agent version in the library if useGraphIsActiveVersion is True.

    Args:
        user_id: Owner of the LibraryAgent.
        agent_id: The agent's ID to update.
        agent_version: The new version of the agent.

    Raises:
        DatabaseError: If there's an error with the update.
    """
    logger.debug(
        f"Updating agent version in library for user #{user_id}, "
        f"agent #{agent_id} v{agent_version}"
    )
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
        logger.error(f"Database error updating agent version in library: {e}")
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
    Updates the specified LibraryAgent record.

    Args:
        library_agent_id: The ID of the LibraryAgent to update.
        user_id: The owner of this LibraryAgent.
        auto_update_version: Whether the agent should auto-update to active version.
        is_favorite: Whether this agent is marked as a favorite.
        is_archived: Whether this agent is archived.
        is_deleted: Whether this agent is deleted.

    Raises:
        DatabaseError: If there's an error in the update operation.
    """
    logger.debug(
        "Updating library agent %s for user %s with auto_update_version=%s, "
        "is_favorite=%s, is_archived=%s, is_deleted=%s",
        library_agent_id,
        user_id,
        auto_update_version,
        is_favorite,
        is_archived,
        is_deleted,
    )
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
        logger.error(f"Database error deleting library agent: {e}")
        raise store_exceptions.DatabaseError("Failed to delete library agent") from e


async def add_store_agent_to_library(
    store_listing_version_id: str, user_id: str
) -> Optional[prisma.models.LibraryAgent]:
    """
    Adds an agent from a store listing version to the user's library if they don't already have it.

    Args:
        store_listing_version_id: The ID of the store listing version containing the agent.
        user_id: The user’s library to which the agent is being added.

    Returns:
        The newly created LibraryAgent if successfully added, or None if the agent already exists.

    Raises:
        AgentNotFoundError: If the store listing or associated agent is not found.
        DatabaseError: If there's an issue creating the LibraryAgent record.
    """
    logger.debug(
        f"Adding agent from store listing version #{store_listing_version_id} "
        f"to library for user #{user_id}"
    )

    try:
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
                f"Store listing version {store_listing_version_id} not found or invalid"
            )

        agent = store_listing_version.Agent
        if agent.userId == user_id:
            logger.warning(
                f"User #{user_id} attempted to add their own agent to their library"
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
                f"User #{user_id} already has agent #{agent.id} in their library"
            )
            return None

        # Create LibraryAgent entry
        updated_agent = await prisma.models.LibraryAgent.prisma().create(
            data={
                "userId": user_id,
                "agentId": agent.id,
                "agentVersion": agent.version,
                "isCreatedByUser": False,
            }
        )
        logger.debug(f"Added agent #{agent.id} to library for user #{user_id}")
        return updated_agent

    except store_exceptions.AgentNotFoundError:
        # Reraise for external handling.
        raise
    except prisma.errors.PrismaError as e:
        logger.error(f"Database error adding agent to library: {e}")
        raise store_exceptions.DatabaseError("Failed to add agent to library") from e


##############################################
########### Presets DB Functions #############
##############################################


async def get_presets(
    user_id: str, page: int, page_size: int
) -> library_model.LibraryAgentPresetResponse:
    """
    Retrieves a paginated list of AgentPresets for the specified user.

    Args:
        user_id: The user ID whose presets are being retrieved.
        page: The current page index (0-based or 1-based, clarify in your domain).
        page_size: Number of items to retrieve per page.

    Returns:
        A LibraryAgentPresetResponse containing a list of presets and pagination info.

    Raises:
        DatabaseError: If there's a database error during the operation.
    """
    logger.debug(
        f"Fetching presets for user #{user_id}, page={page}, page_size={page_size}"
    )

    if page < 0 or page_size < 1:
        logger.warning(
            "Invalid pagination input: page=%d, page_size=%d", page, page_size
        )
        raise store_exceptions.DatabaseError("Invalid pagination parameters")

    try:
        presets_records = await prisma.models.AgentPreset.prisma().find_many(
            where={"userId": user_id},
            skip=page * page_size,
            take=page_size,
        )
        total_items = await prisma.models.AgentPreset.prisma().count(
            where={"userId": user_id}
        )
        total_pages = (total_items + page_size - 1) // page_size

        presets = [
            library_model.LibraryAgentPreset.from_db(preset)
            for preset in presets_records
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
        logger.error(f"Database error getting presets: {e}")
        raise store_exceptions.DatabaseError("Failed to fetch presets") from e


async def get_preset(
    user_id: str, preset_id: str
) -> library_model.LibraryAgentPreset | None:
    """
    Retrieves a single AgentPreset by its ID for a given user.

    Args:
        user_id: The user that owns the preset.
        preset_id: The ID of the preset.

    Returns:
        A LibraryAgentPreset if it exists and matches the user, otherwise None.

    Raises:
        DatabaseError: If there's a database error during the fetch.
    """
    logger.debug(f"Fetching preset #{preset_id} for user #{user_id}")
    try:
        preset = await prisma.models.AgentPreset.prisma().find_unique(
            where={"id": preset_id},
            include={"InputPresets": True},
        )
        if not preset or preset.userId != user_id:
            return None
        return library_model.LibraryAgentPreset.from_db(preset)
    except prisma.errors.PrismaError as e:
        logger.error(f"Database error getting preset: {e}")
        raise store_exceptions.DatabaseError("Failed to fetch preset") from e


async def upsert_preset(
    user_id: str,
    preset: library_model.CreateLibraryAgentPresetRequest,
    preset_id: Optional[str] = None,
) -> library_model.LibraryAgentPreset:
    """
    Creates or updates an AgentPreset for a user.

    Args:
        user_id: The ID of the user creating/updating the preset.
        preset: The preset data used for creation or update.
        preset_id: An optional preset ID to update; if None, a new preset is created.

    Returns:
        The newly created or updated LibraryAgentPreset.

    Raises:
        DatabaseError: If there's a database error in creating or updating the preset.
        ValueError: If attempting to update a non-existent preset.
    """
    logger.debug(
        f"Upserting preset #{preset_id} ({repr(preset.name)}) for user #{user_id}",
    )
    try:
        if preset_id:
            # Update existing preset
            updated = await prisma.models.AgentPreset.prisma().update(
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
            if not updated:
                raise ValueError(f"AgentPreset #{preset_id} not found")
            return library_model.LibraryAgentPreset.from_db(updated)
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
        logger.error(f"Database error upserting preset: {e}")
        raise store_exceptions.DatabaseError("Failed to create preset") from e


async def delete_preset(user_id: str, preset_id: str) -> None:
    """
    Soft-deletes a preset by marking it as isDeleted = True.

    Args:
        user_id: The user that owns the preset.
        preset_id: The ID of the preset to delete.

    Raises:
        DatabaseError: If there's a database error during deletion.
    """
    logger.info("Deleting preset %s for user %s", preset_id, user_id)
    try:
        await prisma.models.AgentPreset.prisma().update_many(
            where={"id": preset_id, "userId": user_id},
            data={"isDeleted": True},
        )
    except prisma.errors.PrismaError as e:
        logger.error(f"Database error deleting preset: {e}")
        raise store_exceptions.DatabaseError("Failed to delete preset") from e
