"""
Palette Colorizer for Blender.
Assign colors from named palettes to objects for viewport display and renders.
The add-on sets the viewport shading to Object color mode and sets obj.color for each object.

Features:
  - 30 curated built-in palettes.
  - Dynamic palette from the active Blender theme.
  - Create and edit custom palettes.
  - Copy and paste palettes as compact JSON strings.
  - Export and import palettes as JSON files.
  - Save named palettes to local add-on preferences across blend files.
  - Assign palette colors to Principled BSDF materials for Cycles and EEVEE renders.
"""

bl_info = {
    "name": "Palette Colorizer",
    "author": "Klra Man",
    "version": (5, 2, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Palette",
    "description": "Apply named color palettes to object viewport colors",
    "category": "3D View",
}

import bpy
import json
import random
import colorsys
from bpy.props import (
    StringProperty, FloatVectorProperty, IntProperty,
    EnumProperty, BoolProperty, CollectionProperty
)
from bpy.types import (
    AddonPreferences, PropertyGroup, Operator, Panel, UIList
)
from bpy_extras.io_utils import ImportHelper, ExportHelper


# ===========================================================================
# Built-in palettes (linear RGB, alpha=1)
# ===========================================================================

BUILTIN_PALETTES = {
    "Nord": [
        (0.53, 0.75, 0.82, 1.0),
        (0.56, 0.74, 0.73, 1.0),
        (0.51, 0.63, 0.76, 1.0),
        (0.40, 0.55, 0.75, 1.0),
        (0.75, 0.38, 0.38, 1.0),
        (0.82, 0.53, 0.35, 1.0),
        (0.80, 0.74, 0.45, 1.0),
        (0.53, 0.75, 0.52, 1.0),
    ],
    "Pastel": [
        (1.00, 0.71, 0.76, 1.0),
        (1.00, 0.85, 0.69, 1.0),
        (1.00, 1.00, 0.71, 1.0),
        (0.71, 0.94, 0.71, 1.0),
        (0.71, 0.87, 1.00, 1.0),
        (0.84, 0.71, 1.00, 1.0),
        (1.00, 0.71, 0.92, 1.0),
        (0.71, 0.94, 0.94, 1.0),
    ],
    "Neon": [
        (1.00, 0.07, 0.57, 1.0),
        (0.00, 1.00, 0.50, 1.0),
        (0.00, 0.75, 1.00, 1.0),
        (1.00, 0.90, 0.00, 1.0),
        (1.00, 0.27, 0.00, 1.0),
        (0.60, 0.00, 1.00, 1.0),
        (0.00, 1.00, 1.00, 1.0),
        (1.00, 0.50, 0.00, 1.0),
    ],
    "Earthy": [
        (0.55, 0.27, 0.07, 1.0),
        (0.72, 0.52, 0.04, 1.0),
        (0.40, 0.60, 0.22, 1.0),
        (0.74, 0.72, 0.42, 1.0),
        (0.50, 0.38, 0.28, 1.0),
        (0.82, 0.71, 0.55, 1.0),
        (0.27, 0.45, 0.30, 1.0),
        (0.60, 0.47, 0.35, 1.0),
    ],
    "Solarized": [
        (0.00, 0.47, 0.54, 1.0),
        (0.15, 0.55, 0.82, 1.0),
        (0.16, 0.63, 0.60, 1.0),
        (0.52, 0.60, 0.00, 1.0),
        (0.71, 0.54, 0.00, 1.0),
        (0.80, 0.29, 0.09, 1.0),
        (0.83, 0.21, 0.51, 1.0),
        (0.42, 0.44, 0.77, 1.0),
    ],
    "Candy": [
        (1.00, 0.41, 0.71, 1.0),
        (0.39, 0.58, 0.93, 1.0),
        (0.20, 0.80, 0.60, 1.0),
        (1.00, 0.75, 0.20, 1.0),
        (0.80, 0.20, 0.80, 1.0),
        (0.20, 0.80, 0.80, 1.0),
        (1.00, 0.50, 0.20, 1.0),
        (0.50, 0.80, 0.20, 1.0),
    ],
    "Grayscale": [
        (0.00, 0.00, 0.00, 1.0),
        (0.14, 0.14, 0.14, 1.0),
        (0.27, 0.27, 0.27, 1.0),
        (0.40, 0.40, 0.40, 1.0),
        (0.53, 0.53, 0.53, 1.0),
        (0.65, 0.65, 0.65, 1.0),
        (0.80, 0.80, 0.80, 1.0),
        (1.00, 1.00, 1.00, 1.0),
    ],
    "Ruby": [
        (0.90, 0.10, 0.10, 1.0),
        (0.75, 0.18, 0.18, 1.0),
        (1.00, 0.27, 0.20, 1.0),
        (0.80, 0.40, 0.40, 1.0),
        (0.60, 0.08, 0.08, 1.0),
        (1.00, 0.55, 0.45, 1.0),
        (0.70, 0.20, 0.30, 1.0),
        (0.95, 0.70, 0.65, 1.0),
    ],
    "Ocean": [
        (0.05, 0.30, 0.70, 1.0),
        (0.10, 0.50, 0.85, 1.0),
        (0.00, 0.65, 0.90, 1.0),
        (0.20, 0.20, 0.55, 1.0),
        (0.35, 0.70, 0.90, 1.0),
        (0.00, 0.45, 0.65, 1.0),
        (0.55, 0.85, 0.95, 1.0),
        (0.10, 0.35, 0.80, 1.0),
    ],
    "Forest": [
        (0.10, 0.40, 0.15, 1.0),
        (0.25, 0.60, 0.20, 1.0),
        (0.45, 0.72, 0.30, 1.0),
        (0.05, 0.28, 0.10, 1.0),
        (0.55, 0.75, 0.40, 1.0),
        (0.30, 0.50, 0.25, 1.0),
        (0.65, 0.80, 0.50, 1.0),
        (0.18, 0.45, 0.30, 1.0),
    ],
    "Cyberpunk": [
        (1.00, 0.00, 0.50, 1.0),
        (0.00, 0.90, 1.00, 1.0),
        (1.00, 0.90, 0.05, 1.0),
        (0.45, 0.05, 0.90, 1.0),
        (0.05, 0.30, 0.95, 1.0),
        (1.00, 0.20, 0.10, 1.0),
        (0.10, 0.80, 0.60, 1.0),
        (0.80, 0.10, 0.70, 1.0),
    ],
    "Sunset": [
        (0.20, 0.10, 0.40, 1.0),
        (0.50, 0.15, 0.45, 1.0),
        (0.80, 0.25, 0.35, 1.0),
        (0.95, 0.45, 0.25, 1.0),
        (1.00, 0.70, 0.20, 1.0),
        (1.00, 0.85, 0.40, 1.0),
        (0.90, 0.40, 0.55, 1.0),
        (0.35, 0.20, 0.50, 1.0),
    ],
    "Autumn": [
        (0.70, 0.25, 0.05, 1.0),
        (0.85, 0.45, 0.10, 1.0),
        (0.90, 0.65, 0.15, 1.0),
        (0.55, 0.18, 0.10, 1.0),
        (0.40, 0.30, 0.15, 1.0),
        (0.60, 0.50, 0.20, 1.0),
        (0.80, 0.35, 0.15, 1.0),
        (0.30, 0.20, 0.10, 1.0),
    ],
    "Synthwave": [
        (0.15, 0.05, 0.30, 1.0),
        (0.45, 0.05, 0.55, 1.0),
        (0.90, 0.10, 0.60, 1.0),
        (1.00, 0.35, 0.70, 1.0),
        (0.10, 0.85, 0.95, 1.0),
        (0.00, 0.50, 0.80, 1.0),
        (0.95, 0.60, 0.20, 1.0),
        (0.70, 0.20, 0.85, 1.0),
    ],
    "Desert": [
        (0.85, 0.65, 0.40, 1.0),
        (0.75, 0.45, 0.25, 1.0),
        (0.60, 0.30, 0.15, 1.0),
        (0.90, 0.78, 0.55, 1.0),
        (0.70, 0.55, 0.35, 1.0),
        (0.50, 0.40, 0.30, 1.0),
        (0.45, 0.50, 0.40, 1.0),
        (0.80, 0.40, 0.30, 1.0),
    ],
    "Retro": [
        (0.85, 0.60, 0.10, 1.0),
        (0.80, 0.30, 0.15, 1.0),
        (0.35, 0.50, 0.35, 1.0),
        (0.60, 0.35, 0.20, 1.0),
        (0.90, 0.85, 0.70, 1.0),
        (0.20, 0.45, 0.50, 1.0),
        (0.70, 0.20, 0.25, 1.0),
        (0.40, 0.25, 0.15, 1.0),
    ],
    "Lavender": [
        (0.80, 0.75, 0.90, 1.0),
        (0.65, 0.55, 0.80, 1.0),
        (0.50, 0.40, 0.70, 1.0),
        (0.35, 0.25, 0.55, 1.0),
        (0.88, 0.82, 0.95, 1.0),
        (0.55, 0.45, 0.75, 1.0),
        (0.75, 0.60, 0.85, 1.0),
        (0.40, 0.30, 0.60, 1.0),
    ],
    "Emerald": [
        (0.05, 0.35, 0.25, 1.0),
        (0.10, 0.55, 0.35, 1.0),
        (0.15, 0.75, 0.45, 1.0),
        (0.40, 0.85, 0.60, 1.0),
        (0.05, 0.25, 0.20, 1.0),
        (0.20, 0.65, 0.50, 1.0),
        (0.60, 0.90, 0.75, 1.0),
        (0.10, 0.45, 0.40, 1.0),
    ],
    "Coffee": [
        (0.22, 0.14, 0.10, 1.0),
        (0.35, 0.22, 0.15, 1.0),
        (0.50, 0.32, 0.22, 1.0),
        (0.65, 0.45, 0.30, 1.0),
        (0.80, 0.62, 0.45, 1.0),
        (0.90, 0.78, 0.65, 1.0),
        (0.42, 0.28, 0.18, 1.0),
        (0.28, 0.18, 0.12, 1.0),
    ],
    "Sakura": [
        (1.00, 0.85, 0.90, 1.0),
        (0.98, 0.70, 0.80, 1.0),
        (0.95, 0.55, 0.70, 1.0),
        (0.85, 0.40, 0.60, 1.0),
        (0.45, 0.30, 0.35, 1.0),
        (0.65, 0.75, 0.60, 1.0),
        (1.00, 0.92, 0.95, 1.0),
        (0.75, 0.35, 0.50, 1.0),
    ],
    "Monokai": [
        (0.98, 0.15, 0.45, 1.0),
        (0.65, 0.85, 0.15, 1.0),
        (0.90, 0.85, 0.35, 1.0),
        (0.40, 0.80, 0.90, 1.0),
        (0.68, 0.50, 0.90, 1.0),
        (0.95, 0.55, 0.15, 1.0),
        (0.45, 0.45, 0.40, 1.0),
        (0.95, 0.95, 0.90, 1.0),
    ],
    "Dracula": [
        (0.16, 0.16, 0.21, 1.0),
        (0.38, 0.44, 0.64, 1.0),
        (0.55, 0.91, 0.99, 1.0),
        (0.31, 0.98, 0.48, 1.0),
        (1.00, 0.73, 0.42, 1.0),
        (1.00, 0.47, 0.77, 1.0),
        (0.74, 0.58, 0.98, 1.0),
        (0.95, 0.95, 0.95, 1.0),
    ],
    "Gruvbox": [
        (0.80, 0.14, 0.11, 1.0),
        (0.60, 0.60, 0.10, 1.0),
        (0.84, 0.60, 0.13, 1.0),
        (0.27, 0.52, 0.53, 1.0),
        (0.70, 0.40, 0.55, 1.0),
        (0.41, 0.60, 0.50, 1.0),
        (0.82, 0.35, 0.10, 1.0),
        (0.92, 0.86, 0.70, 1.0),
    ],
    "Tokyo Night": [
        (0.10, 0.11, 0.18, 1.0),
        (0.45, 0.65, 0.95, 1.0),
        (0.73, 0.55, 0.95, 1.0),
        (0.45, 0.85, 0.85, 1.0),
        (0.95, 0.45, 0.60, 1.0),
        (0.98, 0.70, 0.40, 1.0),
        (0.25, 0.35, 0.55, 1.0),
        (0.80, 0.85, 0.95, 1.0),
    ],
    "Vaporwave": [
        (0.40, 0.85, 0.90, 1.0),
        (0.95, 0.55, 0.80, 1.0),
        (0.70, 0.45, 0.85, 1.0),
        (0.55, 0.90, 0.75, 1.0),
        (1.00, 0.75, 0.85, 1.0),
        (0.30, 0.60, 0.80, 1.0),
        (0.85, 0.40, 0.65, 1.0),
        (0.95, 0.90, 0.95, 1.0),
    ],
    "Clay": [
        (0.75, 0.35, 0.25, 1.0),
        (0.60, 0.25, 0.18, 1.0),
        (0.80, 0.50, 0.35, 1.0),
        (0.85, 0.65, 0.45, 1.0),
        (0.50, 0.45, 0.40, 1.0),
        (0.65, 0.55, 0.50, 1.0),
        (0.40, 0.20, 0.15, 1.0),
        (0.90, 0.75, 0.60, 1.0),
    ],
    "Midnight": [
        (0.05, 0.07, 0.15, 1.0),
        (0.10, 0.15, 0.30, 1.0),
        (0.15, 0.25, 0.50, 1.0),
        (0.25, 0.45, 0.75, 1.0),
        (0.40, 0.65, 0.90, 1.0),
        (0.65, 0.80, 0.95, 1.0),
        (0.20, 0.35, 0.60, 1.0),
        (0.85, 0.90, 1.00, 1.0),
    ],
    "Citrus": [
        (0.60, 0.85, 0.15, 1.0),
        (0.95, 0.90, 0.10, 1.0),
        (1.00, 0.65, 0.05, 1.0),
        (1.00, 0.40, 0.10, 1.0),
        (0.95, 0.20, 0.30, 1.0),
        (0.35, 0.75, 0.25, 1.0),
        (1.00, 0.80, 0.25, 1.0),
        (0.85, 0.30, 0.15, 1.0),
    ],
    "Copper": [
        (0.72, 0.45, 0.30, 1.0),
        (0.55, 0.30, 0.18, 1.0),
        (0.85, 0.55, 0.35, 1.0),
        (0.30, 0.60, 0.55, 1.0),
        (0.20, 0.48, 0.45, 1.0),
        (0.45, 0.75, 0.68, 1.0),
        (0.40, 0.22, 0.12, 1.0),
        (0.90, 0.68, 0.50, 1.0),
    ],
    "Arctic": [
        (0.85, 0.92, 0.98, 1.0),
        (0.65, 0.80, 0.92, 1.0),
        (0.45, 0.68, 0.85, 1.0),
        (0.25, 0.50, 0.75, 1.0),
        (0.12, 0.30, 0.55, 1.0),
        (0.08, 0.18, 0.38, 1.0),
        (0.55, 0.75, 0.88, 1.0),
        (0.95, 0.98, 1.00, 1.0),
    ],
}


# ===========================================================================
# Palette serialization helpers
# ===========================================================================

def palette_to_dict(name, colors):
    """Convert palette name and color list to JSON dictionary."""
    return {
        "name": name,
        "version": 1,
        "colors": [[round(c, 4) for c in rgba] for rgba in colors],
    }


def dict_to_palette(data):
    """Parse dictionary from JSON and return palette name and colors."""
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object.")
    colors_raw = data.get("colors")
    if not colors_raw or not isinstance(colors_raw, list):
        raise ValueError("Missing or invalid colors list.")
    colors = []
    for entry in colors_raw:
        if len(entry) == 3:
            entry = entry + [1.0]
        if len(entry) != 4:
            raise ValueError(f"Color entry must have 3 or 4 components: {entry}")
        colors.append(tuple(float(v) for v in entry))
    name = data.get("name", "Imported")
    return name, colors


def load_colors_into_custom(settings, colors):
    """Replace custom palette slots with given color list."""
    settings.custom_colors.clear()
    for rgba in colors:
        item = settings.custom_colors.add()
        item.color = rgba
    settings.custom_color_index = 0


def get_theme_palette_colors(context):
    """Extract representative colors from the active Blender theme."""
    try:
        theme = context.preferences.themes[0]
        v3d = theme.view_3d
        ui = theme.user_interface
        return [
            tuple(v3d.object_active[:3]) + (1.0,),
            tuple(v3d.object_selected[:3]) + (1.0,),
            tuple(ui.axis_x[:3]) + (1.0,),
            tuple(ui.axis_y[:3]) + (1.0,),
            tuple(ui.axis_z[:3]) + (1.0,),
            tuple(ui.wcol_regular.inner[:3]) + (1.0,),
            tuple(ui.wcol_tool.inner[:3]) + (1.0,),
            tuple(v3d.space.gradients.high_gradient[:3]) + (1.0,),
        ]
    except Exception:
        return [(0.8, 0.8, 0.8, 1.0)] * 8


# ===========================================================================
# Enum callback
# ===========================================================================

# Module-level cache: Prevents Blender from reading freed memory in dynamic enums.
_PALETTE_ENUM_ITEMS_CACHE = []


def get_palette_items(self, context):
    global _PALETTE_ENUM_ITEMS_CACHE
    items = [(k, k, f"Built-in palette: {k}") for k in BUILTIN_PALETTES]
    items.append(("THEME", "Current Theme", "Extract colors from the active Blender theme"))
    try:
        prefs = context.preferences.addons[__name__].preferences
        for entry in prefs.saved_palettes:
            key = f"SAVED::{entry.name}"
            items.append((key, f"[S] {entry.name}", f"Saved palette: {entry.name}"))
    except (KeyError, AttributeError):
        pass
    items.append(("CUSTOM", "Custom", "Use the custom palette defined below"))
    _PALETTE_ENUM_ITEMS_CACHE = items
    return _PALETTE_ENUM_ITEMS_CACHE


def get_active_palette_colors(settings, context=None):
    name = settings.palette_name
    if name == "CUSTOM":
        return [tuple(item.color) for item in settings.custom_colors] or [(0.8, 0.8, 0.8, 1.0)]
    if name == "THEME" and context:
        return get_theme_palette_colors(context)
    if name.startswith("SAVED::") and context:
        saved_name = name[7:]
        try:
            prefs = context.preferences.addons[__name__].preferences
            for entry in prefs.saved_palettes:
                if entry.name == saved_name:
                    _, colors = dict_to_palette(json.loads(entry.json_data))
                    return colors
        except Exception:
            pass
    return BUILTIN_PALETTES.get(name, [(0.8, 0.8, 0.8, 1.0)])


# ===========================================================================
# Add-on preferences: Store the saved palette library
# ===========================================================================

class SavedPaletteEntry(PropertyGroup):
    name: StringProperty(name="Name", default="Unnamed")
    json_data: StringProperty(name="JSON", default="{}")


class PaletteColorizerPreferences(AddonPreferences):
    bl_idname = __name__

    saved_palettes: CollectionProperty(type=SavedPaletteEntry)
    saved_palette_index: IntProperty(default=0)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Saved Palette Library", icon='COLORSET_01_VEC')
        row = layout.row()
        row.template_list(
            "PALETTE_UL_saved", "",
            self, "saved_palettes",
            self, "saved_palette_index",
            rows=5,
        )
        col = row.column(align=True)
        col.operator("palette.library_remove", icon='REMOVE', text="")


# ===========================================================================
# Property groups
# ===========================================================================

class PaletteColorItem(PropertyGroup):
    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,
        min=0.0, max=1.0,
        default=(0.8, 0.8, 0.8, 1.0),
    )


class PaletteColorizerSettings(PropertyGroup):
    palette_name: EnumProperty(
        name="Palette",
        items=get_palette_items,
        description="Select a built-in, theme, saved, or custom palette",
    )
    custom_colors: CollectionProperty(type=PaletteColorItem)
    custom_color_index: IntProperty(default=0)
    custom_palette_name: StringProperty(
        name="Palette Name",
        default="My Palette",
        description="Name used when you save or export this custom palette",
    )
    assignment_mode: EnumProperty(
        name="Assignment",
        items=[
            ("SEQUENTIAL", "Sequential", "Assign colors in palette order"),
            ("RANDOM", "Random", "Assign colors randomly from palette"),
            ("BY_NAME", "By Name Hash", "Stable color based on object name"),
        ],
        default="SEQUENTIAL",
    )
    affect: EnumProperty(
        name="Affect",
        items=[
            ("SELECTED", "Selected Objects", "Only selected objects"),
            ("ALL", "All Scene Objects", "Every object in the scene"),
            ("VISIBLE", "Visible Objects", "Only visible objects"),
        ],
        default="SELECTED",
    )
    auto_switch_shading: BoolProperty(
        name="Auto-switch Viewport Shading",
        description="Automatically set active viewport to Object color mode",
        default=True,
    )
    preserve_alpha: BoolProperty(
        name="Preserve Existing Alpha",
        description="Keep the current alpha value of each object",
        default=False,
    )
    randomize_seed: IntProperty(
        name="Random Seed",
        default=1,
        min=1,
        max=9999,
        description="Seed value for random color assignment",
    )
    apply_to_material: BoolProperty(
        name="Also Apply to Materials",
        description=(
            "Create or update a Principled BSDF material on each object "
            "so colors render in Cycles and EEVEE"
        ),
        default=False,
    )
    paste_buffer: StringProperty(
        name="Paste String",
        description="Paste a palette share string here, then select Import String",
        default="",
    )


# ===========================================================================
# Object helpers
# ===========================================================================

def name_to_color_index(name, palette_len):
    h = 0
    for ch in name:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return h % palette_len


def get_target_objects(settings, context):
    if settings.affect == "SELECTED":
        return [o for o in context.selected_objects if o.type == 'MESH']
    elif settings.affect == "ALL":
        return [o for o in context.scene.objects if o.type == 'MESH']
    else:
        return [o for o in context.visible_objects if o.type == 'MESH']


def switch_viewport_shading(context, color_type="OBJECT"):
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.color_type = color_type
            break


# ===========================================================================
# Material helpers
# ===========================================================================

def get_or_create_palette_material(obj, r, g, b):
    """
    Find existing palette material on first slot, or create new material.
    Set the Principled BSDF Base Color and return the material.
    """
    PALETTE_MAT_PREFIX = "PC_"

    mat = None
    if obj.data.materials and obj.data.materials[0] and \
            obj.data.materials[0].name.startswith(PALETTE_MAT_PREFIX):
        mat = obj.data.materials[0]
    else:
        mat_name = f"{PALETTE_MAT_PREFIX}{obj.name}"
        mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

    mat.use_nodes = True

    bsdf = next(
        (n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'),
        None,
    )
    if bsdf is None:
        bsdf = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')

    bsdf.inputs['Base Color'].default_value = (r, g, b, 1.0)
    return mat


# ===========================================================================
# Core operators
# ===========================================================================

class PALETTE_OT_apply_colors(Operator):
    bl_idname = "palette.apply_colors"
    bl_label = "Apply Palette"
    bl_description = "Assign palette colors to target objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.palette_colorizer
        palette = get_active_palette_colors(settings, context)
        objects = get_target_objects(settings, context)
        if not objects:
            self.report({'WARNING'}, "No valid mesh objects found.")
            return {'CANCELLED'}
        if not palette:
            self.report({'WARNING'}, "Palette is empty.")
            return {'CANCELLED'}
        rng = random.Random(settings.randomize_seed)
        for i, obj in enumerate(objects):
            if settings.assignment_mode == "SEQUENTIAL":
                idx = i % len(palette)
            elif settings.assignment_mode == "RANDOM":
                idx = rng.randint(0, len(palette) - 1)
            else:
                idx = name_to_color_index(obj.name, len(palette))
            r, g, b, a = palette[idx]
            if settings.preserve_alpha:
                a = obj.color[3]
            obj.color = (r, g, b, a)
            if settings.apply_to_material:
                get_or_create_palette_material(obj, r, g, b)
        if settings.auto_switch_shading:
            switch_viewport_shading(context, "OBJECT")
        self.report({'INFO'}, f"Applied '{settings.palette_name}' to {len(objects)} object(s).")
        return {'FINISHED'}


class PALETTE_OT_reset_colors(Operator):
    bl_idname = "palette.reset_colors"
    bl_label = "Reset to White"
    bl_description = "Reset obj.color to white for target objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.palette_colorizer
        objects = get_target_objects(settings, context)
        for obj in objects:
            obj.color = (1.0, 1.0, 1.0, 1.0)
        self.report({'INFO'}, f"Reset {len(objects)} object(s) to white.")
        return {'FINISHED'}


class PALETTE_OT_apply_materials(Operator):
    bl_idname = "palette.apply_materials"
    bl_label = "Apply Materials"
    bl_description = (
        "Assign palette colors to Principled BSDF materials on target objects "
        "for Cycles and EEVEE renders"
    )
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.palette_colorizer
        palette = get_active_palette_colors(settings, context)
        objects = get_target_objects(settings, context)

        if not objects:
            self.report({'WARNING'}, "No valid mesh objects found.")
            return {'CANCELLED'}
        if not palette:
            self.report({'WARNING'}, "Palette is empty.")
            return {'CANCELLED'}

        rng = random.Random(settings.randomize_seed)
        for i, obj in enumerate(objects):
            if settings.assignment_mode == "SEQUENTIAL":
                idx = i % len(palette)
            elif settings.assignment_mode == "RANDOM":
                idx = rng.randint(0, len(palette) - 1)
            else:
                idx = name_to_color_index(obj.name, len(palette))

            r, g, b, a = palette[idx]
            get_or_create_palette_material(obj, r, g, b)

        self.report({'INFO'}, f"Applied materials to {len(objects)} object(s).")
        return {'FINISHED'}


class PALETTE_OT_clear_materials(Operator):
    bl_idname = "palette.clear_materials"
    bl_label = "Clear Materials"
    bl_description = "Remove temporary palette materials from target objects"
    bl_options = {'REGISTER', 'UNDO'}

    only_palette: BoolProperty(
        name="Only Palette Materials",
        description="Only remove materials created by Palette Colorizer (PC_*)",
        default=True,
    )

    def execute(self, context):
        settings = context.scene.palette_colorizer
        objects = get_target_objects(settings, context)
        if not objects:
            self.report({'WARNING'}, "No valid mesh objects found.")
            return {'CANCELLED'}

        removed_count = 0
        palette_mats = set()
        for obj in objects:
            if not obj.data or not hasattr(obj.data, "materials"):
                continue
            for i in reversed(range(len(obj.data.materials))):
                mat = obj.data.materials[i]
                if mat:
                    if self.only_palette and not mat.name.startswith("PC_"):
                        continue
                    palette_mats.add(mat)
                    obj.data.materials.pop(index=i)
                    removed_count += 1

        for mat in palette_mats:
            if mat.users == 0:
                bpy.data.materials.remove(mat)

        self.report({'INFO'}, f"Removed {removed_count} material slot(s) across {len(objects)} object(s).")
        return {'FINISHED'}


# ===========================================================================
# Custom palette edit operators
# ===========================================================================

class PALETTE_OT_add_custom_color(Operator):
    bl_idname = "palette.add_custom_color"
    bl_label = "Add Color"
    bl_description = "Add a new color slot to the custom palette"

    def execute(self, context):
        settings = context.scene.palette_colorizer
        item = settings.custom_colors.add()
        item.color = (random.random(), random.random(), random.random(), 1.0)
        settings.custom_color_index = len(settings.custom_colors) - 1
        return {'FINISHED'}


class PALETTE_OT_remove_custom_color(Operator):
    bl_idname = "palette.remove_custom_color"
    bl_label = "Remove Color"
    bl_description = "Remove the selected color slot from the custom palette"

    def execute(self, context):
        settings = context.scene.palette_colorizer
        idx = settings.custom_color_index
        if 0 <= idx < len(settings.custom_colors):
            settings.custom_colors.remove(idx)
            settings.custom_color_index = max(0, idx - 1)
        return {'FINISHED'}


class PALETTE_OT_randomize_custom(Operator):
    bl_idname = "palette.randomize_custom"
    bl_label = "Generate Hues"
    bl_description = "Fill custom palette with evenly distributed hues"

    count: IntProperty(name="Count", default=8, min=2, max=32)

    def execute(self, context):
        settings = context.scene.palette_colorizer
        settings.custom_colors.clear()
        for i in range(self.count):
            r, g, b = colorsys.hsv_to_rgb(i / self.count, 0.75, 0.90)
            item = settings.custom_colors.add()
            item.color = (r, g, b, 1.0)
        settings.custom_color_index = 0
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class PALETTE_OT_randomize_seed(Operator):
    bl_idname = "palette.randomize_seed"
    bl_label = "Randomize Seed"
    bl_description = "Select a random seed between 1 and 9999"

    def execute(self, context):
        # Pick digit count with equal probability so 1, 2, 3, and 4 digits are not biased
        digits = random.randint(1, 4)
        min_val = 1 if digits == 1 else 10 ** (digits - 1)
        max_val = 10 ** digits - 1
        context.scene.palette_colorizer.randomize_seed = random.randint(min_val, max_val)
        return {'FINISHED'}


# ===========================================================================
# Share: Copy and Paste string (uses Blender clipboard)
# ===========================================================================

class PALETTE_OT_copy_string(Operator):
    bl_idname = "palette.copy_string"
    bl_label = "Copy Share String"
    bl_description = (
        "Encode active palette as a compact JSON string and copy to clipboard. "
        "Paste anywhere: Discord, forums, or chat."
    )

    def execute(self, context):
        settings = context.scene.palette_colorizer
        colors = get_active_palette_colors(settings, context)
        name = (
            settings.custom_palette_name
            if settings.palette_name == "CUSTOM"
            else settings.palette_name
        )
        share_str = json.dumps(palette_to_dict(name, colors), separators=(',', ':'))
        context.window_manager.clipboard = share_str
        self.report({'INFO'}, f"Copied '{name}' ({len(colors)} colors) to clipboard.")
        return {'FINISHED'}


class PALETTE_OT_paste_string(Operator):
    bl_idname = "palette.paste_string"
    bl_label = "Import Pasted String"
    bl_description = (
        "Parse the palette string from the Paste field or clipboard. "
        "Load it into the Custom palette and select Custom mode."
    )

    def execute(self, context):
        settings = context.scene.palette_colorizer
        raw = settings.paste_buffer.strip() or context.window_manager.clipboard.strip()
        if not raw:
            self.report({'WARNING'}, "Paste String field and clipboard are both empty.")
            return {'CANCELLED'}
        try:
            name, colors = dict_to_palette(json.loads(raw))
        except (json.JSONDecodeError, ValueError) as e:
            self.report({'ERROR'}, f"Invalid palette string: {e}")
            return {'CANCELLED'}
        load_colors_into_custom(settings, colors)
        settings.custom_palette_name = name
        settings.palette_name = "CUSTOM"
        settings.paste_buffer = ""
        self.report({'INFO'}, f"Loaded '{name}' ({len(colors)} colors).")
        return {'FINISHED'}


# ===========================================================================
# Share: Export and Import JSON file
# ===========================================================================

class PALETTE_OT_export_json(Operator, ExportHelper):
    bl_idname = "palette.export_json"
    bl_label = "Export Palette (.json)"
    bl_description = "Save the active palette to a JSON file"

    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})

    def execute(self, context):
        settings = context.scene.palette_colorizer
        colors = get_active_palette_colors(settings, context)
        name = (
            settings.custom_palette_name
            if settings.palette_name == "CUSTOM"
            else settings.palette_name
        )
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(palette_to_dict(name, colors), f, indent=2)
        except OSError as e:
            self.report({'ERROR'}, f"Could not write file: {e}")
            return {'CANCELLED'}
        self.report({'INFO'}, f"Exported '{name}' to {self.filepath}")
        return {'FINISHED'}


class PALETTE_OT_import_json(Operator, ImportHelper):
    bl_idname = "palette.import_json"
    bl_label = "Import Palette (.json)"
    bl_description = "Load a JSON palette file into the Custom palette slot"

    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})

    def execute(self, context):
        settings = context.scene.palette_colorizer
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                name, colors = dict_to_palette(json.load(f))
        except (OSError, json.JSONDecodeError, ValueError) as e:
            self.report({'ERROR'}, f"Failed to import: {e}")
            return {'CANCELLED'}
        load_colors_into_custom(settings, colors)
        settings.custom_palette_name = name
        settings.palette_name = "CUSTOM"
        self.report({'INFO'}, f"Imported '{name}' ({len(colors)} colors).")
        return {'FINISHED'}


# ===========================================================================
# Library: save, load, remove (stored in add-on preferences)
# ===========================================================================

class PALETTE_OT_library_save(Operator):
    bl_idname = "palette.library_save"
    bl_label = "Save to Library"
    bl_description = (
        "Save the active Custom palette to the add-on library. "
        "Library palettes persist across blend files."
    )

    def execute(self, context):
        settings = context.scene.palette_colorizer
        if settings.palette_name != "CUSTOM":
            self.report({'WARNING'}, "Switch to Custom palette first before saving to library.")
            return {'CANCELLED'}
        colors = get_active_palette_colors(settings, context)
        name = settings.custom_palette_name.strip() or "Unnamed"
        data_str = json.dumps(palette_to_dict(name, colors))
        prefs = context.preferences.addons[__name__].preferences
        for entry in prefs.saved_palettes:
            if entry.name == name:
                entry.json_data = data_str
                self.report({'INFO'}, f"Updated '{name}' in library.")
                return {'FINISHED'}
        entry = prefs.saved_palettes.add()
        entry.name = name
        entry.json_data = data_str
        prefs.saved_palette_index = len(prefs.saved_palettes) - 1
        self.report({'INFO'}, f"Saved '{name}' to library.")
        return {'FINISHED'}


class PALETTE_OT_library_load(Operator):
    bl_idname = "palette.library_load"
    bl_label = "Load"
    bl_description = "Load this library palette into the Custom slot"

    index: IntProperty(default=0)

    def execute(self, context):
        settings = context.scene.palette_colorizer
        prefs = context.preferences.addons[__name__].preferences
        if not prefs.saved_palettes or not (0 <= self.index < len(prefs.saved_palettes)):
            self.report({'WARNING'}, "Invalid library index.")
            return {'CANCELLED'}
        entry = prefs.saved_palettes[self.index]
        try:
            name, colors = dict_to_palette(json.loads(entry.json_data))
        except (json.JSONDecodeError, ValueError) as e:
            self.report({'ERROR'}, f"Corrupt library entry: {e}")
            return {'CANCELLED'}
        load_colors_into_custom(settings, colors)
        settings.custom_palette_name = name
        settings.palette_name = "CUSTOM"
        self.report({'INFO'}, f"Loaded '{name}' from library.")
        return {'FINISHED'}


class PALETTE_OT_library_remove(Operator):
    bl_idname = "palette.library_remove"
    bl_label = "Remove"
    bl_description = "Remove the selected palette from the library"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        idx = prefs.saved_palette_index
        if 0 <= idx < len(prefs.saved_palettes):
            name = prefs.saved_palettes[idx].name
            prefs.saved_palettes.remove(idx)
            prefs.saved_palette_index = max(0, idx - 1)
            self.report({'INFO'}, f"Removed '{name}' from library.")
        return {'FINISHED'}


# ===========================================================================
# UI Lists
# ===========================================================================

class PALETTE_UL_colors(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "color", text=f"Color {index + 1}")


class PALETTE_UL_saved(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.name, icon='COLORSET_01_VEC')
        op = row.operator("palette.library_load", text="", icon='IMPORT')
        op.index = index


# ===========================================================================
# Panels
# ===========================================================================

class PALETTE_PT_main(Panel):
    bl_label = "Palette Colorizer"
    bl_idname = "PALETTE_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Palette"
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        settings = context.scene.palette_colorizer

        box = layout.box()
        box.label(text="Palette", icon='COLOR')
        box.prop(settings, "palette_name", text="")

        if settings.palette_name == "CUSTOM":
            box.prop(settings, "custom_palette_name", text="Name")
            row = box.row()
            row.template_list(
                "PALETTE_UL_colors", "",
                settings, "custom_colors",
                settings, "custom_color_index",
                rows=4,
            )
            col = row.column(align=True)
            col.operator("palette.add_custom_color", icon='ADD', text="")
            col.operator("palette.remove_custom_color", icon='REMOVE', text="")
            col.separator()
            col.operator("palette.randomize_custom", icon='LOOP_FORWARDS', text="")

        box = layout.box()
        box.label(text="Assignment", icon='PRESET')
        box.prop(settings, "assignment_mode", text="Mode")
        if settings.assignment_mode == "RANDOM":
            row = box.row(align=True)
            row.prop(settings, "randomize_seed")
            row.operator("palette.randomize_seed", icon='FILE_REFRESH', text="")

        box = layout.box()
        box.label(text="Target", icon='OBJECT_DATA')
        box.prop(settings, "affect", text="Objects")
        box.prop(settings, "auto_switch_shading")
        box.prop(settings, "preserve_alpha")
        box.prop(settings, "apply_to_material")

        layout.separator()
        row = layout.row(align=True)
        row.scale_y = 1.4
        row.operator("palette.apply_colors", icon='PLAY', text="Apply Palette")
        row.operator("palette.reset_colors", icon='LOOP_BACK', text="Reset")

        row = layout.row(align=True)
        row.scale_y = 1.2
        row.operator("palette.apply_materials", icon='MATERIAL', text="Apply Materials")
        row.operator("palette.clear_materials", icon='TRASH', text="Clear Materials")


class PALETTE_PT_share(Panel):
    bl_label = "Share Palettes"
    bl_idname = "PALETTE_PT_share"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Palette"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 2

    def draw(self, context):
        layout = self.layout
        settings = context.scene.palette_colorizer

        # Clipboard string
        box = layout.box()
        box.label(text="Share String", icon='COPYDOWN')
        box.label(text="Copy or paste in Discord, forums, or chat", icon='INFO')
        box.operator("palette.copy_string", icon='COPYDOWN', text="Copy Active Palette as String")
        box.separator()
        box.label(text="Paste a received string here:")
        box.prop(settings, "paste_buffer", text="")
        box.operator("palette.paste_string", icon='PASTEDOWN', text="Import Pasted String")

        # JSON file
        box = layout.box()
        box.label(text="JSON File", icon='FILE')
        row = box.row(align=True)
        row.operator("palette.export_json", icon='EXPORT', text="Export .json")
        row.operator("palette.import_json", icon='IMPORT', text="Import .json")

        # Local library
        box = layout.box()
        box.label(text="My Library", icon='BOOKMARKS')
        box.label(text="Persists across blend files", icon='INFO')

        try:
            prefs = context.preferences.addons[__name__].preferences
            if prefs.saved_palettes:
                row = box.row()
                row.template_list(
                    "PALETTE_UL_saved", "",
                    prefs, "saved_palettes",
                    prefs, "saved_palette_index",
                    rows=3,
                )
                col = row.column(align=True)
                col.operator("palette.library_remove", icon='REMOVE', text="")
            else:
                box.label(text="No saved palettes yet.", icon='GHOST_DISABLED')
        except (KeyError, AttributeError):
            box.label(text="Enable add-on to use library.", icon='ERROR')

        box.operator(
            "palette.library_save", icon='FILE_TICK',
            text="Save Custom Palette to Library"
        )


# ===========================================================================
# Registration
# ===========================================================================

classes = (
    SavedPaletteEntry,
    PaletteColorItem,
    PaletteColorizerPreferences,
    PaletteColorizerSettings,
    PALETTE_UL_colors,
    PALETTE_UL_saved,
    PALETTE_OT_apply_colors,
    PALETTE_OT_reset_colors,
    PALETTE_OT_apply_materials,
    PALETTE_OT_clear_materials,
    PALETTE_OT_add_custom_color,
    PALETTE_OT_remove_custom_color,
    PALETTE_OT_randomize_custom,
    PALETTE_OT_randomize_seed,
    PALETTE_OT_copy_string,
    PALETTE_OT_paste_string,
    PALETTE_OT_export_json,
    PALETTE_OT_import_json,
    PALETTE_OT_library_save,
    PALETTE_OT_library_load,
    PALETTE_OT_library_remove,
    PALETTE_PT_main,
    PALETTE_PT_share,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.palette_colorizer = bpy.props.PointerProperty(
        type=PaletteColorizerSettings
    )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.palette_colorizer


if __name__ == "__main__":
    register()