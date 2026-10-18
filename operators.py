# SPDX-License-Identifier: GPL-3.0-or-later

"""
Operators and scene execution logic for Palette Colorizer.
"""

import json
import random
import colorsys
import bpy
import bmesh
from mathutils import Vector
from bpy.props import IntProperty, BoolProperty, StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper, ExportHelper

from .palettes import (
    get_active_palette_colors,
    palette_to_dict,
    dict_to_palette,
    load_colors_into_custom,
    extract_colors_from_image,
)

PALETTE_MAT_PREFIX = "PC_"
COLOR_ATTR_NAME = "PC_Color"
ORIG_MAT_ATTR_NAME = "_pc_orig_mat_idx"
VALID_OBJECT_TYPES = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'}

def name_to_color_index(name, palette_len):
    """Compute a deterministic hash index from a string name."""
    h = 0
    for ch in name:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return h % max(1, palette_len)

def get_target_objects(settings, context):
    """Return sorted target objects based on scope and object type filter."""
    allowed_types = VALID_OBJECT_TYPES if settings.include_non_mesh else {'MESH'}
    if settings.affect == "SELECTED":
        pool = context.selected_objects
    elif settings.affect == "ALL":
        pool = context.scene.objects
    else:
        pool = context.visible_objects
    objs = [o for o in pool if o.type in allowed_types]
    objs.sort(key=lambda o: o.name)
    return objs

def get_root_parent(obj):
    """Return the top-level parent object for hierarchy grouping."""
    curr = obj
    while curr.parent is not None:
        curr = curr.parent
    return curr

def get_group_key(obj, grouping_mode):
    """Return a stable group key string for an object based on grouping mode."""
    if grouping_mode == "COLLECTION":
        cols = obj.users_collection
        return cols[0].name if cols else "Scene Collection"
    if grouping_mode == "ROOT_PARENT":
        return get_root_parent(obj).name
    return obj.name

def get_world_bounds_info(obj):
    """Return (world_center, bounding_radius) for spatial adjacency checks."""
    try:
        corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        center = sum(corners, Vector((0.0, 0.0, 0.0))) / 8.0
        radius = max((c - center).length for c in corners)
        return center, max(radius, 0.001)
    except Exception:
        return obj.matrix_world.translation.copy(), 0.5

def compute_adjacent_pairs(objects):
    """Return a dictionary mapping object index to a list of touching prior object indices."""
    bounds = [get_world_bounds_info(o) for o in objects]
    neighbors = {i: [] for i in range(len(objects))}
    limit = min(len(objects), 400)
    for i in range(limit):
        c1, r1 = bounds[i]
        for j in range(i):
            c2, r2 = bounds[j]
            if (c1 - c2).length <= (r1 + r2) * 1.15:
                neighbors[i].append(j)
    return neighbors

def switch_viewport_shading(context, color_type="OBJECT"):
    """Set 3D Viewport solid shading color mode."""
    if not context.screen:
        return
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    try:
                        space.shading.color_type = color_type
                    except Exception:
                        pass

def has_protected_real_material(obj):
    """Return True if object has a non-palette material assigned."""
    if not obj.data or not hasattr(obj.data, "materials"):
        return False
    for mat in obj.data.materials:
        if mat and not mat.name.startswith(PALETTE_MAT_PREFIX):
            return True
    return False

def configure_bsdf_surface(bsdf, settings):
    """Apply Roughness, Metallic, and Specular values to a Principled BSDF node."""
    if not bsdf:
        return
    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = settings.mat_roughness
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = settings.mat_metallic
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = settings.mat_specular
    elif "Specular" in bsdf.inputs:
        bsdf.inputs["Specular"].default_value = settings.mat_specular

def update_all_pc_materials(settings):
    """Update surface parameters on all existing Palette Colorizer materials."""
    for mat in bpy.data.materials:
        if not mat.name.startswith(PALETTE_MAT_PREFIX) or not mat.node_tree:
            continue
        bsdf = next(
            (n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'),
            None,
        )
        configure_bsdf_surface(bsdf, settings)

def _ensure_principled_bsdf(mat, settings):
    """Ensure the material uses nodes and return its Principled BSDF node."""
    if bpy.app.version < (5, 0, 0):
        mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is None:
        bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
    out = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None)
    if out is None:
        out = nt.nodes.new('ShaderNodeOutputMaterial')
        out.location = (300, 0)
    if not out.inputs['Surface'].is_linked:
        nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    configure_bsdf_surface(bsdf, settings)
    return nt, bsdf

def get_or_create_shared_object_info_material(settings):
    """Create or update a single master material driven by Object Info -> Color."""
    mat_name = f"{PALETTE_MAT_PREFIX}Showcase_Material"
    mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(name=mat_name)
    nt, bsdf = _ensure_principled_bsdf(mat, settings)

    obj_info = next((n for n in nt.nodes if n.type == 'OBJECT_INFO'), None)
    if obj_info is None:
        obj_info = nt.nodes.new('ShaderNodeObjectInfo')
        obj_info.location = (-260, 0)

    nt.links.new(obj_info.outputs['Color'], bsdf.inputs['Base Color'])
    return mat

def get_or_create_swatch_material(swatch_index, rgba, settings):
    """Create or update a shared material for a specific palette swatch index."""
    mat_name = f"{PALETTE_MAT_PREFIX}Swatch_{swatch_index + 1:02d}"
    mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(name=mat_name)
    nt, bsdf = _ensure_principled_bsdf(mat, settings)

    for link in list(bsdf.inputs['Base Color'].links):
        nt.links.remove(link)

    r, g, b = rgba[0], rgba[1], rgba[2]
    bsdf.inputs['Base Color'].default_value = (r, g, b, 1.0)
    mat.diffuse_color = (r, g, b, 1.0)
    return mat

def get_or_create_attribute_material(settings):
    """Create or update a shared material driven by the PC_Color mesh attribute."""
    mat_name = f"{PALETTE_MAT_PREFIX}Attribute_Material"
    mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(name=mat_name)
    nt, bsdf = _ensure_principled_bsdf(mat, settings)

    attr_node = next((n for n in nt.nodes if n.type == 'ATTRIBUTE'), None)
    if attr_node is None:
        attr_node = nt.nodes.new('ShaderNodeAttribute')
        attr_node.location = (-260, 0)
    attr_node.attribute_name = COLOR_ATTR_NAME

    nt.links.new(attr_node.outputs['Color'], bsdf.inputs['Base Color'])
    return mat

def assign_material_to_object(obj, mat, settings):
    """Assign a palette material to an object by reusing a PC_* slot or adding a new slot."""
    if not obj.data or not hasattr(obj.data, "materials"):
        return
    if settings.protect_real_materials and has_protected_real_material(obj):
        return

    mats = obj.data.materials
    pc_idx = next(
        (i for i, m in enumerate(mats) if m and m.name.startswith(PALETTE_MAT_PREFIX)),
        None,
    )

    if pc_idx is not None:
        mats[pc_idx] = mat
    elif len(mats) == 0:
        mats.append(mat)
        pc_idx = 0
    elif len(mats) == 1 and mats[0] is None:
        mats[0] = mat
        pc_idx = 0
    else:
        mats.append(mat)
        pc_idx = len(mats) - 1

    obj.active_material_index = pc_idx

    if pc_idx > 0:
        if obj.type == 'MESH' and len(obj.data.polygons) > 0:
            poly_count = len(obj.data.polygons)
            if ORIG_MAT_ATTR_NAME not in obj.data.attributes:
                orig_indices = [0] * poly_count
                obj.data.polygons.foreach_get("material_index", orig_indices)
                backup_attr = obj.data.attributes.new(
                    name=ORIG_MAT_ATTR_NAME,
                    type='INT',
                    domain='FACE',
                )
                backup_attr.data.foreach_set("value", orig_indices)
            obj.data.polygons.foreach_set("material_index", [pc_idx] * poly_count)
            obj.data.update()
        elif hasattr(obj.data, "splines") and len(obj.data.splines) > 0:
            if "_pc_orig_spline_mats" not in obj:
                obj["_pc_orig_spline_mats"] = [s.material_index for s in obj.data.splines]
            for s in obj.data.splines:
                s.material_index = pc_idx

def write_mesh_color_attribute(obj, rgba):
    """Write a uniform RGBA color to the PC_Color attribute on a mesh object."""
    if obj.type != 'MESH' or not obj.data:
        return
    mesh = obj.data
    attr = mesh.color_attributes.get(COLOR_ATTR_NAME)
    if attr is None:
        attr = mesh.color_attributes.new(
            name=COLOR_ATTR_NAME,
            type='BYTE_COLOR',
            domain='POINT',
        )
    count = len(attr.data)
    if count > 0:
        flat = list(rgba) * count
        attr.data.foreach_set("color", flat)
    mesh.color_attributes.active_color = attr

def write_mesh_islands_colors(obj, palette, settings, rng):
    """Assign palette colors per loose mesh island using bmesh and PC_Color attribute."""
    if obj.type != 'MESH' or not obj.data:
        return palette[0]
    mesh = obj.data

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()

    visited = set()
    islands = []
    for v in bm.verts:
        if v.index in visited:
            continue
        stack = [v]
        comp = []
        visited.add(v.index)
        while stack:
            curr = stack.pop()
            comp.append(curr.index)
            for e in curr.link_edges:
                other = e.other_vert(curr)
                if other.index not in visited:
                    visited.add(other.index)
                    stack.append(other)
        islands.append(comp)
    bm.free()

    attr = mesh.color_attributes.get(COLOR_ATTR_NAME)
    if attr is not None and attr.domain != 'POINT':
        mesh.color_attributes.remove(attr)
        attr = None
    if attr is None:
        attr = mesh.color_attributes.new(
            name=COLOR_ATTR_NAME,
            type='BYTE_COLOR',
            domain='POINT',
        )

    v_count = len(mesh.vertices)
    colors_flat = [1.0] * (v_count * 4)
    first_color = palette[0]

    for idx_island, vert_indices in enumerate(islands):
        if settings.assignment_mode == "SEQUENTIAL":
            c_idx = idx_island % len(palette)
        elif settings.assignment_mode == "RANDOM":
            c_idx = rng.randint(0, len(palette) - 1)
        else:
            c_idx = name_to_color_index(f"{obj.name}_{idx_island}", len(palette))
        rgba = palette[c_idx]
        if idx_island == 0:
            first_color = rgba
        for v_i in vert_indices:
            base = v_i * 4
            colors_flat[base:base + 4] = rgba

    if v_count > 0:
        attr.data.foreach_set("color", colors_flat)
    mesh.color_attributes.active_color = attr
    return first_color

def apply_palette_to_scene(context, settings, force_material=False):
    """Apply the active palette to target objects according to current settings."""
    palette = get_active_palette_colors(settings, context)
    objects = get_target_objects(settings, context)
    if not objects or not palette:
        return 0

    rng = random.Random(settings.randomize_seed)
    num_colors = len(palette)

    do_viewport = settings.output_mode in {"VIEWPORT", "BOTH"}
    do_material = force_material or (settings.output_mode in {"MATERIAL", "BOTH"})

    shared_obj_mat = None
    shared_attr_mat = None
    if do_material:
        if settings.material_mode == "SHARED_OBJECT_INFO":
            shared_obj_mat = get_or_create_shared_object_info_material(settings)
        elif settings.material_mode == "COLOR_ATTRIBUTE":
            shared_attr_mat = get_or_create_attribute_material(settings)

    neighbors = {}
    if (
        settings.assignment_mode == "RANDOM"
        and settings.grouping_mode == "OBJECT"
        and settings.avoid_adjacent_duplicates
        and num_colors > 1
    ):
        neighbors = compute_adjacent_pairs(objects)

    group_color_map = {}
    assigned_indices = {}
    applied_count = 0

    for i, obj in enumerate(objects):
        if obj.get("pc_locked", False):
            continue

        if settings.grouping_mode == "ISLAND" and obj.type == 'MESH':
            primary_rgba = write_mesh_islands_colors(obj, palette, settings, rng)
            r, g, b, a = primary_rgba
            if settings.preserve_alpha:
                a = obj.color[3]
            if do_viewport or settings.material_mode == "SHARED_OBJECT_INFO":
                obj.color = (r, g, b, a)
            if do_material:
                mat = get_or_create_attribute_material(settings)
                assign_material_to_object(obj, mat, settings)
            applied_count += 1
            continue

        g_key = get_group_key(obj, settings.grouping_mode)
        if settings.grouping_mode in {"COLLECTION", "ROOT_PARENT"} and g_key in group_color_map:
            idx = group_color_map[g_key]
        else:
            if settings.assignment_mode == "SEQUENTIAL":
                idx = (len(group_color_map) if settings.grouping_mode != "OBJECT" else i) % num_colors
            elif settings.assignment_mode == "RANDOM":
                used_by_neighbors = {assigned_indices[n] for n in neighbors.get(i, []) if n in assigned_indices}
                candidates = [c for c in range(num_colors) if c not in used_by_neighbors]
                idx = rng.choice(candidates) if candidates else rng.randint(0, num_colors - 1)
            else:
                idx = name_to_color_index(g_key, num_colors)
            group_color_map[g_key] = idx

        assigned_indices[i] = idx
        r, g, b, a = palette[idx]
        if settings.preserve_alpha:
            a = obj.color[3]

        if do_viewport or (do_material and settings.material_mode == "SHARED_OBJECT_INFO"):
            obj.color = (r, g, b, a)

        if do_material:
            if settings.material_mode == "SHARED_OBJECT_INFO":
                assign_material_to_object(obj, shared_obj_mat, settings)
            elif settings.material_mode == "PER_SWATCH":
                swatch_mat = get_or_create_swatch_material(idx, (r, g, b, a), settings)
                assign_material_to_object(obj, swatch_mat, settings)
            elif settings.material_mode == "COLOR_ATTRIBUTE":
                write_mesh_color_attribute(obj, (r, g, b, a))
                assign_material_to_object(obj, shared_attr_mat, settings)

        applied_count += 1

    if settings.auto_switch_shading:
        if settings.output_mode == "MATERIAL" or (force_material and settings.material_mode == "PER_SWATCH"):
            switch_viewport_shading(context, "MATERIAL")
        else:
            switch_viewport_shading(context, "OBJECT")

    return applied_count

class PALETTE_OT_apply_colors(Operator):
    bl_idname = "palette.apply_colors"
    bl_label = "Apply Palette"
    bl_description = "Assign active palette colors and materials to target objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.palette_colorizer
        count = apply_palette_to_scene(context, settings)
        if count == 0:
            self.report({'WARNING'}, "No unlocked target objects found.")
            return {'CANCELLED'}
        self.report({'INFO'}, f"Applied '{settings.palette_name}' to {count} object(s).")
        return {'FINISHED'}

class PALETTE_OT_apply_materials(Operator):
    bl_idname = "palette.apply_materials"
    bl_label = "Assign Materials"
    bl_description = "Assign showcase materials to target objects for Cycles and EEVEE rendering"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.palette_colorizer
        count = apply_palette_to_scene(context, settings, force_material=True)
        if count == 0:
            self.report({'WARNING'}, "No unlocked target objects found.")
            return {'CANCELLED'}
        self.report({'INFO'}, f"Assigned showcase materials to {count} object(s).")
        return {'FINISHED'}

class PALETTE_OT_reset_colors(Operator):
    bl_idname = "palette.reset_colors"
    bl_label = "Reset"
    bl_description = "Reset viewport colors to white on target unlocked objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.palette_colorizer
        objects = get_target_objects(settings, context)
        count = 0
        for obj in objects:
            if obj.get("pc_locked", False):
                continue
            obj.color = (1.0, 1.0, 1.0, 1.0)
            count += 1
        self.report({'INFO'}, f"Reset {count} object(s) to white.")
        return {'FINISHED'}

class PALETTE_OT_clear_materials(Operator):
    bl_idname = "palette.clear_materials"
    bl_label = "Clear Materials"
    bl_description = "Remove temporary Palette Colorizer (PC_*) materials and color attributes from target objects"
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
            self.report({'WARNING'}, "No valid target objects found.")
            return {'CANCELLED'}

        removed_count = 0
        palette_mats = set()
        for obj in objects:
            if obj.type == 'MESH' and obj.data:
                attr = obj.data.color_attributes.get(COLOR_ATTR_NAME)
                if attr is not None:
                    obj.data.color_attributes.remove(attr)

                backup_attr = obj.data.attributes.get(ORIG_MAT_ATTR_NAME)
                if backup_attr is not None:
                    poly_count = len(obj.data.polygons)
                    if len(backup_attr.data) == poly_count and poly_count > 0:
                        orig_indices = [0] * poly_count
                        backup_attr.data.foreach_get("value", orig_indices)
                        obj.data.polygons.foreach_set("material_index", orig_indices)
                    obj.data.attributes.remove(backup_attr)

            elif hasattr(obj.data, "splines") and "_pc_orig_spline_mats" in obj:
                orig_spline_mats = list(obj["_pc_orig_spline_mats"])
                for idx_s, s in enumerate(obj.data.splines):
                    if idx_s < len(orig_spline_mats):
                        s.material_index = int(orig_spline_mats[idx_s])
                del obj["_pc_orig_spline_mats"]

            if not obj.data or not hasattr(obj.data, "materials"):
                continue
            for i in reversed(range(len(obj.data.materials))):
                mat = obj.data.materials[i]
                if mat:
                    if self.only_palette and not mat.name.startswith(PALETTE_MAT_PREFIX):
                        continue
                    palette_mats.add(mat)
                    obj.data.materials.pop(index=i)
                    removed_count += 1

            if len(obj.data.materials) > 0:
                obj.active_material_index = 0
            if obj.type == 'MESH' and obj.data:
                obj.data.update()

        for mat in palette_mats:
            if mat.users == 0:
                bpy.data.materials.remove(mat)

        self.report({'INFO'}, f"Removed {removed_count} material slot(s) across {len(objects)} object(s).")
        return {'FINISHED'}

class PALETTE_OT_lock_selected(Operator):
    bl_idname = "palette.lock_selected"
    bl_label = "Lock Selected"
    bl_description = "Pin current palette colors on selected objects so seed and palette changes skip them"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        objs = context.selected_objects
        if not objs:
            self.report({'WARNING'}, "No objects selected.")
            return {'CANCELLED'}
        for obj in objs:
            obj["pc_locked"] = True
        self.report({'INFO'}, f"Locked color on {len(objs)} object(s).")
        return {'FINISHED'}

class PALETTE_OT_unlock_selected(Operator):
    bl_idname = "palette.unlock_selected"
    bl_label = "Unlock Selected"
    bl_description = "Unpin selected objects so they receive new palette colors again"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        objs = context.selected_objects
        if not objs:
            self.report({'WARNING'}, "No objects selected.")
            return {'CANCELLED'}
        for obj in objs:
            if "pc_locked" in obj:
                del obj["pc_locked"]
        self.report({'INFO'}, f"Unlocked {len(objs)} object(s).")
        if context.scene.palette_colorizer.auto_apply:
            apply_palette_to_scene(context, context.scene.palette_colorizer)
        return {'FINISHED'}

class PALETTE_OT_randomize_seed(Operator):
    bl_idname = "palette.randomize_seed"
    bl_label = "Randomize Seed"
    bl_description = "Select an unbiased random seed between 1 and 9999"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        digits = random.randint(1, 4)
        min_val = 1 if digits == 1 else 10 ** (digits - 1)
        max_val = 10 ** digits - 1
        context.scene.palette_colorizer.randomize_seed = random.randint(min_val, max_val)
        return {'FINISHED'}

class PALETTE_OT_step_seed(Operator):
    bl_idname = "palette.step_seed"
    bl_label = "Step Seed"
    bl_description = "Increment or decrement the random seed by 1"
    bl_options = {'REGISTER', 'UNDO'}

    step: IntProperty(default=1)

    def execute(self, context):
        settings = context.scene.palette_colorizer
        new_seed = max(1, min(9999, settings.randomize_seed + self.step))
        settings.randomize_seed = new_seed
        return {'FINISHED'}

class PALETTE_OT_copy_to_custom(Operator):
    bl_idname = "palette.copy_to_custom"
    bl_label = "Edit in Custom"
    bl_description = "Copy the active palette into the Custom Palette editor for tweaking"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.palette_colorizer
        colors = get_active_palette_colors(settings, context)
        src_name = settings.palette_name
        if src_name.startswith("SAVED::"):
            src_name = src_name[7:]
        load_colors_into_custom(settings, colors)
        if src_name != "CUSTOM":
            settings.custom_palette_name = f"{src_name} Copy"
        settings.palette_name = "CUSTOM"
        self.report({'INFO'}, f"Copied {len(colors)} colors to Custom Palette.")
        return {'FINISHED'}

class PALETTE_OT_sample_image_colors(Operator):
    bl_idname = "palette.sample_image_colors"
    bl_label = "Sample Image Colors"
    bl_description = "Sample 8 dominant colors from the selected image into the Custom Palette"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.palette_colorizer
        img = settings.source_image
        if not img:
            self.report({'WARNING'}, "Select a Source Image first.")
            return {'CANCELLED'}
        colors = extract_colors_from_image(img, count=8)
        if not colors:
            self.report({'WARNING'}, "Could not read pixel data from the selected image.")
            return {'CANCELLED'}
        load_colors_into_custom(settings, colors)
        settings.custom_palette_name = img.name.rsplit(".", 1)[0]
        settings.palette_name = "CUSTOM"
        self.report({'INFO'}, f"Extracted {len(colors)} colors from '{img.name}'.")
        return {'FINISHED'}

class PALETTE_OT_add_custom_color(Operator):
    bl_idname = "palette.add_custom_color"
    bl_label = "Add Color"
    bl_description = "Add a new color slot to the custom palette"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.palette_colorizer
        item = settings.custom_colors.add()
        item.color = (random.random(), random.random(), random.random(), 1.0)
        settings.custom_color_index = len(settings.custom_colors) - 1
        if settings.auto_apply:
            apply_palette_to_scene(context, settings)
        return {'FINISHED'}

class PALETTE_OT_remove_custom_color(Operator):
    bl_idname = "palette.remove_custom_color"
    bl_label = "Remove Color"
    bl_description = "Remove the selected color slot from the custom palette"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.palette_colorizer
        idx = settings.custom_color_index
        if 0 <= idx < len(settings.custom_colors):
            settings.custom_colors.remove(idx)
            settings.custom_color_index = max(0, idx - 1)
            if settings.auto_apply:
                apply_palette_to_scene(context, settings)
        return {'FINISHED'}

class PALETTE_OT_randomize_custom(Operator):
    bl_idname = "palette.randomize_custom"
    bl_label = "Generate Hues"
    bl_description = "Fill custom palette with evenly distributed hues"
    bl_options = {'REGISTER', 'UNDO'}

    count: IntProperty(name="Count", default=8, min=2, max=32)

    def execute(self, context):
        settings = context.scene.palette_colorizer
        settings.custom_colors.clear()
        for i in range(self.count):
            r, g, b = colorsys.hsv_to_rgb(i / self.count, 0.75, 0.90)
            item = settings.custom_colors.add()
            item.color = (r, g, b, 1.0)
        settings.custom_color_index = 0
        if settings.auto_apply:
            apply_palette_to_scene(context, settings)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class PALETTE_OT_copy_string(Operator):
    bl_idname = "palette.copy_string"
    bl_label = "Copy Share String"
    bl_description = "Encode active palette as a compact JSON string and copy to clipboard"

    def execute(self, context):
        settings = context.scene.palette_colorizer
        colors = get_active_palette_colors(settings, context)
        name = (
            settings.custom_palette_name
            if settings.palette_name == "CUSTOM"
            else settings.palette_name.replace("SAVED::", "")
        )
        share_str = json.dumps(palette_to_dict(name, colors), separators=(',', ':'))
        context.window_manager.clipboard = share_str
        self.report({'INFO'}, f"Copied '{name}' ({len(colors)} colors) to clipboard.")
        return {'FINISHED'}

class PALETTE_OT_paste_string(Operator):
    bl_idname = "palette.paste_string"
    bl_label = "Import Pasted String"
    bl_description = "Parse the palette string from the Paste field or clipboard into Custom mode"
    bl_options = {'REGISTER', 'UNDO'}

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
            else settings.palette_name.replace("SAVED::", "")
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
    bl_options = {'REGISTER', 'UNDO'}

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

class PALETTE_OT_library_save(Operator):
    bl_idname = "palette.library_save"
    bl_label = "Save to Library"
    bl_description = "Save the active palette to the persistent add-on library"

    def execute(self, context):
        settings = context.scene.palette_colorizer
        colors = get_active_palette_colors(settings, context)
        if settings.palette_name == "CUSTOM":
            name = settings.custom_palette_name.strip() or "Unnamed"
        else:
            name = settings.palette_name.replace("SAVED::", "")
        data_str = json.dumps(palette_to_dict(name, colors))
        prefs = context.preferences.addons[__package__].preferences
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
    bl_options = {'REGISTER', 'UNDO'}

    index: IntProperty(default=0)

    def execute(self, context):
        settings = context.scene.palette_colorizer
        prefs = context.preferences.addons[__package__].preferences
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
        prefs = context.preferences.addons[__package__].preferences
        idx = prefs.saved_palette_index
        if 0 <= idx < len(prefs.saved_palettes):
            name = prefs.saved_palettes[idx].name
            prefs.saved_palettes.remove(idx)
            prefs.saved_palette_index = max(0, idx - 1)
            self.report({'INFO'}, f"Removed '{name}' from library.")
        return {'FINISHED'}

class PALETTE_OT_open_preferences(Operator):
    bl_idname = "palette.open_preferences"
    bl_label = "Open Add-on Preferences"
    bl_description = "Open Palette Colorizer preferences and saved palette library"

    def execute(self, context):
        try:
            bpy.ops.preferences.addon_show(module=__package__)
        except Exception:
            bpy.ops.screen.userpref_show("INVOKE_DEFAULT")
        return {'FINISHED'}
