# Blender AI Control MCP — Tool Catalogue

Complete reference for all MCP tools exposed by the **Blender AI Control MCP Server**.

---

## 1. System & Connection Tools

### `blender_health`
* **Description:** Check if the local Blender bridge is running and reachable.
* **Arguments:** None
* **Returns:**
```json
{
  "status": "ok",
  "blender_connected": true,
  "protocol_version": "1"
}
```

### `blender_status`
* **Description:** Retrieve real-time project and scene status from Blender (version, active scene, objects count, active selection, dirty state).
* **Arguments:** None
* **Returns:**
```json
{
  "blender_connected": true,
  "blender_version": [4, 2, 3],
  "blender_version_string": "4.2.3 LTS",
  "project_filepath": null,
  "is_saved": false,
  "is_dirty": true,
  "active_scene": "Scene",
  "objects_count": 4,
  "active_object": "Phase1_Proof_Cube",
  "selected_objects": ["Phase1_Proof_Cube"],
  "render_engine": "BLENDER_EEVEE_NEXT"
}
```

### `blender_version`
* **Description:** Get Blender version and build platform information.
* **Arguments:** None
* **Returns:**
```json
{
  "version": [4, 2, 3],
  "version_string": "4.2.3 LTS",
  "build_platform": "win32"
}
```

---

## 2. Scene & Collection Tools

### `blender_list_scenes`
* **Description:** List all scenes in the current project with their render engines, active cameras, and object counts.
* **Arguments:** None
* **Returns:**
```json
{
  "total": 1,
  "scenes": [
    {
      "name": "Scene",
      "is_active": true,
      "render_engine": "BLENDER_EEVEE_NEXT",
      "active_camera": "Camera",
      "objects_count": 3,
      "unit_system": "METRIC"
    }
  ],
  "active_scene": "Scene"
}
```

### `blender_inspect_scene`
* **Description:** Inspect detailed configuration of a scene (resolution, FPS, active camera, render engine, units, collections).
* **Arguments:**
  * `name` *(string, optional)*: Name of the scene (defaults to active scene).
* **Returns:**
```json
{
  "name": "Scene",
  "is_active": true,
  "render_engine": "BLENDER_EEVEE_NEXT",
  "resolution_x": 1920,
  "resolution_y": 1080,
  "fps": 24,
  "active_camera": "Camera",
  "objects_count": 3,
  "root_collections": []
}
```

### `blender_create_scene`
* **Description:** Create a new scene in the project.
* **Arguments:**
  * `name` *(string, default "New Scene")*: Name of the new scene.
  * `setup_mode` *(string, default "NEW")*: `"NEW"`, `"EMPTY"`, `"LINK_COPY"`, or `"FULL_COPY"`.

### `blender_set_active_scene`
* **Description:** Switch the active scene in Blender to the specified scene.
* **Arguments:**
  * `name` *(string, required)*: Name of the target scene.

### `blender_save_project`
* **Description:** Save the Blender project (.blend). If never saved before, `filepath` must be provided.
* **Arguments:**
  * `filepath` *(string, optional)*: Absolute path to save the `.blend` file.

### `blender_list_collections`
* **Description:** List all collections in the active scene and their member objects.
* **Arguments:** None

### `blender_create_collection`
* **Description:** Create a new collection, optionally nested under a parent collection.
* **Arguments:**
  * `name` *(string, required)*: Collection name.
  * `parent_collection` *(string, optional)*: Parent collection name.

### `blender_link_to_collection`
* **Description:** Link an object into a collection, with option to unlink it from all other collections.
* **Arguments:**
  * `object_name` *(string, required)*: Object to link.
  * `collection_name` *(string, required)*: Target collection.
  * `unlink_from_others` *(boolean, default false)*: Whether to remove the object from all other collections.

---

## 3. Object Management Tools

### `blender_create_primitive`
* **Description:** Create a 3D primitive mesh in Blender.
* **Arguments:**
  * `primitive_type` *(string, default "CUBE")*: `"CUBE"`, `"UV_SPHERE"`, `"CYLINDER"`, `"PLANE"`, `"CONE"`, `"TORUS"`.
  * `name` *(string, optional)*: Name for newly created object.
  * `location` *(float array, default [0,0,0])*: `[X, Y, Z]` location.
  * `rotation` *(float array, default [0,0,0])*: `[X, Y, Z]` Euler rotation in radians.
  * `scale` *(float array, default [1,1,1])*: `[X, Y, Z]` scale multiplier.
  * `size` *(float, default 2.0)*: Overall dimensions/radius.

### `blender_inspect_object`
* **Description:** Inspect detailed properties of an object in Blender.
* **Arguments:**
  * `name` *(string, required)*: Name of object to inspect.
* **Returns:** Transforms, dimensions, vertex/poly count, parent, children, collections, materials, and modifiers.

### `blender_list_objects`
* **Description:** List objects in active scene, optionally filtered by type or collection.
* **Arguments:**
  * `object_type` *(string, optional)*: e.g. `"MESH"`, `"CAMERA"`, `"LIGHT"`.
  * `collection` *(string, optional)*: Filter by collection name.

### `blender_rename_object`
* **Description:** Rename an existing object in Blender.
* **Arguments:**
  * `old_name` *(string, required)*: Current name.
  * `new_name` *(string, required)*: New name.

### `blender_transform_object`
* **Description:** Set or adjust location, rotation, or scale of an object.
* **Arguments:**
  * `name` *(string, required)*: Object name.
  * `location` *(float array, optional)*: `[X, Y, Z]` location.
  * `rotation` *(float array, optional)*: `[X, Y, Z]` Euler rotation in radians.
  * `scale` *(float array, optional)*: `[X, Y, Z]` scale.
  * `relative` *(boolean, default false)*: If true, adds/multiplies relative to existing transforms.

### `blender_duplicate_object`
* **Description:** Duplicate an object (deep copy or linked) with optional offset and new name.
* **Arguments:**
  * `name` *(string, required)*: Object to duplicate.
  * `new_name` *(string, optional)*: Name for duplicated copy.
  * `linked` *(boolean, default false)*: Shared mesh data if true.
  * `offset` *(float array, optional)*: `[X, Y, Z]` translation offset.

### `blender_delete_object`
* **Description:** Delete an object from Blender and unreference data blocks.
* **Arguments:**
  * `name` *(string, required)*: Name of object to delete.
  * `delete_data` *(boolean, default true)*: Whether to clean up unreferenced mesh data.

### `blender_set_parent`
* **Description:** Parent a child object to a parent object, or unparent if parent_name is omitted.
* **Arguments:**
  * `child_name` *(string, required)*: Name of child object.
  * `parent_name` *(string, optional)*: Name of parent object (omit or null to unparent).
  * `keep_transform` *(boolean, default true)*: Preserve world space transform without snapping.

### `blender_set_visibility`
* **Description:** Set object visibility in 3D viewport and/or final render.
* **Arguments:**
  * `name` *(string, required)*: Name of object.
  * `hide_viewport` *(boolean, optional)*: Show/hide in viewport.
  * `hide_render` *(boolean, optional)*: Show/hide in render.

### `blender_select_object`
* **Description:** Select or deselect an object, optionally deselect other objects, and set as active object.
* **Arguments:**
  * `name` *(string, optional)*: Target object.
  * `select` *(boolean, default true)*: Select or deselect.
  * `deselect_others` *(boolean, default false)*: Clear other selections.
  * `set_active` *(boolean, default true)*: Set as active object in context.
