# SPDX-License-Identifier: GPL-3.0-or-later

"""
Add-on Preferences and saved palette library for Palette Colorizer.
"""

from bpy.props import (
    IntProperty,
    BoolProperty,
    EnumProperty,
    CollectionProperty,
)
from bpy.types import AddonPreferences

from .properties import SavedPaletteEntry

class PaletteColorizerPreferences(AddonPreferences):
    bl_idname = __package__

    saved_palettes: CollectionProperty(type=SavedPaletteEntry)
    saved_palette_index: IntProperty(default=0)

    show_sidebar_prefs_button: BoolProperty(
        name="Show Preferences Button in Sidebar Header",
        description="Display a quick-access Preferences gear button in the 3D Viewport Palette panel header",
        default=True,
    )

    tabs: EnumProperty(
        name="Tabs",
        items=[
            ("GENERAL", "General", "General add-on settings"),
            ("LIBRARY", "Saved Library", "Manage saved palettes that persist across blend files"),
            ("ABOUT", "About", "Version and documentation links"),
        ],
        default="GENERAL",
    )

    def draw(self, context):
        layout = self.layout

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
        col.label(text="Palette Colorizer 1.1.1 for Blender 5.0+", icon='COLOR')
        col.label(text="Author: Klra")
        col.label(text="Assign color palettes to viewport objects and showcase shaders.")
        row = col.row(align=True)
        row.operator("wm.url_open", text="GitHub Repository", icon='URL').url = (
            "https://github.com/Klraman/Palette-Colorizer"
        )
        row.operator("wm.url_open", text="Report an Issue", icon='HELP').url = (
            "https://github.com/Klraman/Palette-Colorizer/issues"
        )
