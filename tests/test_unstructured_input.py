from pathlib import Path
from unittest.mock import MagicMock

import pytest

from mcp_config_converter.transformers import ConfigTransformer
from mcp_config_converter.types import EncodingFormat

TEST_DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def mock_llm_client():
    client = MagicMock()
    # Mock the generate method directly since ConfigTransformer calls it
    client.generate.return_value = '{"servers": {"mock": {}}}'
    client.provider = "mock-provider"
    client.model = "mock-model"
    return client


def test_convert_pseudo_structured_text(mock_llm_client) -> None:
    """Test converting a pseudo-structured text file."""
    input_file = TEST_DATA_DIR / "config_pseudo.txt"
    if not input_file.exists():
        pytest.skip("config_pseudo.txt not found")

    input_content = input_file.read_text(encoding="utf-8")

    transformer = ConfigTransformer(llm_client=mock_llm_client, encoding=EncodingFormat.NONE.value)

    # We patch build_conversion_prompt to verify what gets passed to it,
    # but also rely on the real method to verify the flow.
    # Actually, simpler to check if transform succeeds.

    result = transformer.transform(input_content, "claude")

    # Verify result is what our mock returned (cleaned)
    # The output is pretty printed now, so we parse it to verify structure
    import json

    parsed_result = json.loads(result)
    assert parsed_result == {"servers": {"mock": {}}}

    # Verify the LLM was called
    mock_llm_client.generate.assert_called_once()

    # specific check: ensure the prompt contained the input content
    call_args = mock_llm_client.generate.call_args
    # The prompt is the first positional argument
    prompt_arg = call_args.args[0]
    assert input_content in prompt_arg


def test_convert_prose_text(mock_llm_client) -> None:
    """Test converting a prose text file."""
    input_file = TEST_DATA_DIR / "config_prose.txt"
    if not input_file.exists():
        pytest.skip("config_prose.txt not found")

    input_content = input_file.read_text(encoding="utf-8")

    # Use TOON encoding to verify fallback behavior (it should fail to parse and use raw text)
    transformer = ConfigTransformer(llm_client=mock_llm_client, encoding=EncodingFormat.TOON.value)

    result = transformer.transform(input_content, "vscode")

    import json

    parsed_result = json.loads(result)
    assert parsed_result == {"servers": {"mock": {}}}
    mock_llm_client.generate.assert_called_once()

    # Verify raw text was used because parsing failed
    prompt_arg = mock_llm_client.generate.call_args.args[0]
    assert input_content in prompt_arg
