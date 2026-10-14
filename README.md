# Palette Colorizer for Blender

Palette Colorizer assigns harmonious color palettes to objects in Blender. It supports Blender 4.2 and Blender 5.2.

## How It Functions

Palette Colorizer changes how you color scene objects:

1. The add-on sets the 3D viewport shading color type to Object mode.
2. It assigns RGBA color values to the color property of each mesh object.
3. You choose from three distribution modes:
   - Sequential: Assigns colors in palette sequence.
   - Random: Assigns colors from the palette with a seed value.
   - By Name: Uses an object name hash to assign a stable color.
4. The add-on can create a Principled BSDF material for each object. This connects the palette color to the Base Color input for Cycles and EEVEE renders.
5. The add-on encodes palettes into compact JSON strings. You can copy these strings to your clipboard or save palettes to your local library.

## Why Use Palette Colorizer Over Blender Random Color

Blender includes a built-in Random viewport color option. Palette Colorizer provides distinct advantages:

- Controlled Color Harmony: Blender random color produces chaotic, clashing hues. Palette Colorizer constrains objects to curated palettes with balanced saturation and values.
- Direct Render Output: Blender random color works only in solid viewport display. It does not appear in Cycles or EEVEE renders without manual shader node networks. Palette Colorizer creates real materials in one click.
- Repeatable Seeds: Blender random color provides no seed control. Palette Colorizer includes an unbiased seed generator from 1 through 9999 to reproduce exact assignments.
- Theme Integration: Palette Colorizer extracts colors from your active Blender interface theme for consistent presentations.
- Team Collaboration: You cannot share Blender random color assignments. Palette Colorizer lets you copy a palette string to Discord or export JSON files to your team.

## Key Features

- 30 built-in color palettes.
- Dynamic palette from your active Blender theme.
- Custom palette editor with color add, remove, and hue generation tools.
- Unbiased random seed generator from 1 through 9999.
- Automatic viewport shading switch to Object color mode.
- One-click material creation for Cycles and EEVEE engines.
- Compact JSON string copy and paste for quick sharing.
- Persistent palette library stored in add-on preferences.

## How to Install

1. Download the palette_colorizer.zip file.
2. Open Blender 4.2 or Blender 5.2.
3. Open Edit and select Preferences.
4. Select the Add-ons section.
5. Click the top-right arrow icon and select Install from Disk.
6. Select the palette_colorizer.zip file and click Install from Disk.
7. Find Palette Colorizer in the list and enable the checkbox.
8. Press N in the 3D Viewport to open the sidebar and select the Palette tab.
