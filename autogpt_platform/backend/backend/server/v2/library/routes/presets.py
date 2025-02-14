import logging
from typing import Annotated, Any

import autogpt_libs.auth as autogpt_auth_lib
import autogpt_libs.utils.cache
import fastapi

import backend.executor
import backend.server.v2.library.db as library_db
import backend.server.v2.library.model as library_model
import backend.util.service

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()


@autogpt_libs.utils.cache.thread_cached
def execution_manager_client() -> backend.executor.ExecutionManager:
    return backend.util.service.get_service_client(backend.executor.ExecutionManager)


@router.get("/presets")
async def get_presets(
    user_id: Annotated[str, fastapi.Depends(autogpt_auth_lib.depends.get_user_id)],
    page: int = 1,
    page_size: int = 10,
) -> library_model.LibraryAgentPresetResponse:
    try:
        presets = await library_db.get_presets(user_id, page, page_size)
        return presets
    except Exception as e:
        logger.exception(f"Exception occurred whilst getting presets: {e}")
        raise fastapi.HTTPException(status_code=500, detail="Failed to get presets")


@router.get("/presets/{preset_id}")
async def get_preset(
    preset_id: str,
    user_id: Annotated[str, fastapi.Depends(autogpt_auth_lib.depends.get_user_id)],
) -> library_model.LibraryAgentPreset:
    try:
        preset = await library_db.get_preset(user_id, preset_id)
        if not preset:
            raise fastapi.HTTPException(
                status_code=404,
                detail=f"Preset {preset_id} not found",
            )
        return preset
    except Exception as e:
        logger.exception(f"Exception occurred whilst getting preset: {e}")
        raise fastapi.HTTPException(status_code=500, detail="Failed to get preset")


@router.post("/presets")
async def create_preset(
    preset: library_model.CreateLibraryAgentPresetRequest,
    user_id: Annotated[str, fastapi.Depends(autogpt_auth_lib.depends.get_user_id)],
) -> library_model.LibraryAgentPreset:
    try:
        return await library_db.upsert_preset(user_id, preset)
    except Exception as e:
        logger.exception(f"Exception occurred whilst creating preset: {e}")
        raise fastapi.HTTPException(status_code=500, detail="Failed to create preset")


@router.put("/presets/{preset_id}")
async def update_preset(
    preset_id: str,
    preset: library_model.CreateLibraryAgentPresetRequest,
    user_id: Annotated[str, fastapi.Depends(autogpt_auth_lib.depends.get_user_id)],
) -> library_model.LibraryAgentPreset:
    try:
        return await library_db.upsert_preset(user_id, preset, preset_id)
    except Exception as e:
        logger.exception(f"Exception occurred whilst updating preset: {e}")
        raise fastapi.HTTPException(status_code=500, detail="Failed to update preset")


@router.delete("/presets/{preset_id}")
async def delete_preset(
    preset_id: str,
    user_id: Annotated[str, fastapi.Depends(autogpt_auth_lib.depends.get_user_id)],
):
    try:
        await library_db.delete_preset(user_id, preset_id)
        return fastapi.Response(status_code=204)
    except Exception as e:
        logger.exception(f"Exception occurred whilst deleting preset: {e}")
        raise fastapi.HTTPException(status_code=500, detail="Failed to delete preset")


@router.post(
    path="/presets/{preset_id}/execute",
    tags=["presets"],
    dependencies=[fastapi.Depends(autogpt_auth_lib.auth_middleware)],
)
async def execute_preset(
    graph_id: str,
    graph_version: int,
    preset_id: str,
    node_input: Annotated[
        dict[str, Any], fastapi.Body(..., embed=True, default_factory=dict)
    ],
    user_id: Annotated[str, fastapi.Depends(autogpt_auth_lib.depends.get_user_id)],
) -> dict[str, Any]:  # FIXME: add proper return type
    try:
        preset = await library_db.get_preset(user_id, preset_id)
        if not preset:
            raise fastapi.HTTPException(status_code=404, detail="Preset not found")

        logger.debug(f"Preset inputs: {preset.inputs}")

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
    except Exception as e:
        msg = str(e).encode().decode("unicode_escape")
        raise fastapi.HTTPException(status_code=400, detail=msg)
