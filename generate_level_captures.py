import json
import os
import math
from PIL import Image, ImageDraw, ImageFont

PROJECT_DIR = r"D:\Unity\Lore & Tactics"
MONITOR_DIR = r"D:\Unity\lore-and-tactics-monitor"
OUT_DIR = os.path.join(MONITOR_DIR, "screenshots", "levels")
os.makedirs(OUT_DIR, exist_ok=True)

# Load data
with open(os.path.join(PROJECT_DIR, "Assets", "Resources", "Data", "levels.json"), "r", encoding="utf-8-sig") as f:
    levels_data = json.load(f)["levels"]

with open(os.path.join(PROJECT_DIR, "Assets", "Resources", "Data", "units.json"), "r", encoding="utf-8-sig") as f:
    units_list = json.load(f)["units"]
    units_dict = {u["id"]: u for u in units_list}

SPRITES_DIR = os.path.join(PROJECT_DIR, "Assets", "Resources", "Sprites")
UNITS_SPRITES = os.path.join(SPRITES_DIR, "Units")
ICONS_SPRITES = os.path.join(SPRITES_DIR, "Icons")

def get_sprite(category, name):
    path = os.path.join(SPRITES_DIR, category, name + ".png")
    if os.path.exists(path):
        return Image.open(path).convert("RGBA")
    return None

def get_unit_sprite(unit_id):
    path = os.path.join(UNITS_SPRITES, unit_id + ".png")
    if os.path.exists(path):
        return Image.open(path).convert("RGBA")
    # fallback
    path2 = os.path.join(ICONS_SPRITES, f"icon_unit_{unit_id}.png")
    if os.path.exists(path2):
        return Image.open(path2).convert("RGBA")
    return None

def get_icon(icon_name):
    path = os.path.join(ICONS_SPRITES, icon_name + ".png")
    if os.path.exists(path):
        return Image.open(path).convert("RGBA")
    return None

# Biome colors
BIOME_CONFIGS = {
    "grassland": {
        "bg": (26, 28, 44),
        "grass": (46, 80, 36),
        "grass_grid": (40, 72, 32),
        "rock": (85, 95, 110),
        "tree": (28, 62, 24),
        "water": (41, 128, 185),
        "goldmine": (212, 172, 13),
        "barricade": (120, 80, 45)
    },
    "swamp": {
        "bg": (20, 30, 21),
        "grass": (40, 58, 38),
        "grass_grid": (34, 50, 32),
        "rock": (70, 80, 75),
        "tree": (22, 45, 25),
        "water": (35, 100, 110),
        "goldmine": (195, 155, 20),
        "barricade": (95, 75, 45)
    },
    "snow": {
        "bg": (26, 36, 51),
        "grass": (65, 85, 105),
        "grass_grid": (55, 75, 95),
        "rock": (110, 125, 145),
        "tree": (40, 65, 75),
        "water": (52, 152, 219),
        "goldmine": (225, 180, 25),
        "barricade": (130, 95, 60)
    },
    "lava": {
        "bg": (28, 16, 20),
        "grass": (60, 35, 38),
        "grass_grid": (50, 28, 30),
        "rock": (90, 50, 55),
        "tree": (45, 25, 25),
        "water": (211, 84, 0), # magma
        "goldmine": (241, 196, 15),
        "barricade": (140, 60, 40)
    }
}

def get_level_biome(lvl_id):
    l = lvl_id.lower()
    if l in ["level03", "level04", "level05"]:
        return "swamp"
    elif l in ["level06", "level07", "level08"]:
        return "snow"
    elif l in ["level09", "level10"]:
        return "lava"
    return "grassland"

W, H = 540, 960

# Load default font
font_large = ImageFont.load_default()
font_med = ImageFont.load_default()
font_small = ImageFont.load_default()

def draw_top_bar(draw, img, gold=240, wood=120, time_str="01:45", castle_hp=1500, fort_hp=1200):
    # Top bar panel
    draw.rectangle([0, 0, W, 80], fill=(16, 20, 29, 255))
    draw.rectangle([0, 78, W, 80], fill=(255, 205, 117, 180))

    # Gear button
    draw.rounded_rectangle([12, 16, 56, 60], radius=4, fill=(37, 48, 72, 255), outline=(60, 75, 105))
    gear_icon = get_icon("icon_gear")
    if gear_icon:
        gear_resized = gear_icon.resize((26, 26), Image.NEAREST)
        img.paste(gear_resized, (21, 25), gear_resized)

    # Gold chip
    draw.rounded_rectangle([66, 18, 165, 58], radius=6, fill=(25, 34, 51, 255))
    gold_icon = get_icon("icon_gold")
    if gold_icon:
        img.paste(gold_icon.resize((24, 24), Image.NEAREST), (72, 26), gold_icon.resize((24, 24), Image.NEAREST))
    draw.text((102, 28), str(gold), fill=(255, 215, 0), font=font_med)

    # Wood chip
    draw.rounded_rectangle([172, 18, 265, 58], radius=6, fill=(25, 34, 51, 255))
    wood_icon = get_icon("icon_wood")
    if wood_icon:
        img.paste(wood_icon.resize((24, 24), Image.NEAREST), (178, 26), wood_icon.resize((24, 24), Image.NEAREST))
    draw.text((208, 28), str(wood), fill=(46, 204, 113), font=font_med)

    # Timer chip
    draw.rounded_rectangle([272, 18, 355, 58], radius=6, fill=(25, 34, 51, 255))
    draw.text((285, 28), f"⏱ {time_str}", fill=(255, 255, 255), font=font_med)

    # Castle HP
    draw.rounded_rectangle([362, 18, 445, 58], radius=6, fill=(21, 36, 61, 255))
    draw.text((370, 28), f"🏰 {castle_hp}", fill=(75, 196, 255), font=font_med)

    # Fort HP
    draw.rounded_rectangle([452, 18, 528, 58], radius=6, fill=(59, 22, 22, 255))
    draw.text((460, 28), f"⚔️ {fort_hp}", fill=(255, 94, 87), font=font_med)

def draw_bottom_dock(draw, img, active_tab="TODOS"):
    dock_top = H - 150
    draw.rectangle([0, dock_top, W, H], fill=(16, 22, 36, 255))
    draw.rectangle([0, dock_top, W, dock_top + 2], fill=(255, 205, 117, 180))

    # Tabs
    tab_w = (W - 24) // 3
    tabs = ["TODOS", "TROPAS", "ECONOMÍA"]
    for i, t in enumerate(tabs):
        tx = 12 + i * tab_w
        is_active = (t == active_tab)
        bg_col = (59, 111, 216, 255) if is_active else (25, 34, 51, 200)
        draw.rounded_rectangle([tx, dock_top + 8, tx + tab_w - 4, dock_top + 34], radius=4, fill=bg_col)
        draw.text((tx + tab_w//2 - 20, dock_top + 14), t, fill=(255, 255, 255), font=font_small)

    # Action cards in dock
    cards = [
        {"name": "Peasant", "cost": "50g", "id": "peasant"},
        {"name": "Knight", "cost": "100g 20w", "id": "knight"},
        {"name": "Spearman", "cost": "75g 25w", "id": "spearman"},
        {"name": "Archer", "cost": "60g 40w", "id": "archer"},
        {"name": "Wizard", "cost": "120g 60w", "id": "wizard"}
    ]
    card_w = (W - 20) // 5
    for i, c in enumerate(cards):
        cx = 10 + i * card_w
        cy = dock_top + 42
        draw.rounded_rectangle([cx, cy, cx + card_w - 4, cy + 96], radius=4, fill=(25, 34, 51, 255), outline=(50, 65, 90))
        spr = get_unit_sprite(c["id"])
        if spr:
            s_img = spr.resize((40, 40), Image.NEAREST)
            img.paste(s_img, (cx + (card_w - 4)//2 - 20, cy + 8), s_img)
        draw.text((cx + 4, cy + 54), c["name"][:7], fill=(255, 255, 255), font=font_small)
        draw.text((cx + 4, cy + 72), c["cost"], fill=(255, 205, 117), font=font_small)

def render_level_image(lvl, filename):
    img = Image.new("RGBA", (W, H), (16, 20, 29, 255))
    draw = ImageDraw.Draw(img)

    biome_name = get_level_biome(lvl["id"])
    b_cfg = BIOME_CONFIGS[biome_name]

    # Map grid area
    grid_top = 86
    grid_bottom = H - 156
    grid_h = grid_bottom - grid_top
    grid_w = W - 20
    grid_left = 10

    # Map raw lines
    raw_map = lvl["map"]
    rows = len(raw_map)
    cols = len(raw_map[0])

    cell_w = grid_w / cols
    cell_h = grid_h / rows

    # Draw map background
    draw.rectangle([grid_left, grid_top, grid_left + grid_w, grid_bottom], fill=b_cfg["bg"])

    # Draw cells
    for r in range(rows):
        line = raw_map[r]
        for c in range(cols):
            ch = line[c]
            x0 = int(grid_left + c * cell_w)
            y0 = int(grid_top + r * cell_h)
            x1 = int(x0 + cell_w)
            y1 = int(y0 + cell_h)

            # Base tile
            draw.rectangle([x0, y0, x1, y1], fill=b_cfg["grass"], outline=b_cfg["grass_grid"])

            if ch == 'T': # Tree
                draw.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], fill=b_cfg["tree"])
                # small tree icon
                tree_spr = get_sprite("Tiles", "tree")
                if tree_spr:
                    t_re = tree_spr.resize((int(cell_w), int(cell_h)), Image.NEAREST)
                    img.paste(t_re, (x0, y0), t_re)
            elif ch == 'G': # Goldmine
                draw.rectangle([x0 + 1, y0 + 1, x1 - 1, y1 - 1], fill=b_cfg["goldmine"])
                gm_spr = get_icon("icon_goldmine")
                if gm_spr:
                    img.paste(gm_spr.resize((int(cell_w), int(cell_h)), Image.NEAREST), (x0, y0), gm_spr.resize((int(cell_w), int(cell_h)), Image.NEAREST))
            elif ch in ['#', 'B']: # Rock / Barricade
                col = b_cfg["barricade"] if ch == 'B' else b_cfg["rock"]
                draw.rectangle([x0 + 1, y0 + 1, x1 - 1, y1 - 1], fill=col)
                if ch == 'B':
                    barr_spr = get_unit_sprite("barricade")
                    if barr_spr:
                        b_re = barr_spr.resize((int(cell_w), int(cell_h)), Image.NEAREST)
                        img.paste(b_re, (x0, y0), b_re)
            elif ch == '~': # Water
                draw.rectangle([x0, y0, x1, y1], fill=b_cfg["water"])
            elif ch == 'M': # Monster
                draw.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], fill=(180, 50, 50))
                draw.text((x0 + 2, y0 + 2), "M", fill=(255, 255, 255), font=font_small)
            elif ch == 'C': # Chest
                draw.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], fill=(230, 180, 40))
                draw.text((x0 + 2, y0 + 2), "C", fill=(0, 0, 0), font=font_small)
            elif ch == 'K': # Kingdom Castle
                cast_spr = get_unit_sprite("castle")
                if cast_spr:
                    c_re = cast_spr.resize((int(cell_w * 2.2), int(cell_h * 2.2)), Image.NEAREST)
                    img.paste(c_re, (int(x0 - cell_w * 0.6), int(y0 - cell_h * 0.6)), c_re)
                else:
                    draw.rectangle([x0 - 5, y0 - 5, x1 + 5, y1 + 5], fill=(59, 111, 216))
            elif ch == 'H': # Horde Fortress
                fort_spr = get_unit_sprite("fortress")
                if fort_spr:
                    f_re = fort_spr.resize((int(cell_w * 2.2), int(cell_h * 2.2)), Image.NEAREST)
                    img.paste(f_re, (int(x0 - cell_w * 0.6), int(y0 - cell_h * 0.6)), f_re)
                else:
                    draw.rectangle([x0 - 5, y0 - 5, x1 + 5, y1 + 5], fill=(192, 57, 43))

    # Place representative active combat units in lane
    # Kingdom units pushing up from row ~24 to row ~12
    # Horde units pushing down from row ~8 to row ~16
    units_to_draw = []
    lvl_num = int(lvl["id"].replace("level", ""))

    # Peasants near kingdom base / mine
    units_to_draw.append(("peasant", 4, rows - 5, 40, 40, False))
    units_to_draw.append(("peasant", 5, rows - 4, 40, 40, False))

    # Kingdom vanguard
    units_to_draw.append(("knight", cols // 2 - 1, rows // 2 + 2, 220, 220, False))
    units_to_draw.append(("spearman", cols // 2 + 1, rows // 2 + 2, 130, 130, False))
    units_to_draw.append(("archer", cols // 2, rows // 2 + 4, 70, 70, False))

    if lvl_num >= 4:
        units_to_draw.append(("wizard", cols // 2 - 2, rows // 2 + 5, 60, 60, False))
    if lvl_num >= 6:
        units_to_draw.append(("paladin", cols // 2 + 2, rows // 2 + 1, 320, 320, False))
    if lvl_num >= 8:
        units_to_draw.append(("catapult", cols // 2, rows // 2 + 6, 150, 150, False))

    # Horde vanguard meeting them
    if lvl_num == 1:
        units_to_draw.append(("goblin", cols // 2 - 1, rows // 2 - 1, 60, 60, True))
        units_to_draw.append(("goblin_archer", cols // 2 + 1, rows // 2 - 3, 55, 55, True))
        units_to_draw.append(("orc", cols // 2, rows // 2 - 1, 180, 180, True))
    elif lvl_num in [2, 3, 4]:
        units_to_draw.append(("orc", cols // 2 - 1, rows // 2 - 1, 180, 180, True))
        units_to_draw.append(("orc", cols // 2 + 1, rows // 2 - 1, 180, 180, True))
        units_to_draw.append(("goblin_archer", cols // 2, rows // 2 - 3, 55, 55, True))
        units_to_draw.append(("orc_chieftain", cols // 2, rows // 2 - 2, 300, 300, True))
    elif lvl_num in [5, 6, 7]:
        units_to_draw.append(("warlord_gorgar", cols // 2, rows // 2 - 1, 850, 850, True))
        units_to_draw.append(("orc_chieftain", cols // 2 - 2, rows // 2 - 1, 300, 300, True))
        units_to_draw.append(("orc", cols // 2 + 2, rows // 2 - 1, 180, 180, True))
        units_to_draw.append(("goblin_archer", cols // 2 + 1, rows // 2 - 4, 55, 55, True))
    else: # 8, 9, 10
        if lvl_num == 10:
            units_to_draw.append(("shaman_zuldar", cols // 2, rows // 2 - 3, 750, 750, True))
        units_to_draw.append(("warlord_gorgar", cols // 2 - 1, rows // 2 - 1, 850, 850, True))
        units_to_draw.append(("orc_chieftain", cols // 2 + 1, rows // 2 - 1, 300, 300, True))
        units_to_draw.append(("orc", cols // 2 - 2, rows // 2 - 2, 180, 180, True))
        units_to_draw.append(("orc", cols // 2 + 2, rows // 2 - 2, 180, 180, True))

    for u_id, c_idx, r_idx, hp, max_hp, is_horde in units_to_draw:
        u_spr = get_unit_sprite(u_id)
        ux = int(grid_left + c_idx * cell_w)
        uy = int(grid_top + r_idx * cell_h)
        uw = int(cell_w * 1.5)
        uh = int(cell_h * 1.5)
        if u_spr:
            if is_horde:
                u_spr = u_spr.transpose(Image.FLIP_LEFT_RIGHT)
            u_resized = u_spr.resize((uw, uh), Image.NEAREST)
            img.paste(u_resized, (ux - 4, uy - 4), u_resized)

        # Health bar
        bar_w = 26
        bar_h = 4
        bar_x = ux + (cell_w - bar_w) // 2
        bar_y = uy - 6
        draw.rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h], fill=(20, 20, 20, 200))
        pct = hp / max_hp
        bar_color = (46, 204, 113) if not is_horde else (231, 76, 60)
        draw.rectangle([bar_x, bar_y, bar_x + int(bar_w * pct), bar_y + bar_h], fill=bar_color)

    # Level info floating badge at top of map
    badge_w = 340
    badge_x = (W - badge_w) // 2
    draw.rounded_rectangle([badge_x, grid_top + 8, badge_x + badge_w, grid_top + 40], radius=8, fill=(16, 24, 38, 230), outline=(255, 205, 117))
    draw.text((badge_x + 12, grid_top + 16), f"Misión: {lvl['displayName']}", fill=(255, 205, 117), font=font_med)

    draw_top_bar(draw, img, gold=lvl["startGold"] + 80, wood=lvl["startWood"] + 40, time_str="01:15", castle_hp=1420, fort_hp=950)
    draw_bottom_dock(draw, img, active_tab="TODOS")

    out_path = os.path.join(OUT_DIR, filename)
    img.save(out_path)
    print(f"Generated level capture: {out_path}")

def render_result_screen(is_victory, filename):
    img = Image.new("RGBA", (W, H), (16, 20, 29, 255))
    draw = ImageDraw.Draw(img)

    # Dim background simulating battle paused
    draw_top_bar(draw, img, gold=320, wood=180, time_str="02:30", castle_hp=1180, fort_hp=0 if is_victory else 850)
    draw_bottom_dock(draw, img)

    # Dark overlay
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 180))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    # Modal Box (440x360)
    mw, mh = 440, 360
    mx = (W - mw) // 2
    my = (H - mh) // 2 - 20
    draw.rounded_rectangle([mx, my, mx + mw, my + mh], radius=12, fill=(27, 32, 48, 252), outline=(255, 205, 117) if is_victory else (231, 76, 60), width=3)

    # Gold top line
    accent_col = (46, 204, 113) if is_victory else (231, 76, 60)
    draw.rectangle([mx, my, mx + mw, my + 6], fill=accent_col)

    title_text = "¡VICTORIA!" if is_victory else "DERROTA"
    draw.text((mx + 130, my + 30), title_text, fill=accent_col, font=font_large)

    if is_victory:
        sub1 = "¡Has destruido la fortaleza enemiga!"
        sub2 = "Recompensas de Batalla:"
        rew1 = "⭐ +100 XP de Comandante"
        rew2 = "🎖️ +3 Puntos de Talento"
        rew3 = "🪙 +50 Monedas de Guerra (Bounty)"
        draw.text((mx + 70, my + 85), sub1, fill=(240, 240, 240), font=font_med)
        draw.text((mx + 110, my + 120), sub2, fill=(255, 205, 117), font=font_med)
        draw.text((mx + 90, my + 155), rew1, fill=(46, 204, 113), font=font_med)
        draw.text((mx + 90, my + 185), rew2, fill=(52, 152, 219), font=font_med)
        draw.text((mx + 90, my + 215), rew3, fill=(241, 196, 15), font=font_med)
    else:
        sub1 = "El Castillo de Aldoria ha caído..."
        sub2 = "Recompensa de Consuelo (Cada acción cuenta):"
        rew1 = "⭐ +30 XP de Comandante"
        rew2 = "🎖️ +1 Punto de Talento"
        rew3 = "🪙 +15 Monedas de Guerra (Por bajas enemigas)"
        draw.text((mx + 85, my + 85), sub1, fill=(200, 200, 200), font=font_med)
        draw.text((mx + 35, my + 120), sub2, fill=(255, 205, 117), font=font_med)
        draw.text((mx + 90, my + 155), rew1, fill=(189, 195, 199), font=font_med)
        draw.text((mx + 90, my + 185), rew2, fill=(189, 195, 199), font=font_med)
        draw.text((mx + 90, my + 215), rew3, fill=(241, 196, 15), font=font_med)

    # Return button
    btn_w, btn_h = 280, 56
    bx = (W - btn_w) // 2
    by = my + mh - 76
    btn_bg = (52, 73, 94) if is_victory else (142, 68, 173)
    draw.rounded_rectangle([bx, by, bx + btn_w, by + btn_h], radius=8, fill=btn_bg, outline=(255, 255, 255))
    map_icon = get_icon("icon_map")
    if map_icon:
        m_re = map_icon.resize((28, 28), Image.NEAREST)
        img.paste(m_re, (bx + 20, by + 14), m_re)
    draw.text((bx + 65, by + 20), "VOLVER AL MAPA", fill=(255, 255, 255), font=font_med)

    out_path = os.path.join(OUT_DIR, filename)
    img.save(out_path)
    print(f"Generated result screen: {out_path}")

# Run generation for all levels
for lvl in levels_data:
    filename = f"{lvl['id']}_{get_level_biome(lvl['id'])}.png"
    render_level_image(lvl, filename)

render_result_screen(True, "screen_victory.png")
render_result_screen(False, "screen_defeat.png")

print("All screenshots successfully generated!")
