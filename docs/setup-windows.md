# Windows Development & Setup Guide

This guide describes how to set up, install, and run **Blender AI Control MCP** locally on Windows.

---

## 1. Prerequisites

* **Operating System:** Windows 10 or 11 (64-bit)
* **Blender:** Blender 4.0+ (Tested with Blender 4.2 LTS at `C:\Program Files\Blender Foundation\Blender 4.2\blender.exe`)
* **Python:** Python 3.11+ (Tested with Python 3.11.6 at `C:\Program Files\Python311\python.exe`)
* **Git** installed and available in PATH

---

## 2. Setup Virtual Environment

Open PowerShell in the project directory:

```powershell
cd "c:\Users\naren\OneDrive\Desktop\blender MCP"

# Create virtual environment with Python 3.11
& "C:\Program Files\Python311\python.exe" -m venv .venv

# Activate environment
.venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -e .
pip install pytest pytest-asyncio ruff mypy
```

---

## 3. Install & Enable the Blender Add-on

Run the automated add-on installer script:

```powershell
.venv\Scripts\python.exe scripts\install_addon.py
```

This script:
1. Copies `blender_addon/` into Blender's user addons folder:
   `%APPDATA%\Blender Foundation\Blender\4.2\scripts\addons\blender_ai_control`
2. Automatically enables `blender_ai_control` in Blender's user preferences and saves them.

---

## 4. Launch Blender & Start the Bridge

Whenever Blender runs with the add-on enabled, the local HTTP bridge automatically binds to:
`http://127.0.0.1:8765`

The secure random token is generated and persisted in:
`%USERPROFILE%\.blender_ai_control\bridge_token`

You can verify the bridge health in your browser or with PowerShell:
```powershell
curl http://127.0.0.1:8765/health
```

---

## 5. Configure Your MCP Client

Add the following to your MCP client configuration (such as `claude_desktop_config.json`, Cursor, or Antigravity):

```json
{
  "mcpServers": {
    "blender": {
      "command": "c:\\Users\\naren\\OneDrive\\Desktop\\blender MCP\\.venv\\Scripts\\python.exe",
      "args": [
        "-m",
        "mcp_server.main"
      ],
      "env": {
        "BLENDER_BRIDGE_HOST": "127.0.0.1",
        "BLENDER_BRIDGE_PORT": "8765"
      }
    }
  }
}
```

---

## 6. Run Verification & Tests

To run the complete automated test suite (including live Blender cube creation):

```powershell
.venv\Scripts\pytest.exe -v
```

To run the standalone Phase 1 end-to-end verification script:

```powershell
.venv\Scripts\python.exe scripts\verify_phase1.py
```
