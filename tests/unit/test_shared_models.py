"""Unit tests for shared models and schemas."""

import pytest
from pydantic import ValidationError
from shared.constants import PROTOCOL_VERSION, STATUS_COMPLETED, STATUS_FAILED
from shared.models import CreatePrimitiveArgs, RequestEnvelope, ResponseEnvelope


def test_request_envelope_defaults():
    req = RequestEnvelope(
        request_id="req_123",
        operation="object.create_primitive",
        arguments={"primitive_type": "CUBE"},
    )
    assert req.protocol_version == PROTOCOL_VERSION
    assert req.request_id == "req_123"
    assert req.operation == "object.create_primitive"
    assert req.arguments["primitive_type"] == "CUBE"
    assert req.timeout_seconds == 30.0


def test_response_envelope_success_and_failure():
    res_ok = ResponseEnvelope.success(
        request_id="req_123",
        result={"name": "Cube", "type": "MESH"},
    )
    assert res_ok.status == STATUS_COMPLETED
    assert res_ok.result == {"name": "Cube", "type": "MESH"}
    assert res_ok.error is None

    res_fail = ResponseEnvelope.failure(
        request_id="req_123",
        code="OBJECT_NOT_FOUND",
        message="Object 'Cube' does not exist",
    )
    assert res_fail.status == STATUS_FAILED
    assert res_fail.result is None
    assert res_fail.error is not None
    assert res_fail.error.code == "OBJECT_NOT_FOUND"
    assert res_fail.error.message == "Object 'Cube' does not exist"


def test_create_primitive_args_validation():
    args = CreatePrimitiveArgs(
        primitive_type="CUBE",
        name="MyCube",
        location=(1.0, 2.0, 3.0),
        size=4.0,
    )
    assert args.primitive_type == "CUBE"
    assert args.name == "MyCube"
    assert args.location == (1.0, 2.0, 3.0)
    assert args.size == 4.0

    # Test invalid coordinate count
    with pytest.raises(ValidationError):
        CreatePrimitiveArgs(location=(1.0, 2.0))  # requires 3-tuple
