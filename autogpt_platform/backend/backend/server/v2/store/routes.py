import json
import logging
import tempfile
import typing
import urllib.parse

import autogpt_libs.auth.depends
import autogpt_libs.auth.middleware
import fastapi
import fastapi.responses
from fastapi.encoders import jsonable_encoder

import backend.data.block
import backend.data.graph
import backend.server.v2.store.db
import backend.server.v2.store.image_gen
import backend.server.v2.store.media
import backend.server.v2.store.model

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()


##############################################
############### Profile Endpoints ############
##############################################


@router.get(
    "/profile",
    tags=["store", "private"],
    response_model=backend.server.v2.store.model.ProfileDetails,
)
async def get_profile(
    user_id: typing.Annotated[
        str, fastapi.Depends(autogpt_libs.auth.depends.get_user_id)
    ]
):
    """
    Get the profile details for the authenticated user.
    """
    try:
        profile = await backend.server.v2.store.db.get_user_profile(user_id)
        if profile is None:
            return fastapi.responses.JSONResponse(
                status_code=404,
                content={"detail": "Profile not found"},
            )
        return profile
    except Exception:
        logger.exception("Exception occurred whilst getting user profile")
        return fastapi.responses.JSONResponse(
            status_code=500,
            content={"detail": "An error occurred while retrieving the user profile"},
        )


@router.post(
    "/profile",
    tags=["store", "private"],
    dependencies=[fastapi.Depends(autogpt_libs.auth.middleware.auth_middleware)],
    response_model=backend.server.v2.store.model.CreatorDetails,
)
async def update_or_create_profile(
    profile: backend.server.v2.store.model.Profile,
    user_id: typing.Annotated[
        str, fastapi.Depends(autogpt_libs.auth.depends.get_user_id)
    ],
):
    """
    Update the store profile for the authenticated user.

    Args:
        profile (Profile): The updated profile details
        user_id (str): ID of the authenticated user

    Returns:
        CreatorDetails: The updated profile

    Raises:
        HTTPException: If there is an error updating the profile
    """
    try:
        updated_profile = await backend.server.v2.store.db.update_profile(
            user_id=user_id, profile=profile
        )
        return updated_profile
    except Exception:
        logger.exception("Exception occurred whilst updating profile")
        return fastapi.responses.JSONResponse(
            status_code=500,
            content={"detail": "An error occurred while updating the user profile"},
        )


##############################################
############### Agent Endpoints ##############
##############################################


@router.get(
    "/agents",
    tags=["store", "public"],
    response_model=backend.server.v2.store.model.StoreAgentsResponse,
)
async def get_agents(
    featured: bool = False,
    creator: str | None = None,
    sorted_by: str | None = None,
    search_query: str | None = None,
    category: str | None = None,
    page: int = 1,
    page_size: int = 20,
):
    """
    Get a paginated list of agents from the store with optional filtering and sorting.

    Args:
        featured (bool, optional): Filter to only show featured agents. Defaults to False.
        creator (str | None, optional): Filter agents by creator username. Defaults to None.
        sorted_by (str | None, optional): Sort agents by "runs" or "rating". Defaults to None.
        search_query (str | None, optional): Search agents by name, subheading and description. Defaults to None.
        category (str | None, optional): Filter agents by category. Defaults to None.
        page (int, optional): Page number for pagination. Defaults to 1.
        page_size (int, optional): Number of agents per page. Defaults to 20.

    Returns:
        StoreAgentsResponse: Paginated list of agents matching the filters

    Raises:
        HTTPException: If page or page_size are less than 1

    Used for:
    - Home Page Featured Agents
    - Home Page Top Agents
    - Search Results
    - Agent Details - Other Agents By Creator
    - Agent Details - Similar Agents
    - Creator Details - Agents By Creator
    """
    if page < 1:
        raise fastapi.HTTPException(
            status_code=422, detail="Page must be greater than 0"
        )

    if page_size < 1:
        raise fastapi.HTTPException(
            status_code=422, detail="Page size must be greater than 0"
        )

    try:
        agents = await backend.server.v2.store.db.get_store_agents(
            featured=featured,
            creator=creator,
            sorted_by=sorted_by,
            search_query=search_query,
            category=category,
            page=page,
            page_size=page_size,
        )
        return agents
    except Exception:
        logger.exception("Exception occured whilst getting store agents")
        return fastapi.responses.JSONResponse(
            status_code=500,
            content={"detail": "An error occurred while retrieving the store agents"},
        )


@router.get(
    "/agents/{username}/{agent_name}",
    tags=["store", "public"],
    response_model=backend.server.v2.store.model.StoreAgentDetails,
)
async def get_agent(username: str, agent_name: str):
    """
    This is only used on the AgentDetails Page

    It returns the store listing agents details.
    """
    try:
        username = urllib.parse.unquote(username).lower()
        # URL decode the agent name since it comes from the URL path
        agent_name = urllib.parse.unquote(agent_name).lower()
        agent = await backend.server.v2.store.db.get_store_agent_details(
            username=username, agent_name=agent_name
        )
        return agent
    except Exception:
        logger.exception("Exception occurred whilst getting store agent details")
        return fastapi.responses.JSONResponse(
            status_code=500,
            content={
                "detail": "An error occurred while retrieving the store agent details"
            },
        )


@router.post(
    "/agents/{username}/{agent_name}/review",
    tags=["store"],
    dependencies=[fastapi.Depends(autogpt_libs.auth.middleware.auth_middleware)],
    response_model=backend.server.v2.store.model.StoreReview,
)
async def create_review(
    username: str,
    agent_name: str,
    review: backend.server.v2.store.model.StoreReviewCreate,
    user_id: typing.Annotated[
        str, fastapi.Depends(autogpt_libs.auth.depends.get_user_id)
    ],
):
    """
    Create a review for a store agent.

    Args:
        username: Creator's username
        agent_name: Name/slug of the agent
        review: Review details including score and optional comments
        user_id: ID of authenticated user creating the review

    Returns:
        The created review
    """
    try:
        username = urllib.parse.unquote(username).lower()
        agent_name = urllib.parse.unquote(agent_name)
        # Create the review
        created_review = await backend.server.v2.store.db.create_store_review(
            user_id=user_id,
            store_listing_version_id=review.store_listing_version_id,
            score=review.score,
            comments=review.comments,
        )

        return created_review
    except Exception:
        logger.exception("Exception occurred whilst creating store review")
        return fastapi.responses.JSONResponse(
            status_code=500,
            content={"detail": "An error occurred while creating the store review"},
        )


##############################################
############# Creator Endpoints #############
##############################################


@router.get(
    "/creators",
    tags=["store", "public"],
    response_model=backend.server.v2.store.model.CreatorsResponse,
)
async def get_creators(
    featured: bool = False,
    search_query: str | None = None,
    sorted_by: str | None = None,
    page: int = 1,
    page_size: int = 20,
):
    """
    This is needed for:
    - Home Page Featured Creators
    - Search Results Page

    ---

    To support this functionality we need:
    - featured: bool - to limit the list to just featured agents
    - search_query: str - vector search based on the creators profile description.
    - sorted_by: [agent_rating, agent_runs] -
    """
    if page < 1:
        raise fastapi.HTTPException(
            status_code=422, detail="Page must be greater than 0"
        )

    if page_size < 1:
        raise fastapi.HTTPException(
            status_code=422, detail="Page size must be greater than 0"
        )

    try:
        creators = await backend.server.v2.store.db.get_store_creators(
            featured=featured,
            search_query=search_query,
            sorted_by=sorted_by,
            page=page,
            page_size=page_size,
        )
        return creators
    except Exception:
        logger.exception("Exception occurred whilst getting store creators")
        return fastapi.responses.JSONResponse(
            status_code=500,
            content={"detail": "An error occurred while retrieving the store creators"},
        )


@router.get(
    "/creator/{username}",
    tags=["store", "public"],
    response_model=backend.server.v2.store.model.CreatorDetails,
)
async def get_creator(
    username: str,
):
    """
    Get the details of a creator
    - Creator Details Page
    """
    try:
        username = urllib.parse.unquote(username).lower()
        creator = await backend.server.v2.store.db.get_store_creator_details(
            username=username.lower()
        )
        return creator
    except Exception:
        logger.exception("Exception occurred whilst getting creator details")
        return fastapi.responses.JSONResponse(
            status_code=500,
            content={
                "detail": "An error occurred while retrieving the creator details"
            },
        )


############################################
############# Store Submissions ###############
############################################
@router.get(
    "/myagents",
    tags=["store", "private"],
    dependencies=[fastapi.Depends(autogpt_libs.auth.middleware.auth_middleware)],
    response_model=backend.server.v2.store.model.MyAgentsResponse,
)
async def get_my_agents(
    user_id: typing.Annotated[
        str, fastapi.Depends(autogpt_libs.auth.depends.get_user_id)
    ]
):
    try:
        agents = await backend.server.v2.store.db.get_my_agents(user_id)
        return agents
    except Exception:
        logger.exception("Exception occurred whilst getting my agents")
        return fastapi.responses.JSONResponse(
            status_code=500,
            content={"detail": "An error occurred while retrieving the my agents"},
        )


@router.delete(
    "/submissions/{submission_id}",
    tags=["store", "private"],
    dependencies=[fastapi.Depends(autogpt_libs.auth.middleware.auth_middleware)],
    response_model=bool,
)
async def delete_submission(
    user_id: typing.Annotated[
        str, fastapi.Depends(autogpt_libs.auth.depends.get_user_id)
    ],
    submission_id: str,
):
    """
    Delete a store listing submission.

    Args:
        user_id (str): ID of the authenticated user
        submission_id (str): ID of the submission to be deleted

    Returns:
        bool: True if the submission was successfully deleted, False otherwise
    """
    try:
        result = await backend.server.v2.store.db.delete_store_submission(
            user_id=user_id,
            submission_id=submission_id,
        )
        return result
    except Exception:
        logger.exception("Exception occurred whilst deleting store submission")
        return fastapi.responses.JSONResponse(
            status_code=500,
            content={"detail": "An error occurred while deleting the store submission"},
        )


@router.get(
    "/submissions",
    tags=["store", "private"],
    dependencies=[fastapi.Depends(autogpt_libs.auth.middleware.auth_middleware)],
    response_model=backend.server.v2.store.model.StoreSubmissionsResponse,
)
async def get_submissions(
    user_id: typing.Annotated[
        str, fastapi.Depends(autogpt_libs.auth.depends.get_user_id)
    ],
    page: int = 1,
    page_size: int = 20,
):
    """
    Get a paginated list of store submissions for the authenticated user.

    Args:
        user_id (str): ID of the authenticated user
        page (int, optional): Page number for pagination. Defaults to 1.
        page_size (int, optional): Number of submissions per page. Defaults to 20.

    Returns:
        StoreListingsResponse: Paginated list of store submissions

    Raises:
        HTTPException: If page or page_size are less than 1
    """
    if page < 1:
        raise fastapi.HTTPException(
            status_code=422, detail="Page must be greater than 0"
        )

    if page_size < 1:
        raise fastapi.HTTPException(
            status_code=422, detail="Page size must be greater than 0"
        )
    try:
        listings = await backend.server.v2.store.db.get_store_submissions(
            user_id=user_id,
            page=page,
            page_size=page_size,
        )
        return listings
    except Exception:
        logger.exception("Exception occurred whilst getting store submissions")
        return fastapi.responses.JSONResponse(
            status_code=500,
            content={
                "detail": "An error occurred while retrieving the store submissions"
            },
        )


@router.post(
    "/submissions",
    tags=["store", "private"],
    dependencies=[fastapi.Depends(autogpt_libs.auth.middleware.auth_middleware)],
    response_model=backend.server.v2.store.model.StoreSubmission,
)
async def create_submission(
    submission_request: backend.server.v2.store.model.StoreSubmissionRequest,
    user_id: typing.Annotated[
        str, fastapi.Depends(autogpt_libs.auth.depends.get_user_id)
    ],
):
    """
    Create a new store listing submission.

    Args:
        submission_request (StoreSubmissionRequest): The submission details
        user_id (str): ID of the authenticated user submitting the listing

    Returns:
        StoreSubmission: The created store submission

    Raises:
        HTTPException: If there is an error creating the submission
    """
    try:
        submission = await backend.server.v2.store.db.create_store_submission(
            user_id=user_id,
            agent_id=submission_request.agent_id,
            agent_version=submission_request.agent_version,
            slug=submission_request.slug,
            name=submission_request.name,
            video_url=submission_request.video_url,
            image_urls=submission_request.image_urls,
            description=submission_request.description,
            sub_heading=submission_request.sub_heading,
            categories=submission_request.categories,
        )
        return submission
    except Exception:
        logger.exception("Exception occurred whilst creating store submission")
        return fastapi.responses.JSONResponse(
            status_code=500,
            content={"detail": "An error occurred while creating the store submission"},
        )


@router.post(
    "/submissions/media",
    tags=["store", "private"],
    dependencies=[fastapi.Depends(autogpt_libs.auth.middleware.auth_middleware)],
)
async def upload_submission_media(
    file: fastapi.UploadFile,
    user_id: typing.Annotated[
        str, fastapi.Depends(autogpt_libs.auth.depends.get_user_id)
    ],
):
    """
    Upload media (images/videos) for a store listing submission.

    Args:
        file (UploadFile): The media file to upload
        user_id (str): ID of the authenticated user uploading the media

    Returns:
        str: URL of the uploaded media file

    Raises:
        HTTPException: If there is an error uploading the media
    """
    try:
        media_url = await backend.server.v2.store.media.upload_media(
            user_id=user_id, file=file
        )
        return media_url
    except Exception:
        logger.exception("Exception occurred whilst uploading submission media")
        return fastapi.responses.JSONResponse(
            status_code=500,
            content={"detail": "An error occurred while uploading the media file"},
        )


@router.post(
    "/submissions/generate_image",
    tags=["store", "private"],
    dependencies=[fastapi.Depends(autogpt_libs.auth.middleware.auth_middleware)],
)
async def generate_image(
    agent_id: str,
    user_id: typing.Annotated[
        str, fastapi.Depends(autogpt_libs.auth.depends.get_user_id)
    ],
) -> fastapi.responses.Response:
    """
    Generate an image for a store listing submission.

    Args:
        agent_id (str): ID of the agent to generate an image for
        user_id (str): ID of the authenticated user

    Returns:
        JSONResponse: JSON containing the URL of the generated image
    """
    try:
        agent = await backend.data.graph.get_graph(agent_id, user_id=user_id)

        if not agent:
            raise fastapi.HTTPException(
                status_code=404, detail=f"Agent with ID {agent_id} not found"
            )
        # Use .jpeg here since we are generating JPEG images
        filename = f"agent_{agent_id}.jpeg"

        existing_url = await backend.server.v2.store.media.check_media_exists(
            user_id, filename
        )
        if existing_url:
            logger.info(f"Using existing image for agent {agent_id}")
            return fastapi.responses.JSONResponse(content={"image_url": existing_url})
        # Generate agent image as JPEG
        image = await backend.server.v2.store.image_gen.generate_agent_image(
            agent=agent
        )

        # Create UploadFile with the correct filename and content_type
        image_file = fastapi.UploadFile(
            file=image,
            filename=filename,
        )

        image_url = await backend.server.v2.store.media.upload_media(
            user_id=user_id, file=image_file, use_file_name=True
        )

        return fastapi.responses.JSONResponse(content={"image_url": image_url})
    except Exception:
        logger.exception("Exception occurred whilst generating submission image")
        return fastapi.responses.JSONResponse(
            status_code=500,
            content={"detail": "An error occurred while generating the image"},
        )


@router.get(
    "/download/agents/{store_listing_version_id}",
    tags=["store", "public"],
)
async def download_agent_file(
    store_listing_version_id: str = fastapi.Path(
        ..., description="The ID of the agent to download"
    ),
    version: typing.Optional[int] = fastapi.Query(
        None, description="Specific version of the agent"
    ),
) -> fastapi.responses.FileResponse:
    """
    Download the agent file by streaming its content.

    Args:
        agent_id (str): The ID of the agent to download.
        version (Optional[int]): Specific version of the agent to download.

    Returns:
        StreamingResponse: A streaming response containing the agent's graph data.

    Raises:
        HTTPException: If the agent is not found or an unexpected error occurs.
    """

    graph_data = await backend.server.v2.store.db.get_agent(
        store_listing_version_id=store_listing_version_id, version_id=version
    )

    graph_data.clean_graph()
    graph_date_dict = jsonable_encoder(graph_data)

    def remove_credentials(obj):
        if obj and isinstance(obj, dict):
            if "credentials" in obj:
                del obj["credentials"]
            if "creds" in obj:
                del obj["creds"]

            for value in obj.values():
                remove_credentials(value)
        elif isinstance(obj, list):
            for item in obj:
                remove_credentials(item)
        return obj

    graph_date_dict = remove_credentials(graph_date_dict)

    file_name = f"agent_{store_listing_version_id}_v{version or 'latest'}.json"

    # Sending graph as a stream (similar to marketplace v1)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as tmp_file:
        tmp_file.write(json.dumps(graph_date_dict))
        tmp_file.flush()

        return fastapi.responses.FileResponse(
            tmp_file.name, filename=file_name, media_type="application/json"
        )


@router.post(
    "/submissions/review/{store_listing_version_id}",
    tags=["store", "private"],
)
async def review_submission(
    request: backend.server.v2.store.model.ReviewSubmissionRequest,
    user: typing.Annotated[
        autogpt_libs.auth.models.User,
        fastapi.Depends(autogpt_libs.auth.depends.requires_admin_user),
    ],
):
    # Proceed with the review submission logic
    try:
        submission = await backend.server.v2.store.db.review_store_submission(
            store_listing_version_id=request.store_listing_version_id,
            is_approved=request.is_approved,
            comments=request.comments,
            reviewer_id=user.user_id,
        )
        return submission
    except Exception as e:
        logger.error(f"Could not create store submission review: {e}")
        raise fastapi.HTTPException(
            status_code=500,
            detail="An error occurred while creating the store submission review",
        )
