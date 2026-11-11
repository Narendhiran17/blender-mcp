"""Unit tests for bridge authentication and token validation."""

from blender_addon.bridge.auth import (
    initialize_token,
    validate_token,
)


def test_token_initialization_and_validation():
    token = initialize_token(explicit_token="test_secret_token_12345")
    assert token == "test_secret_token_12345"

    assert validate_token("test_secret_token_12345") is True
    assert validate_token("wrong_token") is False
    assert validate_token("") is False
    assert validate_token(None) is False
