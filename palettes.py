"""
Palette data, category definitions, theme color extraction, and image color sampling.
"""

import json
import colorsys

def get_addon_id():
    """Return the root package name for add-on preferences lookup."""
    return __package__ if __package__ else __name__.split(".")[0]

# ===========================================================================
# Built-in palettes (linear RGB, alpha=1.0)
# ===========================================================================

BUILTIN_PALETTES = {
    "Nord": [
        (0.53, 0.75, 0.82, 1.0),
        (0.56, 0.74, 0.73, 1.0),
        (0.51, 0.63, 0.76, 1.0),
        (0.40, 0.55, 0.75, 1.0),
        (0.75, 0.38, 0.38, 1.0),
        (0.82, 0.53, 0.35, 1.0),
        (0.80, 0.74, 0.45, 1.0),
        (0.53, 0.75, 0.52, 1.0),
    ],
    "Pastel": [
        (1.00, 0.71, 0.76, 1.0),
        (1.00, 0.85, 0.69, 1.0),
        (1.00, 1.00, 0.71, 1.0),
        (0.71, 0.94, 0.71, 1.0),
        (0.71, 0.87, 1.00, 1.0),
        (0.84, 0.71, 1.00, 1.0),
        (1.00, 0.71, 0.92, 1.0),
        (0.71, 0.94, 0.94, 1.0),
    ],
    "Neon": [
        (1.00, 0.07, 0.57, 1.0),
        (0.00, 1.00, 0.50, 1.0),
        (0.00, 0.75, 1.00, 1.0),
        (1.00, 0.90, 0.00, 1.0),
        (1.00, 0.27, 0.00, 1.0),
        (0.60, 0.00, 1.00, 1.0),
        (0.00, 1.00, 1.00, 1.0),
        (1.00, 0.50, 0.00, 1.0),
    ],
    "Earthy": [
        (0.55, 0.27, 0.07, 1.0),
        (0.72, 0.52, 0.04, 1.0),
        (0.40, 0.60, 0.22, 1.0),
        (0.74, 0.72, 0.42, 1.0),
        (0.50, 0.38, 0.28, 1.0),
        (0.82, 0.71, 0.55, 1.0),
        (0.27, 0.45, 0.30, 1.0),
        (0.60, 0.47, 0.35, 1.0),
    ],
    "Solarized": [
        (0.00, 0.47, 0.54, 1.0),
        (0.15, 0.55, 0.82, 1.0),
        (0.16, 0.63, 0.60, 1.0),
        (0.52, 0.60, 0.00, 1.0),
        (0.71, 0.54, 0.00, 1.0),
        (0.80, 0.29, 0.09, 1.0),
        (0.83, 0.21, 0.51, 1.0),
        (0.42, 0.44, 0.77, 1.0),
    ],
    "Candy": [
        (1.00, 0.41, 0.71, 1.0),
        (0.39, 0.58, 0.93, 1.0),
        (0.20, 0.80, 0.60, 1.0),
        (1.00, 0.75, 0.20, 1.0),
        (0.80, 0.20, 0.80, 1.0),
        (0.20, 0.80, 0.80, 1.0),
        (1.00, 0.50, 0.20, 1.0),
        (0.50, 0.80, 0.20, 1.0),
    ],
    "Grayscale": [
        (0.00, 0.00, 0.00, 1.0),
        (0.14, 0.14, 0.14, 1.0),
        (0.27, 0.27, 0.27, 1.0),
        (0.40, 0.40, 0.40, 1.0),
        (0.53, 0.53, 0.53, 1.0),
        (0.65, 0.65, 0.65, 1.0),
        (0.80, 0.80, 0.80, 1.0),
        (1.00, 1.00, 1.00, 1.0),
    ],
    "Ruby": [
        (0.90, 0.10, 0.10, 1.0),
        (0.75, 0.18, 0.18, 1.0),
        (1.00, 0.27, 0.20, 1.0),
        (0.80, 0.40, 0.40, 1.0),
        (0.60, 0.08, 0.08, 1.0),
        (1.00, 0.55, 0.45, 1.0),
        (0.70, 0.20, 0.30, 1.0),
        (0.95, 0.70, 0.65, 1.0),
    ],
    "Ocean": [
        (0.05, 0.30, 0.70, 1.0),
        (0.10, 0.50, 0.85, 1.0),
        (0.00, 0.65, 0.90, 1.0),
        (0.20, 0.20, 0.55, 1.0),
        (0.35, 0.70, 0.90, 1.0),
        (0.00, 0.45, 0.65, 1.0),
        (0.55, 0.85, 0.95, 1.0),
        (0.10, 0.35, 0.80, 1.0),
    ],
    "Forest": [
        (0.10, 0.40, 0.15, 1.0),
        (0.25, 0.60, 0.20, 1.0),
        (0.45, 0.72, 0.30, 1.0),
        (0.05, 0.28, 0.10, 1.0),
        (0.55, 0.75, 0.40, 1.0),
        (0.30, 0.50, 0.25, 1.0),
        (0.65, 0.80, 0.50, 1.0),
        (0.18, 0.45, 0.30, 1.0),
    ],
    "Cyberpunk": [
        (1.00, 0.00, 0.50, 1.0),
        (0.00, 0.90, 1.00, 1.0),
        (1.00, 0.90, 0.05, 1.0),
        (0.45, 0.05, 0.90, 1.0),
        (0.05, 0.30, 0.95, 1.0),
        (1.00, 0.20, 0.10, 1.0),
        (0.10, 0.80, 0.60, 1.0),
        (0.80, 0.10, 0.70, 1.0),
    ],
    "Sunset": [
        (0.20, 0.10, 0.40, 1.0),
        (0.50, 0.15, 0.45, 1.0),
        (0.80, 0.25, 0.35, 1.0),
        (0.95, 0.45, 0.25, 1.0),
        (1.00, 0.70, 0.20, 1.0),
        (1.00, 0.85, 0.40, 1.0),
        (0.90, 0.40, 0.55, 1.0),
        (0.35, 0.20, 0.50, 1.0),
    ],
    "Autumn": [
        (0.70, 0.25, 0.05, 1.0),
        (0.85, 0.45, 0.10, 1.0),
        (0.90, 0.65, 0.15, 1.0),
        (0.55, 0.18, 0.10, 1.0),
        (0.40, 0.30, 0.15, 1.0),
        (0.60, 0.50, 0.20, 1.0),
        (0.80, 0.35, 0.15, 1.0),
        (0.30, 0.20, 0.10, 1.0),
    ],
    "Synthwave": [
        (0.15, 0.05, 0.30, 1.0),
        (0.45, 0.05, 0.55, 1.0),
        (0.90, 0.10, 0.60, 1.0),
        (1.00, 0.35, 0.70, 1.0),
        (0.10, 0.85, 0.95, 1.0),
        (0.00, 0.50, 0.80, 1.0),
        (0.95, 0.60, 0.20, 1.0),
        (0.70, 0.20, 0.85, 1.0),
    ],
    "Desert": [
        (0.85, 0.65, 0.40, 1.0),
        (0.75, 0.45, 0.25, 1.0),
        (0.60, 0.30, 0.15, 1.0),
        (0.90, 0.78, 0.55, 1.0),
        (0.70, 0.55, 0.35, 1.0),
        (0.50, 0.40, 0.30, 1.0),
        (0.45, 0.50, 0.40, 1.0),
        (0.80, 0.40, 0.30, 1.0),
    ],
    "Retro": [
        (0.85, 0.60, 0.10, 1.0),
        (0.80, 0.30, 0.15, 1.0),
        (0.35, 0.50, 0.35, 1.0),
        (0.60, 0.35, 0.20, 1.0),
        (0.90, 0.85, 0.70, 1.0),
        (0.20, 0.45, 0.50, 1.0),
        (0.70, 0.20, 0.25, 1.0),
        (0.40, 0.25, 0.15, 1.0),
    ],
    "Lavender": [
        (0.80, 0.75, 0.90, 1.0),
        (0.65, 0.55, 0.80, 1.0),
        (0.50, 0.40, 0.70, 1.0),
        (0.35, 0.25, 0.55, 1.0),
        (0.88, 0.82, 0.95, 1.0),
        (0.55, 0.45, 0.75, 1.0),
        (0.75, 0.60, 0.85, 1.0),
        (0.40, 0.30, 0.60, 1.0),
    ],
    "Emerald": [
        (0.05, 0.35, 0.25, 1.0),
        (0.10, 0.55, 0.35, 1.0),
        (0.15, 0.75, 0.45, 1.0),
        (0.40, 0.85, 0.60, 1.0),
        (0.05, 0.25, 0.20, 1.0),
        (0.20, 0.65, 0.50, 1.0),
        (0.60, 0.90, 0.75, 1.0),
        (0.10, 0.45, 0.40, 1.0),
    ],
    "Coffee": [
        (0.22, 0.14, 0.10, 1.0),
        (0.35, 0.22, 0.15, 1.0),
        (0.50, 0.32, 0.22, 1.0),
        (0.65, 0.45, 0.30, 1.0),
        (0.80, 0.62, 0.45, 1.0),
        (0.90, 0.78, 0.65, 1.0),
        (0.42, 0.28, 0.18, 1.0),
        (0.28, 0.18, 0.12, 1.0),
    ],
    "Sakura": [
        (1.00, 0.85, 0.90, 1.0),
        (0.98, 0.70, 0.80, 1.0),
        (0.95, 0.55, 0.70, 1.0),
        (0.85, 0.40, 0.60, 1.0),
        (0.45, 0.30, 0.35, 1.0),
        (0.65, 0.75, 0.60, 1.0),
        (1.00, 0.92, 0.95, 1.0),
        (0.75, 0.35, 0.50, 1.0),
    ],
    "Monokai": [
        (0.98, 0.15, 0.45, 1.0),
        (0.65, 0.85, 0.15, 1.0),
        (0.90, 0.85, 0.35, 1.0),
        (0.40, 0.80, 0.90, 1.0),
        (0.68, 0.50, 0.90, 1.0),
        (0.95, 0.55, 0.15, 1.0),
        (0.45, 0.45, 0.40, 1.0),
        (0.95, 0.95, 0.90, 1.0),
    ],
    "Dracula": [
        (0.16, 0.16, 0.21, 1.0),
        (0.38, 0.44, 0.64, 1.0),
        (0.55, 0.91, 0.99, 1.0),
        (0.31, 0.98, 0.48, 1.0),
        (1.00, 0.73, 0.42, 1.0),
        (1.00, 0.47, 0.77, 1.0),
        (0.74, 0.58, 0.98, 1.0),
        (0.95, 0.95, 0.95, 1.0),
    ],
    "Gruvbox": [
        (0.80, 0.14, 0.11, 1.0),
        (0.60, 0.60, 0.10, 1.0),
        (0.84, 0.60, 0.13, 1.0),
        (0.27, 0.52, 0.53, 1.0),
        (0.70, 0.40, 0.55, 1.0),
        (0.41, 0.60, 0.50, 1.0),
        (0.82, 0.35, 0.10, 1.0),
        (0.92, 0.86, 0.70, 1.0),
    ],
    "Tokyo Night": [
        (0.10, 0.11, 0.18, 1.0),
        (0.45, 0.65, 0.95, 1.0),
        (0.73, 0.55, 0.95, 1.0),
        (0.45, 0.85, 0.85, 1.0),
        (0.95, 0.45, 0.60, 1.0),
        (0.98, 0.70, 0.40, 1.0),
        (0.25, 0.35, 0.55, 1.0),
        (0.80, 0.85, 0.95, 1.0),
    ],
    "Vaporwave": [
        (0.40, 0.85, 0.90, 1.0),
        (0.95, 0.55, 0.80, 1.0),
        (0.70, 0.45, 0.85, 1.0),
        (0.55, 0.90, 0.75, 1.0),
        (1.00, 0.75, 0.85, 1.0),
        (0.30, 0.60, 0.80, 1.0),
        (0.85, 0.40, 0.65, 1.0),
        (0.95, 0.90, 0.95, 1.0),
    ],
    "Clay": [
        (0.75, 0.35, 0.25, 1.0),
        (0.60, 0.25, 0.18, 1.0),
        (0.80, 0.50, 0.35, 1.0),
        (0.85, 0.65, 0.45, 1.0),
        (0.50, 0.45, 0.40, 1.0),
        (0.65, 0.55, 0.50, 1.0),
        (0.40, 0.20, 0.15, 1.0),
        (0.90, 0.75, 0.60, 1.0),
    ],
    "Midnight": [
        (0.05, 0.07, 0.15, 1.0),
        (0.10, 0.15, 0.30, 1.0),
        (0.15, 0.25, 0.50, 1.0),
        (0.25, 0.45, 0.75, 1.0),
        (0.40, 0.65, 0.90, 1.0),
        (0.65, 0.80, 0.95, 1.0),
        (0.20, 0.35, 0.60, 1.0),
        (0.85, 0.90, 1.00, 1.0),
    ],
    "Citrus": [
        (0.60, 0.85, 0.15, 1.0),
        (0.95, 0.90, 0.10, 1.0),
        (1.00, 0.65, 0.05, 1.0),
        (1.00, 0.40, 0.10, 1.0),
        (0.95, 0.20, 0.30, 1.0),
        (0.35, 0.75, 0.25, 1.0),
        (1.00, 0.80, 0.25, 1.0),
        (0.85, 0.30, 0.15, 1.0),
    ],
    "Copper": [
        (0.72, 0.45, 0.30, 1.0),
        (0.55, 0.30, 0.18, 1.0),
        (0.85, 0.55, 0.35, 1.0),
        (0.30, 0.60, 0.55, 1.0),
        (0.20, 0.48, 0.45, 1.0),
        (0.45, 0.75, 0.68, 1.0),
        (0.40, 0.22, 0.12, 1.0),
        (0.90, 0.68, 0.50, 1.0),
    ],
    "Arctic": [
        (0.85, 0.92, 0.98, 1.0),
        (0.65, 0.80, 0.92, 1.0),
        (0.45, 0.68, 0.85, 1.0),
        (0.25, 0.50, 0.75, 1.0),
        (0.12, 0.30, 0.55, 1.0),
        (0.08, 0.18, 0.38, 1.0),
        (0.55, 0.75, 0.88, 1.0),
        (0.95, 0.98, 1.00, 1.0),
    ],
}

PALETTE_CATEGORIES = [
    ("Technical & Dark", [
        "Nord", "Solarized", "Monokai", "Dracula",
        "Gruvbox", "Tokyo Night", "Midnight", "Grayscale",
    ]),
    ("Vibrant & Neon", [
        "Neon", "Cyberpunk", "Synthwave", "Vaporwave",
        "Candy", "Citrus", "Ruby",
    ]),
    ("Pastel & Soft", [
        "Pastel", "Lavender", "Sakura", "Arctic", "Ocean",
    ]),
    ("Earth & Warm", [
        "Earthy", "Forest", "Emerald", "Sunset", "Autumn",
        "Desert", "Retro", "Coffee", "Clay", "Copper",
    ]),
]

# ===========================================================================
# Palette serialization and conversion helpers
# ===========================================================================

def palette_to_dict(name, colors):
    """Convert palette name and color list to a JSON-serializable dictionary."""
    return {
        "name": name,
        "version": 1,
        "colors": [[round(c, 4) for c in rgba] for rgba in colors],
    }

def dict_to_palette(data):
    """Parse dictionary from JSON and return palette name and colors."""
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object.")
    colors_raw = data.get("colors")
    if not colors_raw or not isinstance(colors_raw, list):
        raise ValueError("Missing or invalid colors list.")
    colors = []
    for entry in colors_raw:
        if len(entry) == 3:
            entry = list(entry) + [1.0]
        if len(entry) != 4:
            raise ValueError(f"Color entry must have 3 or 4 components: {entry}")
        colors.append(tuple(max(0.0, min(1.0, float(v))) for v in entry))
    name = data.get("name", "Imported")
    return name, colors

def load_colors_into_custom(settings, colors):
    """Replace custom palette slots with the provided RGBA color list."""
    settings.custom_colors.clear()
    for rgba in colors:
        item = settings.custom_colors.add()
        item.color = rgba
    settings.custom_color_index = 0

def get_theme_palette_colors(context):
    """Extract representative colors from the active Blender user interface theme."""
    try:
        theme = context.preferences.themes[0]
        v3d = theme.view_3d
        ui = theme.user_interface
        return [
            tuple(v3d.object_active[:3]) + (1.0,),
            tuple(v3d.object_selected[:3]) + (1.0,),
            tuple(ui.axis_x[:3]) + (1.0,),
            tuple(ui.axis_y[:3]) + (1.0,),
            tuple(ui.axis_z[:3]) + (1.0,),
            tuple(ui.wcol_regular.inner[:3]) + (1.0,),
            tuple(ui.wcol_tool.inner[:3]) + (1.0,),
            tuple(v3d.space.gradients.high_gradient[:3]) + (1.0,),
        ]
    except Exception:
        return [(0.8, 0.8, 0.8, 1.0)] * 8

def extract_colors_from_image(image, count=8):
    """Sample dominant colors across hue buckets from a Blender Image datablock."""
    if not image or not image.has_data:
        return []
    width, height = image.size
    if width <= 0 or height <= 0:
        return []

    total_pixels = width * height
    channels = image.channels
    if channels < 3:
        return []

    raw = image.pixels[:]
    step = max(1, total_pixels // 2048)

    buckets = [[] for _ in range(count)]
    fallback_samples = []

    for p_idx in range(0, total_pixels, step):
        base = p_idx * channels
        r = max(0.0, min(1.0, float(raw[base])))
        g = max(0.0, min(1.0, float(raw[base + 1])))
        b = max(0.0, min(1.0, float(raw[base + 2])))
        a = float(raw[base + 3]) if channels >= 4 else 1.0
        if a < 0.2:
            continue

        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        fallback_samples.append((r, g, b, 1.0))
        if s < 0.08 or v < 0.08 or v > 0.98:
            continue

        b_idx = min(count - 1, int(h * count))
        buckets[b_idx].append((s * v, r, g, b))

    result = []
    for bucket in buckets:
        if bucket:
            bucket.sort(key=lambda x: x[0], reverse=True)
            mid = bucket[len(bucket) // 4]
            result.append((mid[1], mid[2], mid[3], 1.0))

    if len(result) < count and fallback_samples:
        stride = max(1, len(fallback_samples) // count)
        for i in range(0, len(fallback_samples), stride):
            if len(result) >= count:
                break
            c = fallback_samples[i]
            if c not in result:
                result.append(c)

    return result[:count] if result else [(0.8, 0.8, 0.8, 1.0)] * count

# ===========================================================================
# Enum callback
# ===========================================================================

_PALETTE_ENUM_ITEMS_CACHE = []

def get_palette_items(self, context):
    """Build categorized enum items for the palette selector."""
    global _PALETTE_ENUM_ITEMS_CACHE
    items = []

    for cat_name, pal_names in PALETTE_CATEGORIES:
        items.append(("", cat_name, ""))
        for k in pal_names:
            if k in BUILTIN_PALETTES:
                items.append((k, k, f"Built-in palette: {k}"))

    items.append(("", "Dynamic & Custom", ""))
    items.append(("THEME", "Current Theme", "Extract colors from the active Blender theme"))
    items.append(("CUSTOM", "Custom Palette", "Use the editable custom palette slots"))

    addon_id = get_addon_id()
    try:
        if context and addon_id in context.preferences.addons:
            prefs = context.preferences.addons[addon_id].preferences
            if prefs and prefs.saved_palettes:
                items.append(("", "Saved Library", ""))
                for entry in prefs.saved_palettes:
                    key = f"SAVED::{entry.name}"
                    items.append((key, f"[S] {entry.name}", f"Saved palette: {entry.name}"))
    except Exception:
        pass

    _PALETTE_ENUM_ITEMS_CACHE = items
    return _PALETTE_ENUM_ITEMS_CACHE

def get_active_palette_colors(settings, context=None):
    """Return the active list of RGBA tuples for the selected palette."""
    name = settings.palette_name
    if name == "CUSTOM":
        return [tuple(item.color) for item in settings.custom_colors] or [(0.8, 0.8, 0.8, 1.0)]
    if name == "THEME" and context:
        return get_theme_palette_colors(context)
    if name.startswith("SAVED::") and context:
        saved_name = name[7:]
        addon_id = get_addon_id()
        try:
            prefs = context.preferences.addons[addon_id].preferences
            for entry in prefs.saved_palettes:
                if entry.name == saved_name:
                    _, colors = dict_to_palette(json.loads(entry.json_data))
                    return colors
        except Exception:
            pass
    return BUILTIN_PALETTES.get(name, BUILTIN_PALETTES["Nord"])
