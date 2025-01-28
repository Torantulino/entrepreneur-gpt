import logging
import random
from datetime import datetime
from typing import Optional

import prisma.enums
import prisma.errors
import prisma.models
import prisma.types

import backend.data.graph
import backend.server.v2.store.exceptions
import backend.server.v2.store.model
from backend.data.graph import GraphModel

logger = logging.getLogger(__name__)


async def get_store_agents(
    featured: bool = False,
    creator: str | None = None,
    sorted_by: str | None = None,
    search_query: str | None = None,
    category: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> backend.server.v2.store.model.StoreAgentsResponse:
    logger.debug(
        f"Getting store agents. featured={featured}, creator={creator}, sorted_by={sorted_by}, search={search_query}, category={category}, page={page}"
    )
    sanitized_query = None
    # Sanitize and validate search query by escaping special characters
    if search_query is not None:
        sanitized_query = search_query.strip()
        if not sanitized_query or len(sanitized_query) > 100:  # Reasonable length limit
            raise backend.server.v2.store.exceptions.DatabaseError(
                f"Invalid search query: len({len(sanitized_query)}) query: {search_query}"
            )

        # Escape special SQL characters
        sanitized_query = (
            sanitized_query.replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
            .replace("[", "\\[")
            .replace("]", "\\]")
            .replace("'", "\\'")
            .replace('"', '\\"')
            .replace(";", "\\;")
            .replace("--", "\\--")
            .replace("/*", "\\/*")
            .replace("*/", "\\*/")
        )

    where_clause = {}
    if featured:
        where_clause["featured"] = featured
    if creator:
        where_clause["creator_username"] = creator
    if category:
        where_clause["categories"] = {"has": category}

    if sanitized_query:
        where_clause["OR"] = [
            {"agent_name": {"contains": sanitized_query, "mode": "insensitive"}},
            {"description": {"contains": sanitized_query, "mode": "insensitive"}},
        ]

    order_by = []
    if sorted_by == "rating":
        order_by.append({"rating": "desc"})
    elif sorted_by == "runs":
        order_by.append({"runs": "desc"})
    elif sorted_by == "name":
        order_by.append({"agent_name": "asc"})

    try:
        agents = await prisma.models.StoreAgent.prisma().find_many(
            where=prisma.types.StoreAgentWhereInput(**where_clause),
            order=order_by,
            skip=(page - 1) * page_size,
            take=page_size,
        )

        total = await prisma.models.StoreAgent.prisma().count(
            where=prisma.types.StoreAgentWhereInput(**where_clause)
        )
        total_pages = (total + page_size - 1) // page_size

        store_agents = [
            backend.server.v2.store.model.StoreAgent(
                slug=agent.slug,
                agent_name=agent.agent_name,
                agent_image=agent.agent_image[0] if agent.agent_image else "",
                creator=agent.creator_username,
                creator_avatar=agent.creator_avatar,
                sub_heading=agent.sub_heading,
                description=agent.description,
                runs=agent.runs,
                rating=agent.rating,
            )
            for agent in agents
        ]

        logger.debug(f"Found {len(store_agents)} agents")
        return backend.server.v2.store.model.StoreAgentsResponse(
            agents=store_agents,
            pagination=backend.server.v2.store.model.Pagination(
                current_page=page,
                total_items=total,
                total_pages=total_pages,
                page_size=page_size,
            ),
        )
    except Exception as e:
        logger.error(f"Error getting store agents: {str(e)}")
        raise backend.server.v2.store.exceptions.DatabaseError(
            "Failed to fetch store agents"
        ) from e


async def get_store_agent_details(
    username: str, agent_name: str
) -> backend.server.v2.store.model.StoreAgentDetails:
    logger.debug(f"Getting store agent details for {username}/{agent_name}")

    try:
        agent = await prisma.models.StoreAgent.prisma().find_first(
            where={"creator_username": username, "slug": agent_name}
        )

        if not agent:
            logger.warning(f"Agent not found: {username}/{agent_name}")
            raise backend.server.v2.store.exceptions.AgentNotFoundError(
                f"Agent {username}/{agent_name} not found"
            )

        logger.debug(f"Found agent details for {username}/{agent_name}")
        return backend.server.v2.store.model.StoreAgentDetails(
            store_listing_version_id=agent.storeListingVersionId,
            slug=agent.slug,
            agent_name=agent.agent_name,
            agent_video=agent.agent_video or "",
            agent_image=agent.agent_image,
            creator=agent.creator_username,
            creator_avatar=agent.creator_avatar,
            sub_heading=agent.sub_heading,
            description=agent.description,
            categories=agent.categories,
            runs=agent.runs,
            rating=agent.rating,
            versions=agent.versions,
            last_updated=agent.updated_at,
        )
    except backend.server.v2.store.exceptions.AgentNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting store agent details: {str(e)}")
        raise backend.server.v2.store.exceptions.DatabaseError(
            "Failed to fetch agent details"
        ) from e


async def get_store_creators(
    featured: bool = False,
    search_query: str | None = None,
    sorted_by: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> backend.server.v2.store.model.CreatorsResponse:
    logger.debug(
        f"Getting store creators. featured={featured}, search={search_query}, sorted_by={sorted_by}, page={page}"
    )

    # Build where clause with sanitized inputs
    where = {}

    if featured:
        where["is_featured"] = featured

    # Add search filter if provided, using parameterized queries
    if search_query:
        # Sanitize and validate search query by escaping special characters
        sanitized_query = search_query.strip()
        if not sanitized_query or len(sanitized_query) > 100:  # Reasonable length limit
            raise backend.server.v2.store.exceptions.DatabaseError(
                "Invalid search query"
            )

        # Escape special SQL characters
        sanitized_query = (
            sanitized_query.replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
            .replace("[", "\\[")
            .replace("]", "\\]")
            .replace("'", "\\'")
            .replace('"', '\\"')
            .replace(";", "\\;")
            .replace("--", "\\--")
            .replace("/*", "\\/*")
            .replace("*/", "\\*/")
        )

        where["OR"] = [
            {"username": {"contains": sanitized_query, "mode": "insensitive"}},
            {"name": {"contains": sanitized_query, "mode": "insensitive"}},
            {"description": {"contains": sanitized_query, "mode": "insensitive"}},
        ]

    try:
        # Validate pagination parameters
        if not isinstance(page, int) or page < 1:
            raise backend.server.v2.store.exceptions.DatabaseError(
                "Invalid page number"
            )
        if not isinstance(page_size, int) or page_size < 1 or page_size > 100:
            raise backend.server.v2.store.exceptions.DatabaseError("Invalid page size")

        # Get total count for pagination using sanitized where clause
        total = await prisma.models.Creator.prisma().count(
            where=prisma.types.CreatorWhereInput(**where)
        )
        total_pages = (total + page_size - 1) // page_size

        # Add pagination with validated parameters
        skip = (page - 1) * page_size
        take = page_size

        # Add sorting with validated sort parameter
        order = []
        valid_sort_fields = {"agent_rating", "agent_runs", "num_agents"}
        if sorted_by in valid_sort_fields:
            order.append({sorted_by: "desc"})
        else:
            order.append({"username": "asc"})

        # Execute query with sanitized parameters
        creators = await prisma.models.Creator.prisma().find_many(
            where=prisma.types.CreatorWhereInput(**where),
            skip=skip,
            take=take,
            order=order,
        )

        # Convert to response model
        creator_models = [
            backend.server.v2.store.model.Creator(
                username=creator.username,
                name=creator.name,
                description=creator.description,
                avatar_url=creator.avatar_url,
                num_agents=creator.num_agents,
                agent_rating=creator.agent_rating,
                agent_runs=creator.agent_runs,
                is_featured=creator.is_featured,
            )
            for creator in creators
        ]

        logger.debug(f"Found {len(creator_models)} creators")
        return backend.server.v2.store.model.CreatorsResponse(
            creators=creator_models,
            pagination=backend.server.v2.store.model.Pagination(
                current_page=page,
                total_items=total,
                total_pages=total_pages,
                page_size=page_size,
            ),
        )
    except Exception as e:
        logger.error(f"Error getting store creators: {str(e)}")
        raise backend.server.v2.store.exceptions.DatabaseError(
            "Failed to fetch store creators"
        ) from e


async def get_store_creator_details(
    username: str,
) -> backend.server.v2.store.model.CreatorDetails:
    logger.debug(f"Getting store creator details for {username}")

    try:
        # Query creator details from database
        creator = await prisma.models.Creator.prisma().find_unique(
            where={"username": username}
        )

        if not creator:
            logger.warning(f"Creator not found: {username}")
            raise backend.server.v2.store.exceptions.CreatorNotFoundError(
                f"Creator {username} not found"
            )

        logger.debug(f"Found creator details for {username}")
        return backend.server.v2.store.model.CreatorDetails(
            name=creator.name,
            username=creator.username,
            description=creator.description,
            links=creator.links,
            avatar_url=creator.avatar_url,
            agent_rating=creator.agent_rating,
            agent_runs=creator.agent_runs,
            top_categories=creator.top_categories,
        )
    except backend.server.v2.store.exceptions.CreatorNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting store creator details: {str(e)}")
        raise backend.server.v2.store.exceptions.DatabaseError(
            "Failed to fetch creator details"
        ) from e


async def get_store_submissions(
    user_id: str, page: int = 1, page_size: int = 20
) -> backend.server.v2.store.model.StoreSubmissionsResponse:
    logger.debug(f"Getting store submissions for user {user_id}, page={page}")

    try:
        # Calculate pagination values
        skip = (page - 1) * page_size

        where = prisma.types.StoreSubmissionWhereInput(user_id=user_id)
        # Query submissions from database
        submissions = await prisma.models.StoreSubmission.prisma().find_many(
            where=where, skip=skip, take=page_size, order=[{"date_submitted": "desc"}]
        )

        # Get total count for pagination
        total = await prisma.models.StoreSubmission.prisma().count(where=where)

        total_pages = (total + page_size - 1) // page_size

        # Convert to response models
        submission_models = [
            backend.server.v2.store.model.StoreSubmission(
                agent_id=sub.agent_id,
                agent_version=sub.agent_version,
                name=sub.name,
                sub_heading=sub.sub_heading,
                slug=sub.slug,
                description=sub.description,
                image_urls=sub.image_urls or [],
                date_submitted=sub.date_submitted or datetime.now(),
                status=sub.status,
                runs=sub.runs or 0,
                rating=sub.rating or 0.0,
            )
            for sub in submissions
        ]

        logger.debug(f"Found {len(submission_models)} submissions")
        return backend.server.v2.store.model.StoreSubmissionsResponse(
            submissions=submission_models,
            pagination=backend.server.v2.store.model.Pagination(
                current_page=page,
                total_items=total,
                total_pages=total_pages,
                page_size=page_size,
            ),
        )

    except Exception as e:
        logger.error(f"Error fetching store submissions: {str(e)}")
        # Return empty response rather than exposing internal errors
        return backend.server.v2.store.model.StoreSubmissionsResponse(
            submissions=[],
            pagination=backend.server.v2.store.model.Pagination(
                current_page=page,
                total_items=0,
                total_pages=0,
                page_size=page_size,
            ),
        )


async def delete_store_submission(
    user_id: str,
    submission_id: str,
) -> bool:
    """
    Delete a store listing submission.

    Args:
        user_id: ID of the authenticated user
        submission_id: ID of the submission to be deleted

    Returns:
        bool: True if the submission was successfully deleted, False otherwise
    """
    logger.debug(f"Deleting store submission {submission_id} for user {user_id}")

    try:
        # Verify the submission belongs to this user
        submission = await prisma.models.StoreListing.prisma().find_first(
            where={"agentId": submission_id, "owningUserId": user_id}
        )

        if not submission:
            logger.warning(f"Submission not found for user {user_id}: {submission_id}")
            raise backend.server.v2.store.exceptions.SubmissionNotFoundError(
                f"Submission not found for this user. User ID: {user_id}, Submission ID: {submission_id}"
            )

        # Delete the submission
        await prisma.models.StoreListing.prisma().delete(
            where=prisma.types.StoreListingWhereUniqueInput(id=submission.id)
        )

        logger.debug(
            f"Successfully deleted submission {submission_id} for user {user_id}"
        )
        return True

    except Exception as e:
        logger.error(f"Error deleting store submission: {str(e)}")
        return False


async def create_store_submission(
    user_id: str,
    agent_id: str,
    agent_version: int,
    slug: str,
    name: str,
    video_url: str | None = None,
    image_urls: list[str] = [],
    description: str = "",
    sub_heading: str = "",
    categories: list[str] = [],
) -> backend.server.v2.store.model.StoreSubmission:
    """
    Create a new store listing submission.

    Args:
        user_id: ID of the authenticated user submitting the listing
        agent_id: ID of the agent being submitted
        agent_version: Version of the agent being submitted
        slug: URL slug for the listing
        name: Name of the agent
        video_url: Optional URL to video demo
        image_urls: List of image URLs for the listing
        description: Description of the agent
        categories: List of categories for the agent

    Returns:
        StoreSubmission: The created store submission
    """
    logger.debug(
        f"Creating store submission for user {user_id}, agent {agent_id} v{agent_version}"
    )

    try:
        # Sanitize slug to only allow letters and hyphens
        slug = "".join(
            c if c.isalpha() or c == "-" or c.isnumeric() else "" for c in slug
        ).lower()

        # First verify the agent belongs to this user
        agent = await prisma.models.AgentGraph.prisma().find_first(
            where=prisma.types.AgentGraphWhereInput(
                id=agent_id, version=agent_version, userId=user_id
            )
        )

        if not agent:
            logger.warning(
                f"Agent not found for user {user_id}: {agent_id} v{agent_version}"
            )
            raise backend.server.v2.store.exceptions.AgentNotFoundError(
                f"Agent not found for this user. User ID: {user_id}, Agent ID: {agent_id}, Version: {agent_version}"
            )

        listing = await prisma.models.StoreListing.prisma().find_first(
            where=prisma.types.StoreListingWhereInput(
                agentId=agent_id, owningUserId=user_id
            )
        )
        if listing is not None:
            logger.warning(f"Listing already exists for agent {agent_id}")
            raise backend.server.v2.store.exceptions.ListingExistsError(
                "Listing already exists for this agent"
            )

        # Create the store listing
        listing = await prisma.models.StoreListing.prisma().create(
            data={
                "agentId": agent_id,
                "agentVersion": agent_version,
                "owningUserId": user_id,
                "createdAt": datetime.now(),
                "StoreListingVersions": {
                    "create": {
                        "agentId": agent_id,
                        "agentVersion": agent_version,
                        "slug": slug,
                        "name": name,
                        "videoUrl": video_url,
                        "imageUrls": image_urls,
                        "description": description,
                        "categories": categories,
                        "subHeading": sub_heading,
                    }
                },
            }
        )

        logger.debug(f"Created store listing for agent {agent_id}")
        # Return submission details
        return backend.server.v2.store.model.StoreSubmission(
            agent_id=agent_id,
            agent_version=agent_version,
            name=name,
            slug=slug,
            sub_heading=sub_heading,
            description=description,
            image_urls=image_urls,
            date_submitted=listing.createdAt,
            status=prisma.enums.SubmissionStatus.PENDING,
            runs=0,
            rating=0.0,
        )

    except (
        backend.server.v2.store.exceptions.AgentNotFoundError,
        backend.server.v2.store.exceptions.ListingExistsError,
    ):
        raise
    except prisma.errors.PrismaError as e:
        logger.error(f"Database error creating store submission: {str(e)}")
        raise backend.server.v2.store.exceptions.DatabaseError(
            "Failed to create store submission"
        ) from e


async def create_store_review(
    user_id: str,
    store_listing_version_id: str,
    score: int,
    comments: str | None = None,
) -> backend.server.v2.store.model.StoreReview:
    try:
        review = await prisma.models.StoreListingReview.prisma().upsert(
            where={
                "storeListingVersionId_reviewByUserId": {
                    "storeListingVersionId": store_listing_version_id,
                    "reviewByUserId": user_id,
                }
            },
            data={
                "create": {
                    "reviewByUserId": user_id,
                    "storeListingVersionId": store_listing_version_id,
                    "score": score,
                    "comments": comments,
                },
                "update": {
                    "score": score,
                    "comments": comments,
                },
            },
        )

        return backend.server.v2.store.model.StoreReview(
            score=review.score,
            comments=review.comments,
        )

    except prisma.errors.PrismaError as e:
        logger.error(f"Database error creating store review: {str(e)}")
        raise backend.server.v2.store.exceptions.DatabaseError(
            "Failed to create store review"
        ) from e


async def get_user_profile(
    user_id: str,
) -> backend.server.v2.store.model.ProfileDetails:
    logger.debug(f"Getting user profile for {user_id}")

    try:
        profile = await prisma.models.Profile.prisma().find_first(
            where={"userId": user_id}  # type: ignore
        )

        if not profile:
            logger.warning(f"Profile not found for user {user_id}")
            new_profile = await prisma.models.Profile.prisma().create(
                data=prisma.types.ProfileCreateInput(
                    userId=user_id,
                    name="No Profile Data",
                    username=f"{random.choice(['happy', 'clever', 'swift', 'bright', 'wise'])}-{random.choice(['fox', 'wolf', 'bear', 'eagle', 'owl'])}_{random.randint(1000,9999)}".lower(),
                    description="No Profile Data",
                    links=[],
                    avatarUrl="",
                )
            )
            return backend.server.v2.store.model.ProfileDetails(
                name=new_profile.name,
                username=new_profile.username,
                description=new_profile.description,
                links=new_profile.links,
                avatar_url=new_profile.avatarUrl,
            )

        return backend.server.v2.store.model.ProfileDetails(
            name=profile.name,
            username=profile.username,
            description=profile.description,
            links=profile.links,
            avatar_url=profile.avatarUrl,
        )
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return backend.server.v2.store.model.ProfileDetails(
            name="No Profile Data",
            username="No Profile Data",
            description="No Profile Data",
            links=[],
            avatar_url="",
        )


async def update_or_create_profile(
    user_id: str, profile: backend.server.v2.store.model.Profile
) -> backend.server.v2.store.model.CreatorDetails:
    """
    Update the store profile for a user. Creates a new profile if one doesn't exist.
    Only allows updating if the user_id matches the owning user.
    If a field is None, it will not overwrite the existing value in the case of an update.

    Args:
        user_id: ID of the authenticated user
        profile: Updated profile details

    Returns:
        CreatorDetails: The updated profile

    Raises:
        HTTPException: If user is not authorized to update this profile
        DatabaseError: If profile cannot be updated due to database issues
    """
    logger.info(f"Updating profile for user {user_id} data: {profile}")

    try:
        # Sanitize username to only allow letters and hyphens
        username = "".join(
            c if c.isalpha() or c == "-" or c.isnumeric() else ""
            for c in profile.username
        ).lower()

        existing_profile = await prisma.models.Profile.prisma().find_first(
            where={"userId": user_id}
        )

        # If no profile exists, create a new one
        if not existing_profile:
            logger.debug(
                f"No existing profile found. Creating new profile for user {user_id}"
            )
            # Create new profile since one doesn't exist
            new_profile = await prisma.models.Profile.prisma().create(
                data={
                    "userId": user_id,
                    "name": profile.name,
                    "username": username,
                    "description": profile.description,
                    "links": profile.links or [],
                    "avatarUrl": profile.avatar_url,
                    "isFeatured": False,
                }
            )

            return backend.server.v2.store.model.CreatorDetails(
                name=new_profile.name,
                username=new_profile.username,
                description=new_profile.description,
                links=new_profile.links,
                avatar_url=new_profile.avatarUrl or "",
                agent_rating=0.0,
                agent_runs=0,
                top_categories=[],
            )
        else:
            logger.debug(f"Updating existing profile for user {user_id}")
            # Update only provided fields for the existing profile
            update_data = {}
            if profile.name is not None:
                update_data["name"] = profile.name
            if profile.username is not None:
                update_data["username"] = username
            if profile.description is not None:
                update_data["description"] = profile.description
            if profile.links is not None:
                update_data["links"] = profile.links
            if profile.avatar_url is not None:
                update_data["avatarUrl"] = profile.avatar_url

            # Update the existing profile
            updated_profile = await prisma.models.Profile.prisma().update(
                where={"id": existing_profile.id},
                data=prisma.types.ProfileUpdateInput(**update_data),
            )
            if updated_profile is None:
                logger.error(f"Failed to update profile for user {user_id}")
                raise backend.server.v2.store.exceptions.DatabaseError(
                    "Failed to update profile"
                )

            return backend.server.v2.store.model.CreatorDetails(
                name=updated_profile.name,
                username=updated_profile.username,
                description=updated_profile.description,
                links=updated_profile.links,
                avatar_url=updated_profile.avatarUrl or "",
                agent_rating=0.0,
                agent_runs=0,
                top_categories=[],
            )

    except prisma.errors.PrismaError as e:
        logger.error(f"Database error updating profile: {str(e)}")
        raise backend.server.v2.store.exceptions.DatabaseError(
            "Failed to update profile"
        ) from e


async def get_my_agents(
    user_id: str,
    page: int = 1,
    page_size: int = 20,
) -> backend.server.v2.store.model.MyAgentsResponse:
    logger.debug(f"Getting my agents for user {user_id}, page={page}")

    try:
        agents_with_max_version = await prisma.models.AgentGraph.prisma().find_many(
            where=prisma.types.AgentGraphWhereInput(
                userId=user_id, StoreListing={"none": {"isDeleted": False}}
            ),
            order=[{"version": "desc"}],
            distinct=["id"],
            skip=(page - 1) * page_size,
            take=page_size,
        )

        # store_listings = await prisma.models.StoreListing.prisma().find_many(
        #     where=prisma.types.StoreListingWhereInput(
        #         isDeleted=False,
        #     ),
        # )

        total = len(
            await prisma.models.AgentGraph.prisma().find_many(
                where=prisma.types.AgentGraphWhereInput(
                    userId=user_id, StoreListing={"none": {"isDeleted": False}}
                ),
                order=[{"version": "desc"}],
                distinct=["id"],
            )
        )

        total_pages = (total + page_size - 1) // page_size

        agents = agents_with_max_version

        my_agents = [
            backend.server.v2.store.model.MyAgent(
                agent_id=agent.id,
                agent_version=agent.version,
                agent_name=agent.name or "",
                last_edited=agent.updatedAt or agent.createdAt,
                description=agent.description or "",
            )
            for agent in agents
        ]

        return backend.server.v2.store.model.MyAgentsResponse(
            agents=my_agents,
            pagination=backend.server.v2.store.model.Pagination(
                current_page=page,
                total_items=total,
                total_pages=total_pages,
                page_size=page_size,
            ),
        )
    except Exception as e:
        logger.error(f"Error getting my agents: {str(e)}")
        raise backend.server.v2.store.exceptions.DatabaseError(
            "Failed to fetch my agents"
        ) from e


async def get_agent(
    store_listing_version_id: str, version_id: Optional[int]
) -> Optional[GraphModel]:
    """Get agent using the version ID and store listing version ID."""
    try:
        store_listing_version = (
            await prisma.models.StoreListingVersion.prisma().find_unique(
                where={"id": store_listing_version_id}, include={"Agent": True}
            )
        )

        if not store_listing_version or not store_listing_version.Agent:
            logger.error(f"Store listing version {store_listing_version_id} not found")
            return None

        agent = store_listing_version.Agent

        graph = await backend.data.graph.get_graph(
            agent.id, agent.version, template=True
        )

        if not graph:
            logger.error(f"Agent {agent.id} not found")
            return None

        graph.version = 1
        graph.is_template = False
        graph.is_active = True

        return graph

    except Exception as e:
        logger.error(f"Error getting agent: {str(e)}")
        raise backend.server.v2.store.exceptions.DatabaseError(
            "Failed to fetch agent"
        ) from e
