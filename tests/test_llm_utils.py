# Generated by CodiumAI
import pytest

from autogpt.llm_utils import chunked_tokens

"""
Code Analysis

Objective:
The objective of the 'chunked_tokens' function is to split a given text into smaller chunks of a specified length, encode each chunk using a specified encoding, and yield the resulting chunks as an iterator.

Inputs:
- 'text': a string representing the text to be chunked and encoded
- 'encoding_name': a string representing the name of the encoding to be used for encoding the text
- 'chunk_length': an integer representing the desired length of each chunk

Flow:
1. Get the encoding corresponding to the specified encoding name using the 'get_encoding' function from the 'tiktoken' module.
2. Encode the input text using the obtained encoding to get a list of tokens.
3. Use the 'batched' function to split the list of tokens into smaller batches of length 'chunk_length'.
4. Yield each batch of tokens as an iterator using the 'yield from' statement.

Outputs:
- An iterator yielding batches of encoded tokens, where each batch has a length of 'chunk_length' except for the last batch, which may have a shorter length.

Additional aspects:
- The 'batched' function is used as a helper function to split the list of tokens into smaller batches.
- The 'batched' function raises a 'ValueError' if the specified batch length is less than 1.
- The 'batched' function uses the 'islice' function from the 'itertools' module to slice the input iterable into batches.
"""


class TestChunkedTokens:
    # Tests that text can be chunked.
    def test_chunked_tokens_equal_chunks(self):
        text = "Auto-GPT is an experimental open-source application showcasing the capabilities of the GPT-4 language model"
        expected_output = [
            (
                13556,
                12279,
                2898,
                374,
                459,
                22772,
                1825,
                31874,
                3851,
                67908,
                279,
                17357,
                315,
                279,
                480,
                2898,
                12,
                19,
                4221,
                1646,
            )
        ]
        output = list(chunked_tokens(text, "cl100k_base", 8191))
        assert output == expected_output
