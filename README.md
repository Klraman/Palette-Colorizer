# Palette Colorizer for Blender

Stop presenting flat gray models. Palette Colorizer gives your work-in-progress models, scene blockouts, and concept assets clean, harmonious colors directly in Blender. It supports Blender 5.0 and newer versions, including Blender 5.2.

## Why Use Palette Colorizer for Work-in-Progress Assets

Presenting 3D assets in default gray shading hides silhouette detail and visual hierarchy. Palette Colorizer solves this problem:

- Clear Visual Hierarchy: Distinct color palettes separate scene elements, component kits, collections, and assemblies at a glance.
- Client and Team Presentations: Deliver appealing work-in-progress viewport captures and turntable renders without complex production shaders.
- Fast Production Handover: Finish your modeling phase and start final shading. One click removes all temporary palette materials and attributes from your objects while keeping existing production shaders safe.

## How It Functions

Palette Colorizer streamlines how you color scene objects:

1. Live Viewport Updates: Select any palette, distribution mode, or seed and watch your scene update immediately in the 3D Viewport.
2. Interactive Swatch Preview: Preview all palette colors directly in the sidebar panel and copy any palette into the Custom editor with one click.
3. Flexible Grouping Modes:
   - Per Object: Assigns a swatch color to each object.
   - Per Collection: Assigns a shared color to all objects in the same collection.
   - Per Root Parent: Assigns a shared color to each parent hierarchy assembly.
   - Per Mesh Island: Assigns colors to disconnected mesh islands inside each object.
4. Three Distribution Modes:
   - Sequential: Assigns colors in palette sequence.
   - Random: Assigns colors using an unbiased seed (1 through 9999) with optional Adjacent Contrast to prevent touching objects from sharing the same color.
   - By Name: Uses an object or group name hash to assign a stable color.
5. Object Color Pinning: Pin specific objects so their colors stay locked while you re-roll seeds on the rest of your scene.
6. Smart Showcase Material Architecture:
   - Shared Master Material: Uses a single Principled BSDF material driven by an Object Info node across the entire scene.
   - Per Swatch Materials: Creates one shared material per palette swatch.
   - Mesh Color Attribute: Writes colors to a mesh Color Attribute and renders them through an Attribute shader node.
7. Live Surface Sliders: Adjust Roughness, Metallic, and Specular values in real time across all showcase materials.

## Why Use Palette Colorizer Over Blender Random Color

Blender includes a built-in Random viewport color option. Palette Colorizer provides distinct advantages:

- Controlled Color Harmony: Blender random color produces chaotic, clashing hues. Palette Colorizer constrains objects to curated palettes with balanced saturation and values.
- Direct Render Output: Blender random color works only in solid viewport display. Palette Colorizer creates render-ready Cycles and EEVEE materials in one click using a single shared material datablock.
- Non-Destructive Material Slots: Assigning showcase materials adds a temporary material slot without overwriting your existing materials. Clicking Clear Materials removes the temporary slot and restores your original per-face materials automatically.
- Pinning and Grouping: Blender random color cannot group by collection, parent hierarchy, or mesh island, and cannot lock colors on specific objects.
- Repeatable Seeds and Adjacency Control: Palette Colorizer includes an unbiased seed generator (1 through 9999) and spatial adjacency checks so touching parts receive contrasting colors.
- Image and Theme Integration: Extract a custom palette from any reference image or directly from your active Blender user interface theme.

## Key Features

- 30 categorized built-in color palettes.
- Dynamic palette extraction from your active Blender theme.
- Dominant color palette sampler from any loaded reference image.
- Interactive swatch preview bar in the sidebar panel.
- Live Update mode for instant feedback when changing palettes or seeds.
- Grouping by Object, Collection, Root Parent hierarchy, or Mesh Island.
- Object Pin and Unpin controls to lock colors on selected objects.
- Adjacent Contrast check to prevent duplicate colors on touching objects.
- Single Shared Master material, Per-Swatch materials, and Mesh Color Attribute modes.
- Live Roughness, Metallic, and Specular surface sliders.
- Protect Existing Materials toggle and one-click Clear Palette Materials cleanup.
- Compact JSON string copy and paste for quick palette sharing.
- Persistent palette library in Add-on Preferences.

## How to Install

1. Download the palette_colorizer.zip file.
2. Open Blender 5.0 or newer (including Blender 5.2).
3. Open Edit and select Preferences.
4. Select Get Extensions or Add-ons.
5. Click the top-right arrow icon and select Install from Disk.
6. Select the palette_colorizer.zip file and click Install from Disk.
