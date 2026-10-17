
import bpy
import math
import os
import json

# Setup clean scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'

# Set world background
world = bpy.data.worlds.new("StudioWorld")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs['Color'].default_value = (0.05, 0.06, 0.08, 1.0)
    bg.inputs['Strength'].default_value = 0.8

# Camera setup
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 65
cam_obj = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam_obj)
cam_obj.location = (0.0, -9.5, 3.8)
cam_obj.rotation_euler = (math.radians(68), 0, 0)
scene.camera = cam_obj

# Key light
key_light = bpy.data.lights.new(name="KeyLight", type='AREA')
key_light.energy = 600
key_light.size = 5.0
key_obj = bpy.data.objects.new(name="KeyLight", object_data=key_light)
scene.collection.objects.link(key_obj)
key_obj.location = (4.0, -5.0, 6.0)
key_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(30))

# Fill light
fill_light = bpy.data.lights.new(name="FillLight", type='AREA')
fill_light.energy = 250
fill_light.size = 6.0
fill_light.color = (0.7, 0.8, 1.0)
fill_obj = bpy.data.objects.new(name="FillLight", object_data=fill_light)
scene.collection.objects.link(fill_obj)
fill_obj.location = (-5.0, -4.0, 4.0)

# Rim light
rim_light = bpy.data.lights.new(name="RimLight", type='SPOT')
rim_light.energy = 400
rim_light.spot_size = math.radians(70)
rim_obj = bpy.data.objects.new(name="RimLight", object_data=rim_light)
scene.collection.objects.link(rim_obj)
rim_obj.location = (0.0, 5.0, 5.0)
rim_obj.rotation_euler = (math.radians(-50), 0, 0)

# Studio floor
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, -1.0))
floor = bpy.context.active_object
floor_mat = bpy.data.materials.new(name="FloorMat")
floor_mat.use_nodes = True
floor_bsdf = floor_mat.node_tree.nodes.get('Principled BSDF')
if floor_bsdf:
    floor_bsdf.inputs['Base Color'].default_value = (0.07, 0.08, 0.10, 1.0)
    floor_bsdf.inputs['Roughness'].default_value = 0.35
floor.data.materials.append(floor_mat)

# Create 8 demo objects arranged symmetrically
objects = []

# 1. Center: Suzanne Monkey
bpy.ops.mesh.primitive_monkey_add(size=1.6, location=(0.0, -0.2, 0.3))
suz = bpy.context.active_object
bpy.ops.object.shade_smooth()
objects.append(suz)

# 2. Beveled Cube left
bpy.ops.mesh.primitive_cube_add(size=1.3, location=(-2.4, -0.6, 0.1))
c1 = bpy.context.active_object
mod = c1.modifiers.new("Bevel", 'BEVEL')
mod.width = 0.15
mod.segments = 4
bpy.ops.object.shade_smooth()
objects.append(c1)

# 3. Sphere right
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.75, location=(2.4, -0.6, 0.1))
s1 = bpy.context.active_object
bpy.ops.object.shade_smooth()
objects.append(s1)

# 4. Torus far left
bpy.ops.mesh.primitive_torus_add(major_radius=0.75, minor_radius=0.28, location=(-4.2, 0.5, 0.1))
t1 = bpy.context.active_object
t1.rotation_euler = (math.radians(45), math.radians(30), 0)
bpy.ops.object.shade_smooth()
objects.append(t1)

# 5. Cylinder far right
bpy.ops.mesh.primitive_cylinder_add(radius=0.6, depth=1.4, location=(4.2, 0.5, 0.1))
cyl = bpy.context.active_object
mod = cyl.modifiers.new("Bevel", 'BEVEL')
mod.width = 0.1
mod.segments = 4
bpy.ops.object.shade_smooth()
objects.append(cyl)

# 6. Small sphere back center-left
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55, location=(-1.3, 1.4, 0.8))
s2 = bpy.context.active_object
bpy.ops.object.shade_smooth()
objects.append(s2)

# 7. Small cube back center-right
bpy.ops.mesh.primitive_cube_add(size=0.9, location=(1.3, 1.4, 0.8))
c2 = bpy.context.active_object
c2.rotation_euler = (0, 0, math.radians(25))
mod = c2.modifiers.new("Bevel", 'BEVEL')
mod.width = 0.1
mod.segments = 4
bpy.ops.object.shade_smooth()
objects.append(c2)

# 8. Ico sphere front
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.5, subdivisions=3, location=(0.0, -2.1, -0.2))
ico = bpy.context.active_object
bpy.ops.object.shade_smooth()
objects.append(ico)

# Create materials for each object
materials = []
for i, obj in enumerate(objects):
    mat = bpy.data.materials.new(name=f"DemoMat_{i}")
    mat.use_nodes = True
    obj.data.materials.append(mat)
    materials.append(mat)

# Load palette dict from JSON passed via env or file
assets_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(assets_dir, "renders")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(assets_dir, "palettes_temp.json"), "r") as f:
    palettes_data = json.load(f)

# Render 16:9 shots
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.image_settings.file_format = 'PNG'

for pal_name, colors in palettes_data.items():
    for i, mat in enumerate(materials):
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            rgba = colors[i % len(colors)]
            bsdf.inputs['Base Color'].default_value = tuple(rgba)
            bsdf.inputs['Roughness'].default_value = 0.25
            bsdf.inputs['Specular IOR Level'].default_value = 0.5
    
    out_path = os.path.join(output_dir, f"{pal_name.lower()}_16_9.png")
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)

# Also render square 1200x1200 for Candy and Nord (for square thumbnail)
scene.render.resolution_x = 1200
scene.render.resolution_y = 1200
cam_obj.location = (0.0, -8.0, 3.2)
cam_obj.rotation_euler = (math.radians(68), 0, 0)

for pal_name in ["Candy", "Nord"]:
    colors = palettes_data[pal_name]
    for i, mat in enumerate(materials):
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            rgba = colors[i % len(colors)]
            bsdf.inputs['Base Color'].default_value = tuple(rgba)
    out_path = os.path.join(output_dir, f"{pal_name.lower()}_square.png")
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)

print("Blender 3D scene renders completed successfully.")
