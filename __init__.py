"""
Palette Colorizer for Blender 5.0+.
Assign curated color palettes to viewport objects and showcase materials.

Features:
  - 30 categorized built-in palettes plus active Blender theme palette.
  - Live viewport updates and interactive color swatch preview strip.
  - Group colors per object, collection, root parent hierarchy, or mesh island.
  - Adjacent contrast graph coloring and object color pinning.
  - Single shared Object Info showcase material, per-swatch materials, or mesh color attributes.
  - Live Roughness, Metallic, and Specular material sliders.
  - Dominant color palette extraction from reference images.
  - Built-in add-on update installer in Preferences.
"""

bl_info = {
    "name": "Palette Colorizer",
    "author": "Klra",
    "version": (1, 1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > Palette",
    "description": "Assign curated color palettes to viewport objects and showcase materials",
    "category": "3D View",
}

def reload_modules():
    import importlib
    import bpy
    from . import palettes, updater, operators, properties, preferences, ui

    if hasattr(bpy.types.Scene, "palette_colorizer"):
        try:
            del bpy.types.Scene.palette_colorizer
        except Exception:
            pass

    for mod in (ui, updater, operators, properties, preferences):
        for attr_name in dir(mod):
            obj = getattr(mod, attr_name, None)
            if isinstance(obj, type) and hasattr(obj, "bl_rna"):
                try:
                    bpy.utils.unregister_class(obj)
                except Exception:
                    pass

    for mod in (palettes, updater, operators, properties, preferences, ui):
        importlib.reload(mod)

if "bpy" in locals():
    reload_modules()

import bpy
from . import palettes
from . import updater
from . import operators
from . import properties
from . import preferences
from . import ui

classes = (
    properties.SavedPaletteEntry,
    properties.PaletteColorItem,
    preferences.PaletteColorizerPreferences,
    properties.PaletteColorizerSettings,
    ui.PALETTE_UL_colors,
    ui.PALETTE_UL_saved,
    operators.PALETTE_OT_apply_colors,
    operators.PALETTE_OT_apply_materials,
    operators.PALETTE_OT_reset_colors,
    operators.PALETTE_OT_clear_materials,
    operators.PALETTE_OT_lock_selected,
    operators.PALETTE_OT_unlock_selected,
    operators.PALETTE_OT_randomize_seed,
    operators.PALETTE_OT_step_seed,
    operators.PALETTE_OT_copy_to_custom,
    operators.PALETTE_OT_sample_image_colors,
    operators.PALETTE_OT_add_custom_color,
    operators.PALETTE_OT_remove_custom_color,
    operators.PALETTE_OT_randomize_custom,
    operators.PALETTE_OT_copy_string,
    operators.PALETTE_OT_paste_string,
    operators.PALETTE_OT_export_json,
    operators.PALETTE_OT_import_json,
    operators.PALETTE_OT_library_save,
    operators.PALETTE_OT_library_load,
    operators.PALETTE_OT_library_remove,
    operators.PALETTE_OT_open_preferences,
    updater.PALETTE_OT_remove_update,
    updater.PALETTE_OT_use_update,
    updater.PALETTE_OT_rescan_updates,
    updater.PALETTE_OT_install_update_now,
    ui.PALETTE_PT_main,
    ui.PALETTE_PT_materials,
    ui.PALETTE_PT_options,
    ui.PALETTE_PT_share,
)

def _safe_unregister_class(cls):
    """Unregister a class or any stale RNA class with the same name."""
    try:
        bpy.utils.unregister_class(cls)
        return
    except Exception:
        pass

    existing = getattr(bpy.types, cls.__name__, None)
    if existing is not None:
        try:
            bpy.utils.unregister_class(existing)
        except Exception:
            pass

def register():
    for cls in reversed(classes):
        _safe_unregister_class(cls)

    pcoll = ui.load_custom_icons()
    thumb = pcoll.get("thumbnail") if pcoll else None
    icon_id = thumb.icon_id if thumb else 0

    if icon_id:
        ui.update_panel_icons(icon_id)

    for cls in classes:
        bpy.utils.register_class(cls)

    if icon_id and bpy.app.version >= (5, 0, 0):
        ui.update_panel_icons(icon_id)

    bpy.types.Scene.palette_colorizer = bpy.props.PointerProperty(
        type=properties.PaletteColorizerSettings
    )

    updater.verify_update()

def unregister():
    if hasattr(bpy.types.Scene, "palette_colorizer"):
        del bpy.types.Scene.palette_colorizer

    for cls in reversed(classes):
        _safe_unregister_class(cls)

    if hasattr(ui.PALETTE_PT_main, "bl_icon_value"):
        ui.PALETTE_PT_main.bl_icon_value = 0

    ui.unload_custom_icons()
    updater.install_update()

if __name__ == "__main__":
    register()
