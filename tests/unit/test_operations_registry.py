"""Unit tests for operations registry."""

from blender_addon.operations.registry import get_operation, list_operations, register_operation


def test_operation_registration_and_execution():
    @register_operation("test.custom_op")
    def sample_op(args):
        return {"doubled": args.get("value", 0) * 2}

    handler = get_operation("test.custom_op")
    assert handler is not None
    res = handler({"value": 21})
    assert res == {"doubled": 42}
    assert "test.custom_op" in list_operations()


def test_unknown_operation():
    handler = get_operation("nonexistent.operation")
    assert handler is None
