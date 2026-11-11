"""Operation registry mapping operation names to main-thread handler functions."""

import logging
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger("blender_ai_control.operations")

HandlerFunc = Callable[[Dict[str, Any]], Dict[str, Any]]

_REGISTRY: Dict[str, HandlerFunc] = {}


def register_operation(name: str) -> Callable[[HandlerFunc], HandlerFunc]:
    """Decorator to register an operation handler."""

    def decorator(fn: HandlerFunc) -> HandlerFunc:
        _REGISTRY[name] = fn
        return fn

    return decorator


def get_operation(name: str) -> Optional[HandlerFunc]:
    """Retrieve registered handler by operation name."""
    return _REGISTRY.get(name)


def list_operations() -> list[str]:
    """List all registered operation names."""
    return sorted(list(_REGISTRY.keys()))
