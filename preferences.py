"""
Add-on Preferences with MESHmachine-style update installer and saved palette library.
"""

import os
import bpy
from bpy.props import (
    StringProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
    CollectionProperty,
)
from bpy.types import AddonPreferences

from .palettes import get_addon_id
from .properties import SavedPaletteEntry
from .updater import get_update_files, stage_update_zip

class PaletteColorizerPreferences(AddonPreferences):
    bl_idname = get_addon_id()

    saved_palettes: CollectionProperty(type=SavedPaletteEntry)
    saved_palette_index: IntProperty(default=0)

    show_sidebar_prefs_button: BoolProperty(
        name="Show Preferences Button in Sidebar Header",
        description="Display a quick-access Preferences gear button in the 3D Viewport Palette panel header",
        default=True,
    )

    def update_update_path(self, context):
        if self.avoid_update:
            self.avoid_update = False
            return

        if self.update_path:
            abs_path = bpy.path.abspath(self.update_path)
            if os.path.exists(abs_path) and abs_path.lower().endswith(".zip"):
                ok, msg = stage_update_zip(abs_path)
                self.update_msg = msg if ok else ""
            self.avoid_update = True
            self.update_path = ""

    def update_show_update(self, context):
        if self.show_update:
            get_update_files(force=True)

    update_path: StringProperty(
        name="Update File Path",
        description="Select a Palette Colorizer .zip archive to stage an update",
        subtype='FILE_PATH',
        default="",
        update=update_update_path,
    )
    update_msg: StringProperty(name="Update Message", default="")
    show_update: BoolProperty(
        name="Install Palette Colorizer Update",
        default=False,
        update=update_show_update,
    )
    avoid_update: BoolProperty(default=False)

    tabs: EnumProperty(
        name="Tabs",
        items=[
            ("GENERAL", "General", "General add-on settings and update manager"),
            ("LIBRARY", "Saved Library", "Manage saved palettes that persist across blend files"),
            ("ABOUT", "About", "Version and documentation links"),
        ],
        default="GENERAL",
    )

    def draw(self, context):
        layout = self.layout
        self.draw_update(layout)

        col = layout.column(align=True)
        row = col.row()
        row.prop(self, "tabs", expand=True)

        box = col.box()
        if self.tabs == "GENERAL":
            self.draw_general_tab(box)
        elif self.tabs == "LIBRARY":
            self.draw_library_tab(box)
        elif self.tabs == "ABOUT":
            self.draw_about_tab(box)

    def draw_update(self, layout):
        col = layout.column(align=True)
        row = col.row()
        row.scale_y = 1.25
        row.prop(
            self,
            "show_update",
            text="Install Palette Colorizer Update",
            icon='TRIA_DOWN' if self.show_update else 'TRIA_RIGHT',
        )

        if not self.show_update:
            return

        update_files = get_update_files()
        box = layout.box()

        if self.update_msg:
            row = box.row(align=True)
            row.scale_y = 1.4
            row.label(text=self.update_msg, icon='FILE_TICK')

            act_row = box.row(align=True)
            act_row.scale_y = 1.3
            act_row.operator("palette.remove_update", text="Remove Update", icon='CANCEL')
            act_row.operator("palette.install_update_now", text="Install Update & Reload", icon='FILE_REFRESH')
            act_row.operator("wm.quit_blender", text="Quit Blender + Install Update", icon='QUIT')
        else:
            sub = box.box()
            scol = sub.column(align=True)
            header = scol.row()
            header.alignment = 'LEFT'

            if update_files:
                header.label(text="Found Updates in Home or Downloads folder:")
                header.operator("palette.rescan_updates", text="Re-Scan", icon='FILE_REFRESH')
                scol.separator()

                for path, ver_str, _ in update_files:
                    item_row = scol.row(align=True)
                    item_row.alignment = 'LEFT'
                    op = item_row.operator(
                        "palette.use_update",
                        text=f"Use Palette Colorizer {ver_str}",
                        icon='IMPORT',
                    )
                    op.path = path
                    op.tail = ver_str

                    path_sub = item_row.row()
                    path_sub.active = False
                    path_sub.label(text=path)
            else:
                header.label(text="No update zip found in your Home or Downloads folder.")
                header.operator("palette.rescan_updates", text="Re-Scan", icon='FILE_REFRESH')

            pick_row = box.row(align=True)
            split = pick_row.split(factor=0.45, align=True)
            split.prop(self, "update_path", text="")
            hint = "Select palette_colorizer.zip file"
            if update_files:
                hint += " or pick a detected file above"
            split.label(text=hint)

    def draw_general_tab(self, box):
        col = box.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(self, "show_sidebar_prefs_button")

    def draw_library_tab(self, box):
        box.label(text="Saved Palette Library (Persists Across Blend Files)", icon='BOOKMARKS')
        if self.saved_palettes:
            row = box.row()
            row.template_list(
                "PALETTE_UL_saved",
                "",
                self,
                "saved_palettes",
                self,
                "saved_palette_index",
                rows=5,
            )
            col = row.column(align=True)
            col.operator("palette.library_remove", icon='REMOVE', text="")
        else:
            box.label(text="No saved palettes in library yet.", icon='INFO')

    def draw_about_tab(self, box):
        col = box.column(align=True)
        col.label(text="Palette Colorizer 1.1 for Blender 5.0+", icon='COLOR')
        col.label(text="Author: Klra")
        col.label(text="Assign curated color palettes to viewport objects and showcase materials.")
        row = col.row(align=True)
        row.operator("wm.url_open", text="GitHub Repository", icon='URL').url = (
            "https://github.com/Klraman/Palette-Colorizer"
        )
