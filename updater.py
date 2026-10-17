"""
Add-on update scanner, staging utility, and installation operators for Preferences.
Modeled on the MESHmachine local zip update workflow.
"""

import os
import re
import shutil
import zipfile
import bpy
from bpy.props import StringProperty
from bpy.types import Operator
from .palettes import get_addon_id

_UPDATE_FILES_CACHE = None

def get_addon_path():
    """Return the root directory path of the installed add-on."""
    return os.path.dirname(os.path.realpath(__file__))

def get_prefs():
    """Return the add-on preferences instance, or None if unavailable."""
    addon_id = get_addon_id()
    try:
        return bpy.context.preferences.addons[addon_id].preferences
    except Exception:
        return None

def remove_folder(path):
    """Delete a directory tree safely and return True on success."""
    if os.path.exists(path) and os.path.isdir(path):
        try:
            shutil.rmtree(path)
            return True
        except Exception:
            return False
    return False

def _parse_version_from_text(manifest_text="", init_text=""):
    """Extract version tuple and string from blender_manifest.toml or __init__.py text."""
    if manifest_text:
        m_id = re.search(r'^\s*id\s*=\s*"([^"]+)"', manifest_text, re.MULTILINE)
        if m_id and m_id.group(1) != "palette_colorizer":
            return None, None
        m_ver = re.search(r'^\s*version\s*=\s*"([^"]+)"', manifest_text, re.MULTILINE)
        if m_ver:
            ver_str = m_ver.group(1).strip()
            parts = [int(p) for p in re.findall(r'\d+', ver_str)[:3]]
            if parts:
                return tuple(parts), ver_str

    if init_text:
        if '"Palette Colorizer"' not in init_text and "'Palette Colorizer'" not in init_text:
            return None, None
        m_ver = re.search(r'["\']version["\']\s*:\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', init_text)
        if m_ver:
            v_tuple = (int(m_ver.group(1)), int(m_ver.group(2)), int(m_ver.group(3)))
            return v_tuple, ".".join(str(x) for x in v_tuple)

    return None, None

def inspect_zip_archive(zip_path):
    """Check if a zip file is a valid Palette Colorizer archive and return (version_tuple, version_str)."""
    if not os.path.exists(zip_path) or not zip_path.lower().endswith(".zip"):
        return None, None

    try:
        with zipfile.ZipFile(zip_path, mode="r") as z:
            names = z.namelist()
            manifest_name = next((n for n in names if n.endswith("blender_manifest.toml")), None)
            init_name = next((n for n in names if n.endswith("__init__.py")), None)

            if not init_name:
                return None, None

            manifest_text = z.read(manifest_name).decode("utf-8", errors="ignore") if manifest_name else ""
            init_text = z.read(init_name).decode("utf-8", errors="ignore")
            return _parse_version_from_text(manifest_text, init_text)
    except Exception:
        return None, None

def get_update_files(force=False):
    """Scan Home and Downloads folders for Palette Colorizer zip archives."""
    global _UPDATE_FILES_CACHE

    if _UPDATE_FILES_CACHE is None or force:
        _UPDATE_FILES_CACHE = []
        home_dir = os.path.expanduser("~")
        search_dirs = []
        if os.path.exists(home_dir):
            search_dirs.append(home_dir)
            dl_dir = os.path.join(home_dir, "Downloads")
            if os.path.exists(dl_dir):
                search_dirs.append(dl_dir)

        seen_paths = set()
        for folder in search_dirs:
            try:
                entries = os.listdir(folder)
            except OSError:
                continue

            for fname in entries:
                lower = fname.lower()
                if not lower.endswith(".zip"):
                    continue
                if not (
                    lower.startswith("palette_colorizer")
                    or lower.startswith("palette-colorizer")
                    or lower.startswith("palette colorizer")
                ):
                    continue

                full_path = os.path.join(folder, fname)
                norm_path = os.path.normcase(os.path.abspath(full_path))
                if norm_path in seen_paths:
                    continue
                seen_paths.add(norm_path)

                v_tuple, v_str = inspect_zip_archive(full_path)
                if v_tuple and v_str:
                    _UPDATE_FILES_CACHE.append((full_path, v_str, v_tuple))

        _UPDATE_FILES_CACHE.sort(key=lambda item: (item[2], item[1]), reverse=True)

    return _UPDATE_FILES_CACHE

def stage_update_zip(zip_path):
    """Extract a validated update zip into the _update staging directory."""
    v_tuple, v_str = inspect_zip_archive(zip_path)
    if not v_tuple or not v_str:
        return False, "Selected file is not a valid Palette Colorizer zip archive."

    addon_path = get_addon_path()
    update_root = os.path.join(addon_path, "_update")
    remove_folder(update_root)
    os.makedirs(update_root, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, mode="r") as z:
            z.extractall(path=update_root)
    except Exception as e:
        remove_folder(update_root)
        return False, f"Failed to extract update zip: {e}"

    return True, f"Palette Colorizer {v_str} is ready to be installed."

def _find_staged_source_dir(update_root):
    """Locate the directory inside _update that contains __init__.py."""
    if not os.path.exists(update_root):
        return None
    if os.path.exists(os.path.join(update_root, "__init__.py")):
        return update_root
    for entry in os.listdir(update_root):
        sub = os.path.join(update_root, entry)
        if os.path.isdir(sub) and os.path.exists(os.path.join(sub, "__init__.py")):
            return sub
    return None

def verify_update():
    """Verify if a staged update exists on startup and set preferences state."""
    prefs = get_prefs()
    if not prefs:
        return

    update_root = os.path.join(get_addon_path(), "_update")
    src_dir = _find_staged_source_dir(update_root)
    if src_dir:
        manifest_path = os.path.join(src_dir, "blender_manifest.toml")
        init_path = os.path.join(src_dir, "__init__.py")
        manifest_text = ""
        init_text = ""
        if os.path.exists(manifest_path):
            with open(manifest_path, "r", encoding="utf-8", errors="ignore") as f:
                manifest_text = f.read()
        if os.path.exists(init_path):
            with open(init_path, "r", encoding="utf-8", errors="ignore") as f:
                init_text = f.read()

        _, v_str = _parse_version_from_text(manifest_text, init_text)
        if v_str:
            prefs.update_msg = f"Palette Colorizer {v_str} is ready to be installed."
            prefs.show_update = True
            return
        remove_folder(update_root)

    if prefs.update_msg:
        prefs.update_msg = ""

def install_update():
    """Apply staged files from _update into the add-on folder and remove _update."""
    addon_path = get_addon_path()
    update_root = os.path.join(addon_path, "_update")
    src_dir = _find_staged_source_dir(update_root)
    if not src_dir:
        return False

    try:
        for item in os.listdir(src_dir):
            if item == "_update":
                continue
            s_item = os.path.join(src_dir, item)
            d_item = os.path.join(addon_path, item)
            if os.path.isdir(s_item):
                if os.path.exists(d_item):
                    shutil.rmtree(d_item)
                shutil.copytree(s_item, d_item)
            else:
                shutil.copy2(s_item, d_item)
        remove_folder(update_root)
        return True
    except Exception as e:
        print(f"Palette Colorizer update error: {e}")
        return False

class PALETTE_OT_remove_update(Operator):
    bl_idname = "palette.remove_update"
    bl_label = "Remove Update"
    bl_description = "Cancel and remove the staged Palette Colorizer update"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return os.path.exists(os.path.join(get_addon_path(), "_update"))

    def execute(self, context):
        update_root = os.path.join(get_addon_path(), "_update")
        remove_folder(update_root)
        prefs = get_prefs()
        if prefs:
            prefs.update_msg = ""
        self.report({'INFO'}, "Removed staged update.")
        return {'FINISHED'}

class PALETTE_OT_use_update(Operator):
    bl_idname = "palette.use_update"
    bl_label = "Use Update"
    bl_options = {'REGISTER'}

    path: StringProperty(name="Path", default="")
    tail: StringProperty(name="Version", default="")

    @classmethod
    def description(cls, context, properties):
        return f"Stage Palette Colorizer {properties.tail} from {properties.path}"

    def execute(self, context):
        prefs = get_prefs()
        if prefs and self.path:
            prefs.update_path = self.path
        return {'FINISHED'}

class PALETTE_OT_rescan_updates(Operator):
    bl_idname = "palette.rescan_updates"
    bl_label = "Re-Scan Updates"
    bl_description = "Scan your Home and Downloads folders for Palette Colorizer zip files"
    bl_options = {'REGISTER'}

    def execute(self, context):
        found = get_update_files(force=True)
        self.report({'INFO'}, f"Found {len(found)} update archive(s).")
        return {'FINISHED'}

class PALETTE_OT_install_update_now(Operator):
    bl_idname = "palette.install_update_now"
    bl_label = "Install Update & Reload"
    bl_description = "Install the staged update immediately and reload Blender scripts"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return os.path.exists(os.path.join(get_addon_path(), "_update"))

    def execute(self, context):
        ok = install_update()
        prefs = get_prefs()
        if prefs:
            prefs.update_msg = ""
            prefs.show_update = False
        if ok:
            self.report({'INFO'}, "Installed Palette Colorizer update. Reloading scripts.")
            try:
                bpy.ops.script.reload()
            except Exception:
                pass
            return {'FINISHED'}
        self.report({'ERROR'}, "Failed to install staged update.")
        return {'CANCELLED'}
