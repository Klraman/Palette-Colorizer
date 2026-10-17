"""
User interface panels, UILists, custom sidebar tab icons, and native color swatch strip.
"""

import os
import bpy
import bpy.utils.previews
from bpy.types import Panel, UIList

from .palettes import get_addon_id, get_active_palette_colors
from .operators import get_target_objects

_preview_collections = {}

def load_custom_icons():
    """Load the compact sidebar tab thumbnail icon."""
    global _preview_collections
    if "main" in _preview_collections:
        return _preview_collections["main"]

    pcoll = bpy.utils.previews.new()
    candidates = [
        os.path.join(os.path.dirname(__file__), "icons", "thumbnail.png"),
        os.path.join(os.path.dirname(__file__), "Astra Assets", "previews", "01-thumbnail.png"),
    ]

    for p in candidates:
        if os.path.exists(p):
            try:
                thumb = pcoll.load("thumbnail", p, 'IMAGE')
                _ = thumb.icon_pixels[0]
            except Exception:
                pass
            break

    _preview_collections["main"] = pcoll
    return pcoll

def unload_custom_icons():
    """Remove all custom preview collections on unregister."""
    global _preview_collections
    for pcoll in _preview_collections.values():
        try:
            bpy.utils.previews.remove(pcoll)
        except Exception:
            pass
    _preview_collections.clear()

def draw_equal_swatch_strip(layout, items_and_props):
    """Draw color swatches with equal widths and no right-edge clipping on resize."""
    total = len(items_and_props)
    if total == 0:
        return

    row = layout.row(align=True)
    row.scale_y = 1.15
    row.scale_x = 0.1

    if total == 8:
        half_l = row.split(factor=0.5, align=True)
        half_r = half_l.split(factor=1.0, align=True)

        q1 = half_l.split(factor=0.5, align=True)
        q2 = q1.split(factor=1.0, align=True)
        q3 = half_r.split(factor=0.5, align=True)
        q4 = q3.split(factor=1.0, align=True)

        s0 = q1.split(factor=0.5, align=True)
        s0.prop(items_and_props[0][0], items_and_props[0][1], text="")
        s0.prop(items_and_props[1][0], items_and_props[1][1], text="")

        s1 = q2.split(factor=0.5, align=True)
        s1.prop(items_and_props[2][0], items_and_props[2][1], text="")
        s1.prop(items_and_props[3][0], items_and_props[3][1], text="")

        s2 = q3.split(factor=0.5, align=True)
        s2.prop(items_and_props[4][0], items_and_props[4][1], text="")
        s2.prop(items_and_props[5][0], items_and_props[5][1], text="")

        s3 = q4.split(factor=0.5, align=True)
        s3.prop(items_and_props[6][0], items_and_props[6][1], text="")
        s3.prop(items_and_props[7][0], items_and_props[7][1], text="")
        return

    curr = row
    for idx, (data_obj, prop_name) in enumerate(items_and_props):
        remaining = total - idx
        if remaining > 1:
            split = curr.split(factor=1.0 / remaining, align=True)
            split.prop(data_obj, prop_name, text="")
            curr = split
        else:
            curr.prop(data_obj, prop_name, text="")

class PALETTE_UL_colors(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.prop(item, "color", text=f"Swatch {index + 1}")

class PALETTE_UL_saved(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.name, icon='COLORSET_01_VEC')
        op = row.operator("palette.library_load", text="", icon='IMPORT')
        op.index = index

class PALETTE_PT_main(Panel):
    bl_label = "Palette Colorizer"
    bl_idname = "PALETTE_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Palette"
    bl_order = 1

    def draw_header_preset(self, context):
        layout = self.layout
        addon_id = get_addon_id()
        show_btn = True
        has_update = False
        try:
            prefs = context.preferences.addons[addon_id].preferences
            show_btn = prefs.show_sidebar_prefs_button
            has_update = bool(prefs.update_msg)
        except Exception:
            pass
        if show_btn:
            icon = 'FILE_REFRESH' if has_update else 'PREFERENCES'
            layout.operator("palette.open_preferences", text="", icon=icon, emboss=False)

    def draw(self, context):
        layout = self.layout
        settings = context.scene.palette_colorizer

        col = layout.column(align=True)
        top_row = col.row(align=True)
        top_row.prop(settings, "palette_name", text="")
        if settings.palette_name != "CUSTOM":
            top_row.operator("palette.copy_to_custom", text="", icon='DUPLICATE')
        top_row.operator("palette.library_save", text="", icon='BOOKMARKS')
        top_row.prop(settings, "auto_apply", text="", icon='PLAY' if settings.auto_apply else 'PAUSE')

        palette_colors = get_active_palette_colors(settings, context)
        if settings.palette_name == "CUSTOM" and len(settings.custom_colors) > 0:
            swatch_pairs = [(item, "color") for item in settings.custom_colors[:16]]
        else:
            count = min(8, len(palette_colors))
            swatch_pairs = [(settings, f"swatch_{i}") for i in range(count)]
        draw_equal_swatch_strip(col, swatch_pairs)

        if settings.palette_name == "CUSTOM":
            cbox = layout.box()
            cbox.prop(settings, "custom_palette_name", text="Name")
            row = cbox.row()
            row.template_list(
                "PALETTE_UL_colors",
                "",
                settings,
                "custom_colors",
                settings,
                "custom_color_index",
                rows=4,
            )
            bcol = row.column(align=True)
            bcol.operator("palette.add_custom_color", icon='ADD', text="")
            bcol.operator("palette.remove_custom_color", icon='REMOVE', text="")
            bcol.separator()
            bcol.operator("palette.randomize_custom", icon='COLOR', text="")

            img_row = cbox.row(align=True)
            img_row.prop(settings, "source_image", text="")
            img_row.operator("palette.sample_image_colors", text="Sample Image", icon='IMAGE_DATA')

        layout.separator(factor=0.5)

        form = layout.column(align=True)
        form.use_property_split = True
        form.use_property_decorate = False

        out_row = form.row(align=True)
        out_row.prop(settings, "output_mode", expand=True)

        dist_row = form.row(align=True)
        dist_row.prop(settings, "assignment_mode", expand=True)

        if settings.assignment_mode == "RANDOM":
            seed_split = form.split(factor=0.4, align=True)
            lbl_row = seed_split.row()
            lbl_row.alignment = 'RIGHT'
            lbl_row.label(text="Seed")
            ctrl_row = seed_split.row(align=True)
            s_prev = ctrl_row.operator("palette.step_seed", text="", icon='TRIA_LEFT')
            s_prev.step = -1
            ctrl_row.prop(settings, "randomize_seed", text="")
            s_next = ctrl_row.operator("palette.step_seed", text="", icon='TRIA_RIGHT')
            s_next.step = 1
            ctrl_row.operator("palette.randomize_seed", icon='FILE_REFRESH', text="")
            if settings.grouping_mode == "OBJECT":
                form.prop(settings, "avoid_adjacent_duplicates")

        form.separator(factor=0.5)
        scope_row = form.row(align=True)
        scope_row.prop(settings, "affect", expand=True)
        form.prop(settings, "grouping_mode")

        target_objs = get_target_objects(settings, context)
        locked_count = sum(1 for o in target_objs if o.get("pc_locked", False))
        lock_row = layout.row(align=True)
        lock_row.operator("palette.lock_selected", text="Pin Selected", icon='LOCKED')
        lock_text = f"Unpin ({locked_count})" if locked_count > 0 else "Unpin Selected"
        lock_row.operator("palette.unlock_selected", text=lock_text, icon='UNLOCKED')

        layout.separator(factor=0.5)
        act_row = layout.row(align=True)
        act_row.scale_y = 1.4
        act_row.operator("palette.apply_colors", icon='PLAY', text="Apply Palette")
        act_row.operator("palette.reset_colors", icon='LOOP_BACK', text="Reset")

class PALETTE_PT_materials(Panel):
    bl_label = "Showcase Materials"
    bl_idname = "PALETTE_PT_materials"
    bl_parent_id = "PALETTE_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Palette"
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        settings = context.scene.palette_colorizer

        col = layout.column(align=True)
        col.use_property_split = True
        col.use_property_decorate = False

        col.prop(settings, "material_mode", text="Architecture")
        col.separator(factor=0.5)
        col.prop(settings, "mat_roughness", slider=True)
        col.prop(settings, "mat_metallic", slider=True)
        col.prop(settings, "mat_specular", slider=True)
        col.separator(factor=0.5)
        col.prop(settings, "protect_real_materials")

        mat_row = layout.row(align=True)
        mat_row.scale_y = 1.2
        mat_row.operator("palette.apply_materials", icon='MATERIAL', text="Assign Materials")
        mat_row.operator("palette.clear_materials", icon='TRASH', text="Clear Materials")

class PALETTE_PT_options(Panel):
    bl_label = "Viewport Options"
    bl_idname = "PALETTE_PT_options"
    bl_parent_id = "PALETTE_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Palette"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 2

    def draw(self, context):
        layout = self.layout
        settings = context.scene.palette_colorizer
        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(settings, "include_non_mesh")
        col.prop(settings, "auto_switch_shading")
        col.prop(settings, "preserve_alpha")

class PALETTE_PT_share(Panel):
    bl_label = "Share & Library"
    bl_idname = "PALETTE_PT_share"
    bl_parent_id = "PALETTE_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Palette"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 3

    def draw(self, context):
        layout = self.layout
        settings = context.scene.palette_colorizer
        addon_id = get_addon_id()

        box = layout.box()
        box.label(text="Share String (Discord / Chat)", icon='COPYDOWN')
        box.operator("palette.copy_string", icon='COPYDOWN', text="Copy Active Palette String")
        row = box.row(align=True)
        row.prop(settings, "paste_buffer", text="")
        row.operator("palette.paste_string", icon='PASTEDOWN', text="Import")

        box = layout.box()
        box.label(text="JSON File", icon='FILE')
        row = box.row(align=True)
        row.operator("palette.export_json", icon='EXPORT', text="Export .json")
        row.operator("palette.import_json", icon='IMPORT', text="Import .json")

        box = layout.box()
        box.label(text="My Library", icon='BOOKMARKS')
        try:
            prefs = context.preferences.addons[addon_id].preferences
            if prefs.saved_palettes:
                row = box.row()
                row.template_list(
                    "PALETTE_UL_saved",
                    "",
                    prefs,
                    "saved_palettes",
                    prefs,
                    "saved_palette_index",
                    rows=3,
                )
                col = row.column(align=True)
                col.operator("palette.library_remove", icon='REMOVE', text="")
            else:
                box.label(text="No saved palettes yet.", icon='INFO')
        except (KeyError, AttributeError):
            box.label(text="Enable add-on to use library.", icon='ERROR')

        box.operator("palette.library_save", icon='FILE_TICK', text="Save Active Palette to Library")

PANEL_CLASSES = (
    PALETTE_PT_main,
    PALETTE_PT_materials,
    PALETTE_PT_options,
    PALETTE_PT_share,
)

def update_panel_icons(icon_id):
    """Assign custom icon ID to top-level panels for compact sidebar mode."""
    if icon_id:
        PALETTE_PT_main.bl_icon_value = icon_id
