"""Integration tests for local bridge HTTP server and client."""

import threading
import time
import httpx
import pytest

from blender_addon.bridge.auth import initialize_token
from blender_addon.bridge.dispatcher import process_queue
from blender_addon.bridge.server import start_bridge, stop_bridge
from blender_addon.operations.registry import register_operation
from mcp_server.client import BlenderBridgeClient
from shared.errors import BlenderControlError

TEST_HOST = "127.0.0.1"
TEST_PORT = 8799
TEST_TOKEN = "test_bridge_token_xyz123"


@pytest.fixture(scope="module", autouse=True)
def run_bridge_and_dispatcher():
    # Register a test operation
    @register_operation("test.echo")
    def echo_op(args):
        return {"echo": args.get("message", "")}

    # Start bridge
    initialize_token(TEST_TOKEN)
    start_bridge(host=TEST_HOST, port=TEST_PORT, token=TEST_TOKEN)

    # Run dispatcher loop in thread to simulate Blender main-thread timer
    running = True

    def dispatcher_loop():
        while running:
            process_queue()
            time.sleep(0.01)

    t = threading.Thread(target=dispatcher_loop, daemon=True)
    t.start()

    yield

    running = False
    stop_bridge()


@pytest.mark.asyncio
async def test_bridge_health_endpoint():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"http://{TEST_HOST}:{TEST_PORT}/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["blender_connected"] is True


@pytest.mark.asyncio
async def test_bridge_auth_rejection():
    async with httpx.AsyncClient() as client:
        # No auth
        resp = await client.post(
            f"http://{TEST_HOST}:{TEST_PORT}/execute",
            json={"operation": "test.echo"},
        )
        assert resp.status_code == 401

        # Bad token
        resp2 = await client.post(
            f"http://{TEST_HOST}:{TEST_PORT}/execute",
            headers={"Authorization": "Bearer invalid_token"},
            json={"operation": "test.echo"},
        )
        assert resp2.status_code == 401


@pytest.mark.asyncio
async def test_client_execute_success():
    client = BlenderBridgeClient(
        base_url=f"http://{TEST_HOST}:{TEST_PORT}",
        token=TEST_TOKEN,
    )
    result = await client.execute("test.echo", {"message": "Hello Blender MCP!"})
    assert result == {"echo": "Hello Blender MCP!"}


@pytest.mark.asyncio
async def test_client_execute_unsupported_operation():
    client = BlenderBridgeClient(
        base_url=f"http://{TEST_HOST}:{TEST_PORT}",
        token=TEST_TOKEN,
    )
    with pytest.raises(BlenderControlError) as exc_info:
        await client.execute("unknown.op", {})
    assert exc_info.value.code == "UNSUPPORTED_OPERATION"
