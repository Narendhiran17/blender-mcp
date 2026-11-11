# Local Blender Bridge API Contract

The **Local Blender Bridge** runs inside Blender as a background HTTP daemon binding strictly to `127.0.0.1` (default port `8765`).

---

## 1. Authentication

All requests to `/status` and `/execute` require authentication using a shared secret token:
- Either via `Authorization: Bearer <token>`
- Or via `X-Blender-Bridge-Token: <token>`

The token is loaded from `BLENDER_BRIDGE_TOKEN` or read from `%USERPROFILE%/.blender_ai_control/bridge_token`.

---

## 2. Endpoints

### `GET /health`
* **Auth required:** No
* **Response (200 OK):**
```json
{
  "status": "ok",
  "blender_connected": true,
  "protocol_version": "1"
}
```

---

### `GET /status`
* **Auth required:** Yes
* **Response (200 OK):**
```json
{
  "protocol_version": "1",
  "request_id": "status_ab12cd34",
  "status": "completed",
  "result": {
    "blender_connected": true,
    "blender_version": [4, 2, 3],
    "blender_version_string": "4.2.3 LTS",
    "project_filepath": null,
    "is_saved": false,
    "is_dirty": false,
    "active_scene": "Scene",
    "objects_count": 3,
    "active_object": null,
    "selected_objects": [],
    "render_engine": "BLENDER_EEVEE_NEXT"
  },
  "error": null
}
```

---

### `POST /execute`
* **Auth required:** Yes
* **Request Payload (`RequestEnvelope`):**
```json
{
  "protocol_version": "1",
  "request_id": "mcp_001",
  "operation": "object.create_primitive",
  "arguments": {
    "primitive_type": "CUBE",
    "name": "MyCube",
    "location": [0.0, 0.0, 1.0],
    "rotation": [0.0, 0.0, 0.0],
    "scale": [1.0, 1.0, 1.0],
    "size": 2.0
  },
  "timeout_seconds": 30.0
}
```

* **Success Response (200 OK):**
```json
{
  "protocol_version": "1",
  "request_id": "mcp_001",
  "status": "completed",
  "result": {
    "name": "MyCube",
    "type": "MESH",
    "location": [0.0, 0.0, 1.0],
    "rotation_euler": [0.0, 0.0, 0.0],
    "scale": [1.0, 1.0, 1.0],
    "dimensions": [2.0, 2.0, 2.0]
  },
  "error": null
}
```

* **Failure Response (200 or 4xx/5xx):**
```json
{
  "protocol_version": "1",
  "request_id": "mcp_001",
  "status": "failed",
  "result": null,
  "error": {
    "code": "UNSUPPORTED_OPERATION",
    "message": "Operation 'unsupported.op' is not registered or supported",
    "details": {}
  }
}
```

---

## 3. Error Codes

| Code | Meaning |
| :--- | :--- |
| `BLENDER_NOT_RUNNING` | Cannot reach Blender process or bridge |
| `BRIDGE_UNAVAILABLE` | Bridge port refused connection |
| `AUTHENTICATION_FAILED` | Token missing or incorrect |
| `INVALID_ARGUMENT` | Malformed JSON or invalid schema values |
| `UNSUPPORTED_OPERATION` | Operation not in allowlist / registry |
| `OBJECT_NOT_FOUND` | Named Blender object not present in scene |
| `OPERATION_FAILED` | Runtime exception raised during execution |
| `TASK_TIMEOUT` | Operation exceeded specified timeout seconds |
