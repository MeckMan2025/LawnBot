"""Write docs/print-guide.md from cad/out/manifest.csv."""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "out", "manifest.csv")
OUT = os.path.join(os.path.dirname(HERE), "docs", "print-guide.md")
DENSITY = {"PETG": 1.27, "TPU 95A": 1.21, "clear PETG": 1.27, "PETG + TPU": 1.27, "PETG + TPU gasket": 1.27, "PETG + TPU skin": 1.27, "PETG + clear window": 1.27, "PETG, 6 pieces": 1.27}

HEAD = """# Print guide

Generated from `cad/out/manifest.csv` by `cad/print_guide.py`. Re-run it after any CAD change.

## Printer settings (Bambu Lab H2C)
- **PETG parts:** 0.4 mm hardened nozzle, 0.2 mm layers, 255 C nozzle, 70 C bed, textured PEI. Walls and infill per the table (gyroid). Dry the spool first.
- **TPU 95A parts:** 0.4 mm nozzle, 0.2 mm layers, 230 C, 40 C bed, 30 mm/s, retraction short, no AMS (direct feed). Dry 8 hours at 65 C first.
- **Clear PETG window:** 0.4 mm nozzle, 100 percent infill, print slowly for clarity.
- **Supports:** only the parts marked `yes`. Use tree supports, 0.2 mm Z gap, and pull them before fitting bearings.
- **Heat-set inserts:** M2.5 (3.4 mm hole), M3 (4.0), M4 (5.6), M5 (6.4), M6 (8.0). Set them with a soldering iron at 230 C, keep them square.
- **Bearing seats:** modelled with 0.25 mm of interference. Test the first seat on a coupon; ream lightly if it needs more than thumb pressure plus a tap.

## Print order
1. **Coupons first:** print one `caster_axle_spacer_outer` and one `bearing_spacer` to check your TPU and PETG dimensions, then a 20 mm slice of `drive_axle_housing` to check the 6808 fit.
2. **Drive first:** `drive_wheel`, `drive_tread`, `drive_axle_housing`, `motor_mount_bracket`, `bearing_spacer`. You can test the motors with these alone.
3. **Chassis:** modules, lids, dowels, battery tray.
4. **Boom and casters:** arms, cross halves, risers, braces, legs, towers, forks, sleeves, rims, tires, spacers, deck quadrants.
5. **Enclosure and shell:** tub, lid, gasket, skirts, canopy quadrants, splices, fenders, bumper, camera mount and hood.
6. **Mast, rear fittings, dock.**

Mass is estimated from the solid volume, the wall count and the infill, so treat it as plus or minus 20 percent.

## Parts
"""


def est_mass(vol_cm3, material, walls, infill):
    rho = DENSITY.get(material, 1.27)
    # shell fraction grows with wall count; the rest follows infill
    shell = min(0.25 + 0.08 * int(walls), 0.75)
    return vol_cm3 * rho * (shell + (1 - shell) * int(infill) / 100.0)


def main():
    rows = list(csv.DictReader(open(MANIFEST)))
    lines = [HEAD, "| Part | Qty | Material | Size (mm) | Walls | Infill | Supports | Orientation | Est. mass each | Notes |", "|---|---|---|---|---|---|---|---|---|---|"]
    total = 0.0
    by_mat = {}
    for r in rows:
        m = est_mass(float(r["volume_cm3"]), r["material"], r["walls"], r["infill_pct"])
        total += m * int(r["qty"])
        by_mat[r["material"]] = by_mat.get(r["material"], 0.0) + m * int(r["qty"])
        lines.append(f"| `{r['part']}` | {r['qty']} | {r['material']} | {r['x_mm']} x {r['y_mm']} x {r['z_mm']} | {r['walls']} | {r['infill_pct']}% | {r['supports']} | {r['orientation']} | {m:.0f} g | {r['notes']} |")
    lines.append("")
    lines.append("## Filament estimate")
    for mat, g in sorted(by_mat.items(), key=lambda kv: -kv[1]):
        lines.append(f"- {mat}: about {g / 1000:.1f} kg")
    lines.append(f"- **Total: about {total / 1000:.1f} kg**")
    with open(OUT, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"wrote {OUT}: {len(rows)} parts, about {total / 1000:.1f} kg of filament")


if __name__ == "__main__":
    main()
