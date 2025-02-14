import logging
from typing import Annotated, Sequence

import autogpt_libs.auth as autogpt_auth_lib
import fastapi

import backend.server.v2.library.db as library_db
import backend.server.v2.library.model as library_model
import backend.server.v2.store.exceptions as store_exceptions

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()


@router.get(
    "/agents",
    tags=["library", "private"],
    dependencies=[fastapi.Depends(autogpt_auth_lib.auth_middleware)],
)
async def get_library_agents(
    user_id: Annotated[str, fastapi.Depends(autogpt_auth_lib.depends.get_user_id)]
) -> Sequence[library_model.LibraryAgent]:
    """
    Get all agents in the user's library, including both created and saved agents.
    """
    try:
        agents = await library_db.get_library_agents(user_id)
        return agents
    except Exception as e:
        logger.exception(f"Exception occurred whilst getting library agents: {e}")
        raise fastapi.HTTPException(
            status_code=500, detail="Failed to get library agents"
        )


@router.post(
    "/agents/{store_listing_version_id}",
    tags=["library", "private"],
    dependencies=[fastapi.Depends(autogpt_auth_lib.auth_middleware)],
    status_code=201,
)
async def add_agent_to_library(
    store_listing_version_id: str,
    user_id: Annotated[str, fastapi.Depends(autogpt_auth_lib.depends.get_user_id)],
) -> fastapi.Response:
    """
    Add an agent from the store to the user's library.

    Args:
        store_listing_version_id (str): ID of the store listing version to add
        user_id (str): ID of the authenticated user

    Returns:
        fastapi.Response: 201 status code on success

    Raises:
        HTTPException: If there is an error adding the agent to the library
    """
    try:
        # Use the database function to add the agent to the library
        await library_db.add_store_agent_to_library(store_listing_version_id, user_id)
        return fastapi.Response(status_code=201)

    except store_exceptions.AgentNotFoundError:
        raise fastapi.HTTPException(
            status_code=404,
            detail=f"Store listing version {store_listing_version_id} not found",
        )
    except store_exceptions.DatabaseError as e:
        logger.exception(f"Database error occurred whilst adding agent to library: {e}")
        raise fastapi.HTTPException(
            status_code=500, detail="Failed to add agent to library"
        )
    except Exception as e:
        logger.exception(
            f"Unexpected exception occurred whilst adding agent to library: {e}"
        )
        raise fastapi.HTTPException(
            status_code=500, detail="Failed to add agent to library"
        )


@router.put(
    "/agents/{library_agent_id}",
    tags=["library", "private"],
    dependencies=[fastapi.Depends(autogpt_auth_lib.auth_middleware)],
    status_code=204,
)
async def update_library_agent(
    library_agent_id: str,
    user_id: Annotated[str, fastapi.Depends(autogpt_auth_lib.depends.get_user_id)],
    auto_update_version: bool = False,
    is_favorite: bool = False,
    is_archived: bool = False,
    is_deleted: bool = False,
) -> fastapi.Response:
    """
    Update the library agent with the given fields.

    Args:
        library_agent_id (str): ID of the library agent to update
        user_id (str): ID of the authenticated user
        auto_update_version (bool): Whether to auto-update the agent version
        is_favorite (bool): Whether the agent is marked as favorite
        is_archived (bool): Whether the agent is archived
        is_deleted (bool): Whether the agent is deleted

    Returns:
        fastapi.Response: 204 status code on success

    Raises:
        HTTPException: If there is an error updating the library agent
    """
    try:
        # Use the database function to update the library agent
        await library_db.update_library_agent(
            library_agent_id,
            user_id,
            auto_update_version,
            is_favorite,
            is_archived,
            is_deleted,
        )
        return fastapi.Response(status_code=204)

    except store_exceptions.DatabaseError as e:
        logger.exception(f"Database error occurred whilst updating library agent: {e}")
        raise fastapi.HTTPException(
            status_code=500, detail="Failed to update library agent"
        )
    except Exception as e:
        logger.exception(
            f"Unexpected exception occurred whilst updating library agent: {e}"
        )
        raise fastapi.HTTPException(
            status_code=500, detail="Failed to update library agent"
        )
