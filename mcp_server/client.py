"""Async HTTP client for communicating with local Blender bridge."""

import logging
import uuid
from typing import Any, Dict, Optional
import httpx

from mcp_server.config import settings
from shared.constants import PROTOCOL_VERSION
from shared.errors import BlenderControlError, ErrorCode

logger = logging.getLogger("blender_ai_control.client")


class BlenderBridgeClient:
    """Client for local Blender HTTP bridge."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        host = settings.bridge_host
        port = settings.bridge_port
        self.base_url = base_url or f"http://{host}:{port}"
        self._token = token
        self.timeout = timeout or settings.bridge_timeout_seconds

    @property
    def token(self) -> str:
        if self._token:
            return self._token
        return settings.get_token()

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def check_health(self) -> Dict[str, Any]:
        """Check bridge health status."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/health")
                if resp.status_code == 200:
                    return resp.json()
                return {
                    "status": "error",
                    "blender_connected": False,
                    "http_status": resp.status_code,
                }
        except httpx.ConnectError:
            return {
                "status": "unavailable",
                "blender_connected": False,
                "message": f"Cannot connect to bridge at {self.base_url}. Is Blender running?",
            }
        except Exception as exc:
            return {
                "status": "error",
                "blender_connected": False,
                "error": str(exc),
            }

    async def get_status(self) -> Dict[str, Any]:
        """Get active scene and Blender runtime status."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.base_url}/status",
                    headers=self._get_headers(),
                )
                data = resp.json()
                if resp.status_code == 401:
                    raise BlenderControlError(
                        ErrorCode.AUTHENTICATION_FAILED,
                        "Bridge authentication failed. Verify BLENDER_BRIDGE_TOKEN.",
                        details=data.get("error", {}),
                    )
                if resp.status_code != 200:
                    err = data.get("error", {})
                    raise BlenderControlError(
                        err.get("code", ErrorCode.OPERATION_FAILED),
                        err.get("message", f"Status request failed with HTTP {resp.status_code}"),
                        details=err.get("details"),
                    )
                return data.get("result", {})
        except httpx.ConnectError as exc:
            raise BlenderControlError(
                ErrorCode.BRIDGE_UNAVAILABLE,
                f"Cannot connect to Blender bridge at {self.base_url}. Ensure Blender is running with add-on enabled.",
            ) from exc

    async def execute(
        self,
        operation: str,
        arguments: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Send structured operation to Blender bridge and wait for result."""
        req_id = f"mcp_{uuid.uuid4().hex[:8]}"
        payload = {
            "protocol_version": PROTOCOL_VERSION,
            "request_id": req_id,
            "operation": operation,
            "arguments": arguments or {},
            "timeout_seconds": timeout or self.timeout,
        }

        request_timeout = (timeout or self.timeout) + 5.0

        try:
            async with httpx.AsyncClient(timeout=request_timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/execute",
                    headers=self._get_headers(),
                    json=payload,
                )
        except httpx.ConnectError as exc:
            raise BlenderControlError(
                ErrorCode.BRIDGE_UNAVAILABLE,
                f"Cannot connect to Blender bridge at {self.base_url}. Make sure Blender is running and the add-on is enabled.",
            ) from exc
        except httpx.TimeoutException as exc:
            raise BlenderControlError(
                ErrorCode.TASK_TIMEOUT,
                f"Operation '{operation}' timed out waiting for Blender bridge response.",
            ) from exc

        try:
            data = resp.json()
        except Exception:
            raise BlenderControlError(
                ErrorCode.OPERATION_FAILED,
                f"Invalid non-JSON response from bridge (HTTP {resp.status_code}): {resp.text[:200]}",
            )

        if resp.status_code == 401:
            raise BlenderControlError(
                ErrorCode.AUTHENTICATION_FAILED,
                "Bridge authentication failed. Ensure the bridge token matches.",
                details=data.get("error"),
            )

        if data.get("status") == "failed" or resp.status_code != 200:
            err = data.get("error") or {}
            raise BlenderControlError(
                code=err.get("code", ErrorCode.OPERATION_FAILED),
                message=err.get("message", f"Operation '{operation}' failed"),
                details=err.get("details"),
            )

        return data.get("result", {})


# Default client instance
default_client = BlenderBridgeClient()
