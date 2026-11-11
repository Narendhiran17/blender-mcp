"""Unit tests for Phase 2 data models."""

from shared.models import (
    CreateCollectionArgs,
    CreateSceneArgs,
    DeleteObjectArgs,
    DuplicateObjectArgs,
    LinkCollectionArgs,
    RenameObjectArgs,
    SaveSceneArgs,
    SelectObjectArgs,
    SetParentArgs,
    SetVisibilityArgs,
    TransformObjectArgs,
)


def test_transform_object_args():
    args = TransformObjectArgs(
        name="Cube",
        location=(1.0, 2.0, 3.0),
        rotation=(0.0, 1.57, 0.0),
        scale=(2.0, 2.0, 2.0),
        relative=True,
    )
    assert args.name == "Cube"
    assert args.location == (1.0, 2.0, 3.0)
    assert args.relative is True


def test_rename_and_duplicate_args():
    rename = RenameObjectArgs(old_name="Old", new_name="New")
    assert rename.old_name == "Old"
    assert rename.new_name == "New"

    dup = DuplicateObjectArgs(name="Original", new_name="Copy", offset=(1.0, 0.0, 0.0), linked=False)
    assert dup.name == "Original"
    assert dup.new_name == "Copy"
    assert dup.offset == (1.0, 0.0, 0.0)
    assert dup.linked is False


def test_hierarchy_and_visibility_args():
    parent_args = SetParentArgs(child_name="Child", parent_name="Parent", keep_transform=True)
    assert parent_args.child_name == "Child"
    assert parent_args.parent_name == "Parent"

    vis_args = SetVisibilityArgs(name="Light", hide_viewport=True, hide_render=False)
    assert vis_args.hide_viewport is True
    assert vis_args.hide_render is False

    sel_args = SelectObjectArgs(name="Camera", select=True, deselect_others=True)
    assert sel_args.deselect_others is True


def test_scene_and_collection_args():
    save_args = SaveSceneArgs(filepath="C:/test/project.blend")
    assert save_args.filepath == "C:/test/project.blend"

    scene_args = CreateSceneArgs(name="Level2", setup_mode="LINK_COPY")
    assert scene_args.name == "Level2"
    assert scene_args.setup_mode == "LINK_COPY"

    col_args = CreateCollectionArgs(name="Props", parent_collection="Scene Collection")
    assert col_args.name == "Props"

    link_args = LinkCollectionArgs(object_name="Chair", collection_name="Props", unlink_from_others=True)
    assert link_args.unlink_from_others is True
