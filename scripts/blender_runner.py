"""Background runner for automated testing of Blender AI Control add-on."""

import sys
import time
import bpy

# Ensure blender_ai_control is registered
if "blender_ai_control" not in bpy.context.preferences.addons:
    bpy.ops.preferences.addon_enable(module="blender_ai_control")

from blender_ai_control.bridge.dispatcher import process_queue
from blender_ai_control.operations.system import is_shutdown_requested

print("READY_FOR_MCP", flush=True)

# Main loop ticking dispatcher until shutdown requested
try:
    while not is_shutdown_requested():
        process_queue()
        time.sleep(0.01)
except KeyboardInterrupt:
    pass

print("BLENDER_RUNNER_EXIT", flush=True)
