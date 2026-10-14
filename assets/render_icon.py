import bpy
import math
import os

# Clean scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# Engine
engine_items = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in engine_items else 'BLENDER_EEVEE'

# World setup
world = bpy.data.worlds.new("IconWorld")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs['Color'].default_value = (0.04, 0.05, 0.07, 1.0)
    bg.inputs['Strength'].default_value = 0.6

# Camera setup (framed so full icon is centered with balanced padding)
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 72
cam_obj = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam_obj)
cam_obj.location = (0.0, -9.2, 5.0)
cam_obj.rotation_euler = (math.radians(61), 0, 0)
scene.camera = cam_obj

# Key Light
key_light = bpy.data.lights.new(name="KeyLight", type='AREA')
key_light.energy = 900
key_light.size = 5.0
key_obj = bpy.data.objects.new(name="KeyLight", object_data=key_light)
scene.collection.objects.link(key_obj)
key_obj.location = (3.5, -4.5, 6.5)
key_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(30))

# Fill Light
fill_light = bpy.data.lights.new(name="FillLight", type='AREA')
fill_light.energy = 400
fill_light.size = 6.0
fill_light.color = (0.75, 0.85, 1.0)
fill_obj = bpy.data.objects.new(name="FillLight", object_data=fill_light)
scene.collection.objects.link(fill_obj)
fill_obj.location = (-4.5, -3.5, 4.5)

# Rim Light
rim_light = bpy.data.lights.new(name="RimLight", type='SPOT')
rim_light.energy = 950
rim_light.spot_size = math.radians(80)
rim_obj = bpy.data.objects.new(name="RimLight", object_data=rim_light)
scene.collection.objects.link(rim_obj)
rim_obj.location = (0.0, 5.5, 6.0)
rim_obj.rotation_euler = (math.radians(-48), 0, 0)

# Sleek rounded pedestal disc
bpy.ops.mesh.primitive_cylinder_add(radius=3.4, depth=0.3, vertices=64, location=(0, 0, -0.6))
pedestal = bpy.context.active_object
mod_bev = pedestal.modifiers.new("Bevel", 'BEVEL')
mod_bev.width = 0.08
mod_bev.segments = 4
bpy.ops.object.shade_smooth()

ped_mat = bpy.data.materials.new(name="PedestalMat")
ped_mat.use_nodes = True
ped_bsdf = ped_mat.node_tree.nodes.get('Principled BSDF')
if ped_bsdf:
    ped_bsdf.inputs['Base Color'].default_value = (0.07, 0.08, 0.11, 1.0)
    ped_bsdf.inputs['Roughness'].default_value = 0.3
pedestal.data.materials.append(ped_mat)

# Center: Suzanne Monkey head with sleek dark metallic shader for high-contrast pop
bpy.ops.mesh.primitive_monkey_add(size=2.1, location=(0.0, -0.1, 0.5))
suzanne = bpy.context.active_object
mod_sub = suzanne.modifiers.new("Subdivision", 'SUBSURF')
mod_sub.levels = 2
mod_sub.render_levels = 2
bpy.ops.object.shade_smooth()

suz_mat = bpy.data.materials.new(name="SuzanneMat")
suz_mat.use_nodes = True
suz_bsdf = suz_mat.node_tree.nodes.get('Principled BSDF')
if suz_bsdf:
    suz_bsdf.inputs['Base Color'].default_value = (0.16, 0.19, 0.25, 1.0)
    suz_bsdf.inputs['Roughness'].default_value = 0.18
    suz_bsdf.inputs['Metallic'].default_value = 0.65
    suz_bsdf.inputs['Specular IOR Level'].default_value = 0.8
suzanne.data.materials.append(suz_mat)

# 8 Glossy, vivid candy-colored spheres forming a color wheel around Suzanne
palette_colors = [
    (1.00, 0.18, 0.35, 1.0),  # Vivid Crimson/Coral
    (1.00, 0.48, 0.05, 1.0),  # Bright Orange
    (1.00, 0.85, 0.05, 1.0),  # Warm Sunshine
    (0.18, 0.88, 0.40, 1.0),  # Emerald Lime
    (0.00, 0.78, 0.95, 1.0),  # Sky Cyan
    (0.18, 0.45, 1.00, 1.0),  # Electric Cobalt
    (0.65, 0.18, 0.98, 1.0),  # Deep Violet
    (1.00, 0.20, 0.75, 1.0),  # Hot Magenta
]

radius = 2.15
num_spheres = len(palette_colors)

for i, col in enumerate(palette_colors):
    angle = (i / num_spheres) * 2 * math.pi + math.radians(22.5)
    x = radius * math.cos(angle)
    y = radius * math.sin(angle) * 0.85 - 0.1
    z = 0.35 + 0.18 * math.sin(angle * 2)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.48, segments=48, ring_count=24, location=(x, y, z))
    sphere = bpy.context.active_object
    bpy.ops.object.shade_smooth()

    s_mat = bpy.data.materials.new(name=f"PaletteSphere_{i}")
    s_mat.use_nodes = True
    s_bsdf = s_mat.node_tree.nodes.get('Principled BSDF')
    if s_bsdf:
        s_bsdf.inputs['Base Color'].default_value = col
        s_bsdf.inputs['Roughness'].default_value = 0.08
        s_bsdf.inputs['Specular IOR Level'].default_value = 0.9
    sphere.data.materials.append(s_mat)

# Output resolution 1200x1200 square
scene.render.resolution_x = 1200
scene.render.resolution_y = 1200
scene.render.image_settings.file_format = 'PNG'

output_path = r"C:\Users\My Computer\Documents\Palette Colorizer\assets\thumbnail.png"
scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)
print("Rendered refined 3D icon thumbnail to:", output_path)
