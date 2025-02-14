import logging
from typing import Optional

import autogpt_libs.auth as autogpt_auth_lib
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

import backend.server.v2.library.db as library_db
import backend.server.v2.library.model as library_model
import backend.server.v2.store.exceptions as store_exceptions

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/agents",
    tags=["library", "private"],
    dependencies=[Depends(autogpt_auth_lib.auth_middleware)],
)


@router.get(
    "",
    response_model=library_model.LibraryAgentResponse,
    responses={
        500: {"description": "Server error", "content": {"application/json": {}}},
    },
)
async def get_library_agents(
    user_id: str = Depends(autogpt_auth_lib.depends.get_user_id),
    search_term: Optional[str] = Query(
        None, description="Search term to filter agents"
    ),
    sort_by: library_model.LibraryAgentSort = Query(
        library_model.LibraryAgentSort.UPDATED_AT,
        description="Sort results by criteria",
    ),
    page: int = Query(
        1,
        ge=1,
        description="Page number to retrieve (must be >= 1)",
    ),
    page_size: int = Query(
        15,
        ge=1,
        description="Number of agents per page (must be >= 1)",
    ),
) -> library_model.LibraryAgentResponse:
    """
    Get all agents in the user's library (both created and saved).

    Args:
        user_id: ID of the authenticated user.
        search_term: Optional search term to filter agents by name/description.
        filter_by: List of filters to apply (favorites, created by user).
        sort_by: List of sorting criteria (created date, updated date).
        page: Page number to retrieve.
        page_size: Number of agents per page.

    Returns:
        A LibraryAgentResponse containing agents and pagination metadata.

    Raises:
        HTTPException: If a server/database error occurs.
    """
    try:
        return await library_db.get_library_agents(
            user_id=user_id,
            search_term=search_term,
            sort_by=sort_by,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        logger.error(f"Could not fetch library agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get library agents",
        ) from e


@router.post(
    "/{store_listing_version_id}",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Agent added successfully"},
        404: {"description": "Store listing version not found"},
        500: {"description": "Server error"},
    },
)
async def add_agent_to_library(
    store_listing_version_id: str,
    user_id: str = Depends(autogpt_auth_lib.depends.get_user_id),
) -> JSONResponse:
    """
    Add an agent from the store to the user's library.

    Args:
        store_listing_version_id: ID of the store listing version to add.
        user_id: ID of the authenticated user.

    Returns:
        201 (Created) on success.

    Raises:
        HTTPException(404): If the listing version is not found.
        HTTPException(500): If a server/database error occurs.
    """
    try:
        await library_db.add_store_agent_to_library(
            store_listing_version_id=store_listing_version_id,
            user_id=user_id,
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Agent added to library successfully"},
        )

    except store_exceptions.AgentNotFoundError:
        logger.warning(f"Agent not found: {store_listing_version_id}")
        raise HTTPException(
            status_code=404,
            detail=f"Store listing version {store_listing_version_id} not found",
        )
    except store_exceptions.DatabaseError as e:
        logger.error(f"Database error occurred whilst adding agent to library: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add agent to library",
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error while adding agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add agent to library",
        ) from e


@router.put(
    "/{library_agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Agent updated successfully"},
        500: {"description": "Server error"},
    },
)
async def update_library_agent(
    library_agent_id: str,
    payload: library_model.LibraryAgentUpdateRequest,
    user_id: str = Depends(autogpt_auth_lib.depends.get_user_id),
) -> JSONResponse:
    """
    Update the library agent with the given fields.

    Args:
        library_agent_id: ID of the library agent to update.
        payload: Fields to update (auto_update_version, is_favorite, etc.).
        user_id: ID of the authenticated user.

    Returns:
        204 (No Content) on success.

    Raises:
        HTTPException(500): If a server/database error occurs.
    """
    try:
        await library_db.update_library_agent(
            library_agent_id=library_agent_id,
            user_id=user_id,
            auto_update_version=payload.auto_update_version,
            is_favorite=payload.is_favorite,
            is_archived=payload.is_archived,
            is_deleted=payload.is_deleted,
        )
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content={"message": "Agent updated successfully"},
        )
    except store_exceptions.DatabaseError as e:
        logger.exception(f"Database error while updating library agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update library agent",
        ) from e
    except Exception as e:
        logger.exception(f"Unexpected error while updating library agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update library agent",
        ) from e
