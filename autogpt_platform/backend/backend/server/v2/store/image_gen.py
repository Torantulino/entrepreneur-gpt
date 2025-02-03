import io
import logging
from enum import Enum

import replicate
import replicate.exceptions
import requests
from prisma.models import AgentGraph
from replicate.helpers import FileOutput

from backend.data.graph import Graph
from backend.util.settings import Settings

logger = logging.getLogger(__name__)


class ImageSize(str, Enum):
    LANDSCAPE = "1024x768"


class ImageStyle(str, Enum):
    DIGITAL_ART = "digital art"


async def generate_agent_image(agent: Graph | AgentGraph) -> io.BytesIO:
    """
    Generate an image for an agent using Flux model via Replicate API.

    Args:
        agent (Graph): The agent to generate an image for

    Returns:
        io.BytesIO: The generated image as bytes
    """
    try:
        settings = Settings()

        if not settings.secrets.replicate_api_key:
            raise ValueError("Missing Replicate API key in settings")

        # Construct prompt from agent details
        prompt = f"Create a visually engaging app store thumbnail for the AI agent that highlights what it does in a clear and captivating way:\n- **Name**: {agent.name}\n- **Description**: {agent.description}\nFocus on showcasing its core functionality with an appealing design."

        # Set up Replicate client
        client = replicate.Client(api_token=settings.secrets.replicate_api_key)

        # Model parameters
        input_data = {
            "prompt": prompt,
            "width": 1024,
            "height": 768,
            "aspect_ratio": "4:3",
            "output_format": "jpg",
            "output_quality": 90,
            "num_inference_steps": 30,
            "guidance": 3.5,
            "negative_prompt": "blurry, low quality, distorted, deformed",
            "disable_safety_checker": True,
        }

        try:
            # Run model
            output = client.run("black-forest-labs/flux-1.1-pro", input=input_data)

            # Depending on the model output, extract the image URL or bytes
            # If the output is a list of FileOutput or URLs
            if isinstance(output, list) and output:
                if isinstance(output[0], FileOutput):
                    image_bytes = output[0].read()
                else:
                    # If it's a URL string, fetch the image bytes
                    result_url = output[0]
                    response = requests.get(result_url)
                    response.raise_for_status()
                    image_bytes = response.content
            elif isinstance(output, FileOutput):
                image_bytes = output.read()
            elif isinstance(output, str):
                # Output is a URL
                response = requests.get(output)
                response.raise_for_status()
                image_bytes = response.content
            else:
                raise RuntimeError("Unexpected output format from the model.")

            return io.BytesIO(image_bytes)

        except replicate.exceptions.ReplicateError as e:
            if e.status == 401:
                raise RuntimeError("Invalid Replicate API token") from e
            raise RuntimeError(f"Replicate API error: {str(e)}") from e

    except Exception as e:
        logger.exception("Failed to generate agent image")
        raise RuntimeError(f"Image generation failed: {str(e)}")
