# Palette Colorizer 1.1.2 Update Notes

#### New in 1.1.2

- Removed the `3D View` tag from `blender_manifest.toml` and added a direct link to the GitHub Issues page for support and bug reports.

### Palette Colorizer 1.1.1: Live Updates, Smart Grouping, Non-Destructive Material Slots, and Blender Extensions Compliance

This update overhauls the user interface, material architecture, and color assignment engine for Blender 5.0 and 5.2, and ensures full compliance with the official Blender Extensions platform.

#### New in 1.1.1 (Blender Extensions Compliance)

- Removed legacy `bl_info` dictionary in favor of `blender_manifest.toml` metadata.
- Added `SPDX-License-Identifier: GPL-3.0-or-later` headers across all Python modules.
- Replaced custom preferences ID wrappers with native `__package__` resolution.
- Removed the custom filesystem self-updater so the add-on remains strictly read-only within its installation directory and uses Blender's native Extensions update system.
- Updated `blender_manifest.toml` tagline and permission descriptions to meet the 64-character limit with no trailing punctuation.

#### Core 1.1 Features

- Live Viewport Updates: Switching palettes, scrubbing the seed slider, or changing distribution modes updates object colors immediately in the viewport.
- Interactive Swatch Preview Strip: Preview all colors of any built-in, theme, saved, or custom palette directly below the palette selector. Click any swatch to edit it and automatically fork the preset into Custom mode.
- Target Grouping Modes: Color your scene Per Object, Per Collection, Per Root Parent hierarchy, or Per Loose Mesh Island.
- Object Color Pinning: Lock colors on selected objects with Pin Selected so seed re-rolls only change the remaining unlocked objects.
- Adjacent Color Contrast: In Random mode, a spatial proximity check prevents touching neighbor objects from receiving identical swatch colors.
- Image Palette Sampler: Sample 8 dominant colors from any loaded Blender reference image directly into your Custom palette.

#### Material and Surface Improvements

- Non-Destructive Material Slots: Assigning showcase materials to meshes that already have materials appends a temporary palette material slot instead of overwriting Slot 0. Clicking Clear Materials removes the temporary slot and restores your original per-face material assignments automatically.
- Single Shared Master Material: Instead of creating one material per object, the default Shared Master mode uses a single Principled BSDF material driven by an Object Info node across the entire scene.
- Per-Swatch and Color Attribute Modes: Switch between a single master material, one material per palette swatch, or a mesh Color Attribute (PC_Color) workflow.
- Live Surface Sliders: Control Roughness, Metallic, and Specular values in real time across all showcase materials for matte clay, glossy plastic, or metallic blockout renders.
- Protect Existing Materials Toggle: Optional toggle to skip objects that already have non-palette materials assigned.
- Non-Mesh Object Support: Color Curve, Surface, Meta, and Text objects alongside standard Meshes.

#### User Interface Redesign

- Categorized Palette Menu: All 30 built-in palettes, Theme palette, and Saved Library palettes are organized under clear category headers.
- Segmented Controls: Replaced nested boxes and redundant buttons with horizontal segmented toggles and collapsible sub-panels matching Blender 5.x design standards.

---

## Compact Summary

Palette Colorizer 1.1.1 for Blender 5.0+ is out now!

What is new:
- Full Blender Extensions platform compliance
- Live viewport updates as you scrub palettes & seeds
- Non-destructive material slots (keeps & restores your original materials)
- Group by Object, Collection, Parent, or Mesh Island
- Pin/lock object colors & Adjacent Contrast check
- 1 Shared Master Material + live Roughness/Metallic sliders
- Sample palettes from reference images
