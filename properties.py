"""
Scene and item PropertyGroup definitions with live update callbacks and native swatch getters.
"""

import bpy
from bpy.props import (
    StringProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    EnumProperty,
    BoolProperty,
    CollectionProperty,
    PointerProperty,
)
from bpy.types import PropertyGroup

from .palettes import (
    get_palette_items,
    get_active_palette_colors,
    load_colors_into_custom,
)
from .operators import apply_palette_to_scene, update_all_pc_materials

def on_live_setting_update(self, context):
    """Trigger immediate scene color update when Live Update is enabled."""
    if not context or not hasattr(context, "scene") or not context.scene:
        return
    settings = getattr(context.scene, "palette_colorizer", None)
    if settings and settings.auto_apply:
        apply_palette_to_scene(context, settings)

def on_material_surface_update(self, context):
    """Update Principled BSDF surface values across all PC_* materials immediately."""
    if not context or not hasattr(context, "scene") or not context.scene:
        return
    settings = getattr(context.scene, "palette_colorizer", None)
    if settings:
        update_all_pc_materials(settings)

def _make_swatch_getter(index):
    def getter(self):
        colors = get_active_palette_colors(self, bpy.context)
        if colors and 0 <= index < len(colors):
            rgba = colors[index]
            return (float(rgba[0]), float(rgba[1]), float(rgba[2]), float(rgba[3]))
        return (0.8, 0.8, 0.8, 1.0)
    return getter

def _make_swatch_setter(index):
    def setter(self, value):
        ctx = bpy.context
        colors = list(get_active_palette_colors(self, ctx))
        if self.palette_name != "CUSTOM":
            src_name = self.palette_name.replace("SAVED::", "")
            load_colors_into_custom(self, colors)
            self.custom_palette_name = f"{src_name} Edited"
            self.palette_name = "CUSTOM"
        if 0 <= index < len(self.custom_colors):
            self.custom_colors[index].color = (
                float(value[0]),
                float(value[1]),
                float(value[2]),
                float(value[3]),
            )
        if self.auto_apply and ctx and getattr(ctx, "scene", None):
            apply_palette_to_scene(ctx, self)
    return setter

class SavedPaletteEntry(PropertyGroup):
    name: StringProperty(name="Name", default="Unnamed")
    json_data: StringProperty(name="JSON", default="{}")

class PaletteColorItem(PropertyGroup):
    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(0.8, 0.8, 0.8, 1.0),
        update=on_live_setting_update,
    )

class PaletteColorizerSettings(PropertyGroup):
    palette_name: EnumProperty(
        name="Palette",
        items=get_palette_items,
        description="Select a built-in, theme, saved, or custom palette",
        update=on_live_setting_update,
    )
    auto_apply: BoolProperty(
        name="Live Update",
        description="Automatically update object colors when you change palette, seed, or mode",
        default=True,
    )
    custom_colors: CollectionProperty(type=PaletteColorItem)
    custom_color_index: IntProperty(default=0)
    custom_palette_name: StringProperty(
        name="Palette Name",
        default="My Palette",
        description="Name used when you save or export this custom palette",
    )

    swatch_0: FloatVectorProperty(
        name="Swatch 1", subtype='COLOR', size=4, min=0.0, max=1.0,
        description="Click to inspect or edit Swatch 1 (forks preset into Custom mode)",
        get=_make_swatch_getter(0), set=_make_swatch_setter(0),
    )
    swatch_1: FloatVectorProperty(
        name="Swatch 2", subtype='COLOR', size=4, min=0.0, max=1.0,
        description="Click to inspect or edit Swatch 2 (forks preset into Custom mode)",
        get=_make_swatch_getter(1), set=_make_swatch_setter(1),
    )
    swatch_2: FloatVectorProperty(
        name="Swatch 3", subtype='COLOR', size=4, min=0.0, max=1.0,
        description="Click to inspect or edit Swatch 3 (forks preset into Custom mode)",
        get=_make_swatch_getter(2), set=_make_swatch_setter(2),
    )
    swatch_3: FloatVectorProperty(
        name="Swatch 4", subtype='COLOR', size=4, min=0.0, max=1.0,
        description="Click to inspect or edit Swatch 4 (forks preset into Custom mode)",
        get=_make_swatch_getter(3), set=_make_swatch_setter(3),
    )
    swatch_4: FloatVectorProperty(
        name="Swatch 5", subtype='COLOR', size=4, min=0.0, max=1.0,
        description="Click to inspect or edit Swatch 5 (forks preset into Custom mode)",
        get=_make_swatch_getter(4), set=_make_swatch_setter(4),
    )
    swatch_5: FloatVectorProperty(
        name="Swatch 6", subtype='COLOR', size=4, min=0.0, max=1.0,
        description="Click to inspect or edit Swatch 6 (forks preset into Custom mode)",
        get=_make_swatch_getter(5), set=_make_swatch_setter(5),
    )
    swatch_6: FloatVectorProperty(
        name="Swatch 7", subtype='COLOR', size=4, min=0.0, max=1.0,
        description="Click to inspect or edit Swatch 7 (forks preset into Custom mode)",
        get=_make_swatch_getter(6), set=_make_swatch_setter(6),
    )
    swatch_7: FloatVectorProperty(
        name="Swatch 8", subtype='COLOR', size=4, min=0.0, max=1.0,
        description="Click to inspect or edit Swatch 8 (forks preset into Custom mode)",
        get=_make_swatch_getter(7), set=_make_swatch_setter(7),
    )

    source_image: PointerProperty(
        type=bpy.types.Image,
        name="Image",
        description="Select a loaded image to sample dominant colors into the Custom palette",
    )
    output_mode: EnumProperty(
        name="Output",
        items=[
            ("VIEWPORT", "Viewport", "Apply colors to viewport object color (obj.color)"),
            ("MATERIAL", "Materials", "Apply colors to Principled BSDF showcase materials"),
            ("BOTH", "Both", "Apply colors to both viewport object color and render materials"),
        ],
        default="VIEWPORT",
        update=on_live_setting_update,
    )
    material_mode: EnumProperty(
        name="Material Mode",
        items=[
            (
                "SHARED_OBJECT_INFO",
                "Shared Master (1 Mat)",
                "Use a single shared material reading Object Info Color across all objects",
            ),
            (
                "PER_SWATCH",
                "Per Swatch",
                "Create one shared material per palette swatch color",
            ),
            (
                "COLOR_ATTRIBUTE",
                "Mesh Color Attribute",
                "Write colors to the PC_Color mesh attribute and render via an Attribute node",
            ),
        ],
        default="SHARED_OBJECT_INFO",
        update=on_live_setting_update,
    )
    mat_roughness: FloatProperty(
        name="Roughness",
        description="Surface roughness for all Palette Colorizer materials",
        default=0.40,
        min=0.0,
        max=1.0,
        subtype='FACTOR',
        update=on_material_surface_update,
    )
    mat_metallic: FloatProperty(
        name="Metallic",
        description="Metallic value for all Palette Colorizer materials",
        default=0.10,
        min=0.0,
        max=1.0,
        subtype='FACTOR',
        update=on_material_surface_update,
    )
    mat_specular: FloatProperty(
        name="Specular",
        description="Specular IOR level for all Palette Colorizer materials",
        default=0.50,
        min=0.0,
        max=1.0,
        subtype='FACTOR',
        update=on_material_surface_update,
    )
    protect_real_materials: BoolProperty(
        name="Protect Existing Materials",
        description=(
            "When enabled, skip objects that already have non-palette materials. "
            "When disabled, add a temporary palette material slot without overwriting existing materials"
        ),
        default=False,
    )
    assignment_mode: EnumProperty(
        name="Distribution",
        items=[
            ("SEQUENTIAL", "Sequential", "Assign colors in palette order"),
            ("RANDOM", "Random", "Assign colors randomly from palette using the seed"),
            ("BY_NAME", "By Name", "Assign a stable color based on object or group name"),
        ],
        default="SEQUENTIAL",
        update=on_live_setting_update,
    )
    grouping_mode: EnumProperty(
        name="Group By",
        items=[
            ("OBJECT", "Per Object", "Assign a color to each individual object"),
            ("COLLECTION", "Per Collection", "Assign a shared color to all objects in the same collection"),
            ("ROOT_PARENT", "Per Root Parent", "Assign a shared color to each parent hierarchy assembly"),
            ("ISLAND", "Per Mesh Island", "Assign colors to disconnected mesh islands inside each object"),
        ],
        default="OBJECT",
        update=on_live_setting_update,
    )
    avoid_adjacent_duplicates: BoolProperty(
        name="Adjacent Contrast",
        description="Reduce duplicate random colors on touching or overlapping neighbor objects",
        default=True,
        update=on_live_setting_update,
    )
    affect: EnumProperty(
        name="Scope",
        items=[
            ("SELECTED", "Selected", "Affect only selected objects"),
            ("VISIBLE", "Visible", "Affect all visible objects in the viewport"),
            ("ALL", "All", "Affect every valid object in the scene"),
        ],
        default="SELECTED",
        update=on_live_setting_update,
    )
    include_non_mesh: BoolProperty(
        name="Include Curves & Text",
        description="Include Curve, Surface, Meta, and Text objects in addition to Meshes",
        default=True,
        update=on_live_setting_update,
    )
    auto_switch_shading: BoolProperty(
        name="Auto-Switch Viewport Shading",
        description="Automatically set the active 3D Viewport shading color mode",
        default=True,
    )
    preserve_alpha: BoolProperty(
        name="Preserve Alpha",
        description="Keep the current alpha value of each object",
        default=False,
        update=on_live_setting_update,
    )
    randomize_seed: IntProperty(
        name="Seed",
        default=1,
        min=1,
        max=9999,
        description="Seed value for random color assignment (1 through 9999)",
        update=on_live_setting_update,
    )
    paste_buffer: StringProperty(
        name="Paste String",
        description="Paste a palette share string here, then select Import Pasted String",
        default="",
    )
