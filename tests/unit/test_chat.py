# Generated by CodiumAI
import time
from unittest.mock import patch

from autogpt.llm import create_chat_message, generate_context


def test_happy_path_role_content():
    """Test that the function returns a dictionary with the correct keys and values when valid strings are provided for role and content."""
    result = create_chat_message("system", "Hello, world!")
    assert result == {"role": "system", "content": "Hello, world!"}


def test_empty_role_content():
    """Test that the function returns a dictionary with the correct keys and values when empty strings are provided for role and content."""
    result = create_chat_message("", "")
    assert result == {"role": "", "content": ""}


def test_generate_context_empty_inputs(mocker):
    """Test the behavior of the generate_context function when all input parameters are empty."""
    # Mock the time.strftime function to return a fixed value
    mocker.patch("time.strftime", return_value="Sat Apr 15 00:00:00 2023")
    # Arrange
    prompt = ""
    relevant_memory = ""
    full_message_history = []
    model = "gpt-3.5-turbo-0301"

    # Act
    result = generate_context(prompt, relevant_memory, full_message_history, model)

    # Assert
    expected_result = (
        -1,
        47,
        3,
        [
            {"role": "system", "content": ""},
            {
                "role": "system",
                "content": f"The current time and date is {time.strftime('%c')}",
            },
            {
                "role": "system",
                "content": f"This reminds you of these events from your past:\n\n\n",
            },
        ],
    )
    assert result == expected_result


def test_generate_context_valid_inputs():
    """Test that the function successfully generates a current_context given valid inputs."""
    # Given
    prompt = "What is your favorite color?"
    relevant_memory = "You once painted your room blue."
    full_message_history = [
        create_chat_message("user", "Hi there!"),
        create_chat_message("assistant", "Hello! How can I assist you today?"),
        create_chat_message("user", "Can you tell me a joke?"),
        create_chat_message(
            "assistant",
            "Why did the tomato turn red? Because it saw the salad dressing!",
        ),
        create_chat_message("user", "Haha, that's funny."),
    ]
    model = "gpt-3.5-turbo-0301"

    # When
    result = generate_context(prompt, relevant_memory, full_message_history, model)

    # Then
    assert isinstance(result[0], int)
    assert isinstance(result[1], int)
    assert isinstance(result[2], int)
    assert isinstance(result[3], list)
    assert result[0] >= 0
    assert result[2] >= 0
    assert result[1] >= 0
    assert len(result[3]) >= 3  # current_context should have at least 3 messages
    assert result[1] <= 2048  # token limit for GPT-3.5-turbo-0301 is 2048 tokens
