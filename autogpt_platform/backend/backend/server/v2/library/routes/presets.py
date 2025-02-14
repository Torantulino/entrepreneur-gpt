import logging
from typing import Annotated, Any

import autogpt_libs.auth as autogpt_auth_lib
import autogpt_libs.utils.cache
from fastapi import APIRouter, Body, Depends, HTTPException, status

import backend.executor
import backend.server.v2.library.db as db
import backend.server.v2.library.model as models
import backend.util.service

logger = logging.getLogger(__name__)

router = APIRouter()


@autogpt_libs.utils.cache.thread_cached
def execution_manager_client() -> backend.executor.ExecutionManager:
    """Return a cached instance of ExecutionManager client."""
    return backend.util.service.get_service_client(backend.executor.ExecutionManager)


@router.get(
    "/presets",
    response_model=models.LibraryAgentPresetResponse,  # Replace with your actual response model
    summary="List presets",
    description="Retrieve a paginated list of presets for the current user.",
)
async def get_presets(
    user_id: str = Depends(autogpt_auth_lib.depends.get_user_id),
    page: int = 1,
    page_size: int = 10,
) -> models.LibraryAgentPresetResponse:
    """
    Retrieve a paginated list of presets for the current user.

    Args:
        user_id (str): ID of the authenticated user.
        page (int): Page number for pagination.
        page_size (int): Number of items per page.

    Returns:
        models.LibraryAgentPresetResponse: A response containing the list of presets.
    """
    try:
        return await db.get_presets(user_id, page, page_size)
    except Exception as e:
        logger.exception(f"Exception occurred while getting presets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get presets",
        )


@router.get(
    "/presets/{preset_id}",
    response_model=models.LibraryAgentPreset,  # Replace with your actual response model
    summary="Get a specific preset",
    description="Retrieve details for a specific preset by its ID.",
)
async def get_preset(
    preset_id: str,
    user_id: str = Depends(autogpt_auth_lib.depends.get_user_id),
) -> models.LibraryAgentPreset:
    """
    Retrieve details for a specific preset by its ID.

    Args:
        preset_id (str): ID of the preset to retrieve.
        user_id (str): ID of the authenticated user.

    Returns:
        models.LibraryAgentPreset: The preset details.

    Raises:
        HTTPException: If the preset is not found or an error occurs.
    """
    try:
        preset = await db.get_preset(user_id, preset_id)
        if not preset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Preset {preset_id} not found",
            )
        return preset
    except Exception as e:
        logger.exception(f"Exception occurred whilst getting preset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get preset",
        )


@router.post(
    "/presets",
    response_model=models.LibraryAgentPreset,  # Replace with your actual response model
    summary="Create a new preset",
    description="Create a new preset for the current user.",
)
async def create_preset(
    preset: models.CreateLibraryAgentPresetRequest,
    user_id: str = Depends(autogpt_auth_lib.depends.get_user_id),
) -> models.LibraryAgentPreset:
    """
    Create a new library agent preset. Automatically corrects node_input format if needed.

    Args:
        preset (models.CreateLibraryAgentPresetRequest): The preset data to create.
        user_id (str): ID of the authenticated user.

    Returns:
        models.LibraryAgentPreset: The created preset.

    Raises:
        HTTPException: If an error occurs while creating the preset.
    """
    try:
        return await db.upsert_preset(user_id, preset)
    except Exception as e:
        logger.exception(f"Exception occurred while creating preset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create preset",
        )


@router.put(
    "/presets/{preset_id}",
    response_model=models.LibraryAgentPreset,  # Replace with your actual response model
    summary="Update an existing preset",
    description="Update an existing preset by its ID.",
)
async def update_preset(
    preset_id: str,
    preset: models.CreateLibraryAgentPresetRequest,
    user_id: str = Depends(autogpt_auth_lib.depends.get_user_id),
) -> models.LibraryAgentPreset:
    """
    Update an existing library agent preset. If the preset doesn't exist, it may be created.

    Args:
        preset_id (str): ID of the preset to update.
        preset (models.CreateLibraryAgentPresetRequest): The preset data to update.
        user_id (str): ID of the authenticated user.

    Returns:
        models.LibraryAgentPreset: The updated preset.

    Raises:
        HTTPException: If an error occurs while updating the preset.
    """
    try:
        return await db.upsert_preset(user_id, preset, preset_id)
    except Exception as e:
        logger.exception(f"Exception occurred whilst updating preset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preset",
        )


@router.delete(
    "/presets/{preset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a preset",
    description="Delete an existing preset by its ID.",
)
async def delete_preset(
    preset_id: str,
    user_id: str = Depends(autogpt_auth_lib.depends.get_user_id),
) -> None:
    """
    Delete a preset by its ID. Returns 204 No Content on success.

    Args:
        preset_id (str): ID of the preset to delete.
        user_id (str): ID of the authenticated user.

    Raises:
        HTTPException: If an error occurs while deleting the preset.
    """
    try:
        await db.delete_preset(user_id, preset_id)
    except Exception as e:
        logger.exception(f"Exception occurred whilst deleting preset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete preset",
        )


@router.post(
    "/presets/{preset_id}/execute",
    tags=["presets"],
    summary="Execute a preset",
    description="Execute a preset with the given graph and node input for the current user.",
)
async def execute_preset(
    graph_id: str,
    graph_version: int,
    preset_id: str,
    node_input: Annotated[dict[str, Any], Body(..., embed=True, default_factory=dict)],
    user_id: str = Depends(autogpt_auth_lib.depends.get_user_id),
) -> dict[str, Any]:  # FIXME: add proper return type
    """
    Execute a preset given graph parameters, returning the execution ID on success.

    Args:
        graph_id (str): ID of the graph to execute.
        graph_version (int): Version of the graph to execute.
        preset_id (str): ID of the preset to execute.
        node_input (Dict[Any, Any]): Input data for the node.
        user_id (str): ID of the authenticated user.

    Returns:
        Dict[str, Any]: A response containing the execution ID.

    Raises:
        HTTPException: If the preset is not found or an error occurs while executing the preset.
    """
    try:
        preset = await db.get_preset(user_id, preset_id)
        if not preset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Preset not found",
            )

        # Merge input overrides with preset inputs
        merged_node_input = preset.inputs | node_input

        execution = execution_manager_client().add_execution(
            graph_id=graph_id,
            graph_version=graph_version,
            data=merged_node_input,
            user_id=user_id,
            preset_id=preset_id,
        )

        logger.debug(f"Execution added: {execution} with input: {merged_node_input}")

        return {"id": execution.graph_exec_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Exception occurred while executing preset: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
