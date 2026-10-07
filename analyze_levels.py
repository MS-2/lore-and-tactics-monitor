import json
import os

PROJECT_DIR = r"D:\Unity\Lore & Tactics"

with open(os.path.join(PROJECT_DIR, "Assets", "Resources", "Data", "levels.json"), "r", encoding="utf-8-sig") as f:
    levels = json.load(f)["levels"]

with open(os.path.join(PROJECT_DIR, "Assets", "Resources", "Data", "units.json"), "r", encoding="utf-8-sig") as f:
    units = {u["id"]: u for u in json.load(f)["units"]}

results = []

for lvl in levels:
    lid = lvl["id"]
    name = lvl["displayName"]
    sg = lvl["startGold"]
    sw = lvl["startWood"]
    pg = lvl["passiveGoldPerSecond"]
    waves = lvl["waves"]

    total_enemy_hp = 0
    total_enemy_count = 0
    wave_summary = []

    for idx, w in enumerate(waves):
        w_time = w["time"]
        w_units = w["units"]
        w_hp = sum(units[uid]["maxHp"] for uid in w_units)
        w_dps = sum(units[uid]["damage"] / max(0.1, units[uid]["attackCooldown"]) for uid in w_units)
        total_enemy_hp += w_hp
        total_enemy_count += len(w_units)
        unit_str = ", ".join(w_units)
        wave_summary.append(f"W{idx+1} (t={w_time}s): [{unit_str}] (HP={w_hp}, DPS={w_dps:.1f})")

    # Player income by wave 1
    w1_time = waves[0]["time"]
    gold_at_w1 = sg + w1_time * pg + (15 * 2 * (w1_time // 8)) # assuming 2 peasants mining gold
    wood_at_w1 = sw + (15 * 1 * (w1_time // 8))

    results.append({
        "id": lid,
        "name": name,
        "waves_count": len(waves),
        "total_enemy_hp": total_enemy_hp,
        "total_enemy_count": total_enemy_count,
        "gold_at_w1": gold_at_w1,
        "wood_at_w1": wood_at_w1,
        "wave_summary": wave_summary
    })

print(json.dumps(results, indent=2, ensure_ascii=False))
