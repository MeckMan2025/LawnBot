"""Build every part, export STEP and STL, check the print volume, write a manifest.

Usage:  .venv/bin/python cad/export.py [module ...]
"""
import csv
import importlib
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cadquery as cq  # noqa: E402

import params as P  # noqa: E402
from lib.features import bbox, fits_build  # noqa: E402
from parts import MODULES  # noqa: E402

OUT = os.path.join(HERE, "out")
STEP_DIR = os.path.join(OUT, "step")
STL_DIR = os.path.join(OUT, "stl")
WEB_DIR = os.path.join(os.path.dirname(HERE), "docs", "guide", "models")   # coarse STLs for the assembly guide


def main(selected):
    os.makedirs(STEP_DIR, exist_ok=True)
    os.makedirs(STL_DIR, exist_ok=True)
    os.makedirs(WEB_DIR, exist_ok=True)
    rows, failures = [], []
    for modname in selected:
        mod = importlib.import_module(f"parts.{modname}")
        for part in mod.parts():
            t0 = time.time()
            try:
                solid = part.build()
                if len(solid.solids().vals()) != 1:
                    raise RuntimeError(f"{len(solid.solids().vals())} solids; expected 1")
                dims = bbox(solid)
                fits = fits_build(solid, dual="tpu" in part.tags and "dual" in part.tags)
                vol_cm3 = solid.val().Volume() / 1000.0
                cq.exporters.export(solid, os.path.join(STEP_DIR, f"{part.name}.step"))
                # coarse web mesh first: OCC keeps the finest triangulation it has made, so the fine export must come second
                cq.exporters.export(solid, os.path.join(WEB_DIR, f"{part.name}.stl"), tolerance=0.6, angularTolerance=0.5)
                cq.exporters.export(solid, os.path.join(STL_DIR, f"{part.name}.stl"), tolerance=0.05, angularTolerance=0.1)
                rows.append({
                    "module": modname, "part": part.name, "qty": part.qty, "material": part.material,
                    "x_mm": round(dims[0], 1), "y_mm": round(dims[1], 1), "z_mm": round(dims[2], 1),
                    "volume_cm3": round(vol_cm3, 1), "fits_h2c": "yes" if fits else "NO",
                    "walls": part.walls, "infill_pct": part.infill, "supports": "yes" if part.supports else "no",
                    "orientation": part.orientation, "notes": part.notes,
                })
                flag = "" if fits else "   <-- TOO BIG"
                print(f"ok   {modname}/{part.name:34s} {dims[0]:6.1f} x {dims[1]:6.1f} x {dims[2]:6.1f}  {vol_cm3:7.1f} cm3  {time.time() - t0:4.1f}s{flag}")
                if not fits:
                    failures.append(f"{part.name} exceeds the print volume: {dims}")
            except Exception as exc:  # keep going so one bad part doesn't hide the rest
                failures.append(f"{modname}/{part.name}: {exc}")
                print(f"FAIL {modname}/{part.name}: {exc}")
    with open(os.path.join(OUT, "manifest.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ["part"])
        w.writeheader()
        w.writerows(rows)
    import json
    with open(os.path.join(WEB_DIR, "manifest.json"), "w") as fh:
        json.dump(rows, fh, indent=1)
    print(f"\n{len(rows)} parts exported to {OUT}")
    if failures:
        print("\nProblems:")
        for f in failures:
            print("  - " + f)
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:] or MODULES)
