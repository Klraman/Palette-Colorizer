"""
Generate reproducible Gumroad marketing assets for Palette Colorizer.
This script renders 3D product renders using Blender background mode
and composites cover, thumbnail, showcase screenshots, and an animated GIF.
"""

import os
import subprocess
import json
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

BLENDER_EXE = r"C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe"

PALETTES = {
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
}

def get_font(size, bold=False):
    font_file = "segoeuib.ttf" if bold else "segoeui.ttf"
    path = os.path.join(r"C:\Windows\Fonts", font_file)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    font_file = "arialbd.ttf" if bold else "arial.ttf"
    path = os.path.join(r"C:\Windows\Fonts", font_file)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def draw_pill(draw, x, y, text, font, bg_color=(30, 35, 45), text_color=(255, 255, 255), pad_x=16, pad_y=8):
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    radius = (h + pad_y * 2) // 2
    draw.rounded_rectangle([x, y, x + w + pad_x * 2, y + h + pad_y * 2], radius=radius, fill=bg_color)
    draw.text((x + pad_x, y + pad_y - bbox[1]), text, fill=text_color, font=font)
    return x + w + pad_x * 2 + 12

def draw_palette_swatches(draw, x, y, colors, swatch_w=34, swatch_h=20, spacing=6, radius=4):
    for i, c in enumerate(colors):
        rgb = tuple(int(v * 255) for v in c[:3])
        draw.rounded_rectangle(
            [x + i * (swatch_w + spacing), y, x + i * (swatch_w + spacing) + swatch_w, y + swatch_h],
            radius=radius,
            fill=rgb,
            outline=(255, 255, 255, 60)
        )

def create_cover():
    render_path = os.path.join(ASSETS_DIR, "renders", "candy_16_9.png")
    im = Image.open(render_path).convert("RGBA")
    
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    
    # Top bar gradient
    for yy in range(180):
        alpha = int(220 * (1.0 - yy / 180))
        odraw.line([(0, yy), (im.width, yy)], fill=(12, 14, 18, alpha))
        
    # Bottom card gradient
    for yy in range(530, 720):
        alpha = int(230 * ((yy - 530) / 190))
        odraw.line([(0, yy), (im.width, yy)], fill=(10, 12, 16, alpha))

    im = Image.alpha_composite(im, overlay)
    draw = ImageDraw.Draw(im)

    font_badge = get_font(18, bold=True)
    draw_pill(draw, 50, 35, "BLENDER ADD-ON", font_badge, bg_color=(255, 107, 107), text_color=(255, 255, 255))
    draw_pill(draw, 225, 35, "VERSION 5.2", font_badge, bg_color=(40, 48, 65), text_color=(200, 220, 255))
    draw_pill(draw, 365, 35, "CYCLES & EEVEE", font_badge, bg_color=(35, 42, 55), text_color=(160, 240, 200))

    font_title = get_font(52, bold=True)
    font_sub = get_font(23, bold=False)
    
    draw.text((50, 90), "Palette Colorizer", fill=(255, 255, 255), font=font_title)
    draw.text((52, 155), "Apply named color palettes to objects in viewport and renders.", fill=(200, 210, 225), font=font_sub)

    # Bottom feature bar with clean non-overlapping 3-column layout
    font_feat = get_font(19, bold=True)
    font_small = get_font(15, bold=False)

    card_y = 565
    draw.rounded_rectangle([40, card_y, 1240, card_y + 120], radius=16, fill=(15, 18, 24, 235), outline=(50, 60, 80))
    
    # Col 1: Palettes
    draw.text((65, card_y + 18), "30 Built-in Palettes", fill=(255, 255, 255), font=font_feat)
    draw.text((65, card_y + 46), "30 Curated Harmonies + Active Blender Theme", fill=(160, 175, 195), font=font_small)
    draw_palette_swatches(draw, 65, card_y + 74, PALETTES["Candy"], swatch_w=24, swatch_h=16, spacing=4)

    # Col 2: Materials
    draw.text((500, card_y + 18), "1-Click Principled BSDF", fill=(255, 255, 255), font=font_feat)
    draw.text((500, card_y + 46), "Assign materials for Cycles & EEVEE", fill=(160, 175, 195), font=font_small)
    draw.text((500, card_y + 74), "Full Base Color node automation", fill=(130, 145, 165), font=font_small)

    # Col 3: Sharing
    draw.text((890, card_y + 18), "JSON Share & Library", fill=(255, 255, 255), font=font_feat)
    draw.text((890, card_y + 46), "Copy or paste strings to Discord", fill=(160, 175, 195), font=font_small)
    draw.text((890, card_y + 74), "Save palettes across project files", fill=(130, 145, 165), font=font_small)

    out_path = os.path.join(ASSETS_DIR, "cover.png")
    im.convert("RGB").save(out_path, quality=95)
    print("Updated cover.png:", out_path)

def create_thumbnail():
    icon_script = os.path.join(ASSETS_DIR, "render_icon.py")
    if os.path.exists(icon_script):
        cmd = [BLENDER_EXE, "--background", "--python", icon_script]
        subprocess.run(cmd, check=True)
        print("Updated thumbnail.png (clean 3D icon via Blender):", os.path.join(ASSETS_DIR, "thumbnail.png"))
    else:
        print("Warning: render_icon.py not found at", icon_script)

def create_showcase_screenshots():
    # Screenshot 1: Palettes Showcase (Nord) with Blender UI Panel simulation
    nord_path = os.path.join(ASSETS_DIR, "renders", "nord_16_9.png")
    im1 = Image.open(nord_path).convert("RGBA")
    draw1 = ImageDraw.Draw(im1)
    
    font_header = get_font(34, bold=True)
    font_desc = get_font(19, bold=False)
    
    draw_pill(draw1, 50, 40, "PALETTE PREVIEW", get_font(18, bold=True), bg_color=(88, 166, 255), text_color=(255, 255, 255))
    draw1.text((50, 85), "Nord Palette: Clean Viewport Colors", fill=(255, 255, 255), font=font_header)
    draw1.text((50, 130), "Assign harmonious color palettes to objects in one click.", fill=(200, 215, 230), font=font_desc)
    draw_palette_swatches(draw1, 50, 168, PALETTES["Nord"], swatch_w=34, swatch_h=20, spacing=6)

    # Draw Blender Sidebar N-Panel overlay on right
    panel_x = 920
    panel_y = 40
    panel_w = 320
    panel_h = 640
    draw1.rounded_rectangle([panel_x, panel_y, panel_x + panel_w, panel_y + panel_h], radius=10, fill=(30, 32, 38, 245), outline=(70, 75, 90))
    
    font_p_title = get_font(18, bold=True)
    font_p_body = get_font(15, bold=False)
    font_p_bold = get_font(15, bold=True)
    
    # Panel Title
    draw1.rectangle([panel_x, panel_y, panel_x + panel_w, panel_y + 36], fill=(42, 45, 54))
    draw1.text((panel_x + 15, panel_y + 8), "Palette Colorizer", fill=(240, 240, 240), font=font_p_title)
    
    # Palette Box
    py = panel_y + 50
    draw1.rounded_rectangle([panel_x + 12, py, panel_x + panel_w - 12, py + 75], radius=6, fill=(24, 26, 30), outline=(50, 54, 65))
    draw1.text((panel_x + 22, py + 8), "Palette", fill=(180, 190, 205), font=font_p_bold)
    # Dropdown
    draw1.rounded_rectangle([panel_x + 22, py + 32, panel_x + panel_w - 22, py + 62], radius=4, fill=(45, 48, 58), outline=(65, 70, 85))
    draw1.text((panel_x + 32, py + 38), "Nord", fill=(255, 255, 255), font=font_p_body)
    draw1.text((panel_x + panel_w - 45, py + 38), "v", fill=(180, 190, 205), font=font_p_body)
    
    # Assignment Box
    py += 88
    draw1.rounded_rectangle([panel_x + 12, py, panel_x + panel_w - 12, py + 75], radius=6, fill=(24, 26, 30), outline=(50, 54, 65))
    draw1.text((panel_x + 22, py + 8), "Assignment", fill=(180, 190, 205), font=font_p_bold)
    draw1.rounded_rectangle([panel_x + 22, py + 32, panel_x + panel_w - 22, py + 62], radius=4, fill=(45, 48, 58), outline=(65, 70, 85))
    draw1.text((panel_x + 32, py + 38), "Sequential", fill=(255, 255, 255), font=font_p_body)
    
    # Buttons
    py += 95
    # Apply Palette button (large, prominent)
    draw1.rounded_rectangle([panel_x + 12, py, panel_x + panel_w - 12, py + 46], radius=6, fill=(65, 115, 215))
    draw1.text((panel_x + 85, py + 12), ">  Apply Palette", fill=(255, 255, 255), font=font_p_title)
    
    py += 54
    # Reset button
    draw1.rounded_rectangle([panel_x + 12, py, panel_x + panel_w - 12, py + 40], radius=6, fill=(50, 54, 65))
    draw1.text((panel_x + 115, py + 10), "Reset", fill=(220, 220, 220), font=font_p_body)
    
    py += 48
    # Apply Materials button
    draw1.rounded_rectangle([panel_x + 12, py, panel_x + panel_w - 12, py + 44], radius=6, fill=(40, 120, 95))
    draw1.text((panel_x + 35, py + 12), "Apply Materials (Cycles / EEVEE)", fill=(240, 255, 245), font=font_p_body)
    
    py += 60
    # Share box
    draw1.rounded_rectangle([panel_x + 12, py, panel_x + panel_w - 12, py + 120], radius=6, fill=(24, 26, 30), outline=(50, 54, 65))
    draw1.text((panel_x + 22, py + 8), "Share Palettes", fill=(180, 190, 205), font=font_p_bold)
    draw1.rounded_rectangle([panel_x + 22, py + 35, panel_x + panel_w - 22, py + 70], radius=4, fill=(45, 48, 58))
    draw1.text((panel_x + 40, py + 43), "Copy Current Palette as String", fill=(210, 225, 245), font=font_p_body)
    draw1.rounded_rectangle([panel_x + 22, py + 76, panel_x + panel_w - 22, py + 110], radius=4, fill=(45, 48, 58))
    draw1.text((panel_x + 45, py + 84), "Export / Import .json File", fill=(210, 225, 245), font=font_p_body)

    out1 = os.path.join(ASSETS_DIR, "screenshot1_nord_palettes.png")
    im1.convert("RGB").save(out1, quality=95)

    # Screenshot 2: Neon Palette & Materials
    neon_path = os.path.join(ASSETS_DIR, "renders", "neon_16_9.png")
    im2 = Image.open(neon_path).convert("RGBA")
    draw2 = ImageDraw.Draw(im2)
    draw_pill(draw2, 50, 40, "RENDER READY", get_font(18, bold=True), bg_color=(255, 120, 200), text_color=(255, 255, 255))
    draw2.text((50, 85), "Cycles & EEVEE Material Creation", fill=(255, 255, 255), font=font_header)
    draw2.text((50, 130), "Create Principled BSDF materials automatically for each colored object.", fill=(200, 215, 230), font=font_desc)
    draw_palette_swatches(draw2, 50, 168, PALETTES["Neon"], swatch_w=34, swatch_h=20, spacing=6)
    
    out2 = os.path.join(ASSETS_DIR, "screenshot2_materials_render.png")
    im2.convert("RGB").save(out2, quality=95)

    # Screenshot 3: Ocean Palette & Sharing
    ocean_path = os.path.join(ASSETS_DIR, "renders", "ocean_16_9.png")
    im3 = Image.open(ocean_path).convert("RGBA")
    draw3 = ImageDraw.Draw(im3)
    draw_pill(draw3, 50, 40, "TEAM WORKFLOW", get_font(18, bold=True), bg_color=(50, 200, 150), text_color=(255, 255, 255))
    draw3.text((50, 85), "Share Palettes via JSON and Library", fill=(255, 255, 255), font=font_header)
    draw3.text((50, 130), "Export JSON files or copy compact strings to share on Discord.", fill=(200, 215, 230), font=font_desc)
    draw_palette_swatches(draw3, 50, 168, PALETTES["Ocean"], swatch_w=34, swatch_h=20, spacing=6)
    
    out3 = os.path.join(ASSETS_DIR, "screenshot3_sharing_workflow.png")
    im3.convert("RGB").save(out3, quality=95)

    print("Updated screenshots 1, 2, 3.")

def create_animated_gif():
    palette_keys = ["Candy", "Nord", "Neon", "Pastel", "Ocean", "Forest", "Ruby"]
    frames = []
    
    font_pill = get_font(15, bold=True)
    font_name = get_font(22, bold=True)

    for key in palette_keys:
        path = os.path.join(ASSETS_DIR, "renders", f"{key.lower()}_16_9.png")
        if not os.path.exists(path):
            continue
        im = Image.open(path).convert("RGBA")
        im = im.resize((960, 540), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(im)

        # Card at top-left with proper spacing
        card_w = 340
        card_h = 92
        draw.rounded_rectangle([30, 30, 30 + card_w, 30 + card_h], radius=12, fill=(15, 18, 25, 235), outline=(60, 70, 90))
        
        # Pill
        next_x = draw_pill(draw, 45, 42, "ACTIVE PALETTE", font_pill, bg_color=(255, 107, 107), text_color=(255, 255, 255), pad_x=10, pad_y=4)
        draw.text((next_x + 8, 42), key, fill=(255, 255, 255), font=font_name)
        
        # Swatches
        draw_palette_swatches(draw, 45, 80, PALETTES[key], swatch_w=28, swatch_h=16, spacing=4, radius=3)

        frames.append(im.convert("RGB"))

    gif_path = os.path.join(ASSETS_DIR, "palette_colorizer_demo.gif")
    if frames:
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=900,
            loop=0
        )
        print("Updated animated GIF:", gif_path)

if __name__ == "__main__":
    create_cover()
    create_thumbnail()
    create_showcase_screenshots()
    create_animated_gif()
    print("All refined assets generated successfully!")
