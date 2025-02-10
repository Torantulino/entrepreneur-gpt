import logging
import time
from enum import Enum
from typing import Any

import httpx

from backend.blocks.fal._auth import (
    TEST_CREDENTIALS,
    TEST_CREDENTIALS_INPUT,
    FalCredentials,
    FalCredentialsField,
    FalCredentialsInput,
)
from backend.data.block import Block, BlockCategory, BlockOutput, BlockSchema
from backend.data.model import SchemaField

logger = logging.getLogger(__name__)


class FalModel(str, Enum):
    KLING_PRO = "fal-ai/kling-video/v1.5/pro/image-to-video"
    # Add more models here in the future as they become available


class ImageToVideoBlock(Block):
    class Input(BlockSchema):
        prompt: str = SchemaField(
            description="Description of how the video should animate from the input image.",
            placeholder="A stylish woman walks down a Tokyo street filled with warm glowing neon and animated city signage.",
        )
        image_url: str = SchemaField(
            description="URL of the source image to animate.",
            placeholder="https://example.com/image.jpg",
        )
        model: FalModel = SchemaField(
            title="FAL Model",
            default=FalModel.KLING_PRO,
            description="The FAL model to use for video generation. Each model may have different capabilities and characteristics.",
        )
        credentials: FalCredentialsInput = FalCredentialsField()

    class Output(BlockSchema):
        video_url: str = SchemaField(description="The URL of the generated video.")
        error: str = SchemaField(
            description="Error message if video generation failed."
        )
        logs: list[str] = SchemaField(description="Generation progress logs.")

    def __init__(self):
        super().__init__(
            id="e7489f57-2fc8-49ca-9085-abe7e39fa901",
            description="Generate videos by animating a source image using FAL AI's image-to-video models.",
            categories={BlockCategory.AI},
            input_schema=self.Input,
            output_schema=self.Output,
            test_input={
                "prompt": "A stylish woman walks down a Tokyo street filled with warm glowing neon and animated city signage.",
                "image_url": "https://fal.media/files/example/image.jpg",
                "model": FalModel.KLING_PRO,
                "credentials": TEST_CREDENTIALS_INPUT,
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[("video_url", "https://fal.media/files/example/video.mp4")],
            test_mock={
                "generate_video": lambda *args, **kwargs: "https://fal.media/files/example/video.mp4"
            },
        )

    def _get_headers(self, api_key: str) -> dict[str, str]:
        """Get headers for FAL API requests."""
        return {
            "Authorization": f"Key {api_key}",
            "Content-Type": "application/json",
        }

    def _submit_request(
        self, url: str, headers: dict[str, str], data: dict[str, Any]
    ) -> dict[str, Any]:
        """Submit a request to the FAL API."""
        try:
            response = httpx.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"FAL API request failed: {str(e)}")
            raise RuntimeError(f"Failed to submit request: {str(e)}")

    def _poll_status(self, status_url: str, headers: dict[str, str]) -> dict[str, Any]:
        """Poll the status endpoint until completion or failure."""
        try:
            response = httpx.get(status_url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get status: {str(e)}")
            raise RuntimeError(f"Failed to get status: {str(e)}")

    def generate_video(self, input_data: Input, credentials: FalCredentials) -> str:
        """Generate video using the specified FAL model."""
        base_url = "https://queue.fal.run"
        api_key = credentials.api_key.get_secret_value()
        headers = self._get_headers(api_key)

        # Submit generation request
        submit_url = f"{base_url}/{input_data.model.value}"
        submit_data = {
            "prompt": input_data.prompt,
            "image_url": input_data.image_url,
        }

        seen_logs = set()

        try:
            # Submit request to queue
            submit_response = httpx.post(submit_url, headers=headers, json=submit_data)
            submit_response.raise_for_status()
            request_data = submit_response.json()

            # Get request_id and urls from initial response
            request_id = request_data.get("request_id")
            status_url = request_data.get("status_url")
            result_url = request_data.get("response_url")

            if not all([request_id, status_url, result_url]):
                raise ValueError("Missing required data in submission response")

            # Poll for status with exponential backoff
            max_attempts = 30
            attempt = 0
            base_wait_time = 5

            while attempt < max_attempts:
                status_response = httpx.get(f"{status_url}?logs=1", headers=headers)
                status_response.raise_for_status()
                status_data = status_response.json()

                # Process new logs
                logs = status_data.get("logs", [])
                if logs and isinstance(logs, list):
                    for log in logs:
                        if isinstance(log, dict):
                            # Create a unique key for this log entry
                            log_key = (
                                f"{log.get('timestamp', '')}-{log.get('message', '')}"
                            )
                            if log_key not in seen_logs:
                                seen_logs.add(log_key)
                                message = log.get("message", "")
                                if message:
                                    logger.debug(
                                        f"[FAL Generation] [{log.get('level', 'INFO')}] [{log.get('source', '')}] [{log.get('timestamp', '')}] {message}"
                                    )
                                    yield "logs", message

                status = status_data.get("status")
                if status == "COMPLETED":
                    # Get the final result
                    result_response = httpx.get(result_url, headers=headers)
                    result_response.raise_for_status()
                    result_data = result_response.json()

                    if "video" not in result_data or not isinstance(
                        result_data["video"], dict
                    ):
                        raise ValueError("Invalid response format - missing video data")

                    video_url = result_data["video"].get("url")
                    if not video_url:
                        raise ValueError("No video URL in response")

                    return video_url

                elif status == "FAILED":
                    error_msg = status_data.get("error", "No error details provided")
                    raise RuntimeError(f"Video generation failed: {error_msg}")
                elif status == "IN_QUEUE":
                    position = status_data.get("queue_position", "unknown")
                    logger.debug(
                        f"[FAL Generation] Status: In queue, position: {position}"
                    )
                    yield "logs", f"In queue, position: {position}"
                elif status == "IN_PROGRESS":
                    logger.debug(
                        "[FAL Generation] Status: Request is being processed..."
                    )
                    yield "logs", "Request is being processed..."
                else:
                    logger.info(f"[FAL Generation] Status: Unknown status: {status}")
                    yield "logs", f"Unknown status: {status}"

                wait_time = min(base_wait_time * (2**attempt), 60)  # Cap at 60 seconds
                time.sleep(wait_time)
                attempt += 1

            raise RuntimeError("Maximum polling attempts reached")

        except httpx.HTTPError as e:
            raise RuntimeError(f"API request failed: {str(e)}")

    def run(
        self, input_data: Input, *, credentials: FalCredentials, **kwargs
    ) -> BlockOutput:
        try:
            generator = self.generate_video(input_data, credentials)
            for output in generator:
                if isinstance(output, tuple):
                    yield output
                else:
                    # If generate_video returns a string directly, it's the video URL
                    yield "video_url", output
        except Exception as e:
            error_message = str(e)
            yield "error", error_message
