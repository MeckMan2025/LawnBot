"""Place the structural parts in the robot frame, export an assembly STEP, report interferences.

Also writes out/assembly.json: every instance with its part name, assembly step, and the ordered
transform ops that take the part from its print frame to the robot frame. The illustrated assembly
guide (docs/guide) reads that file.

Usage:  .venv/bin/python cad/assembly.py [--no-check]
"""
import itertools
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cadquery as cq  # noqa: E402

import params as P  # noqa: E402
from parts import chassis, drivetrain, casters, boom, enclosure, shell, mast, rear  # noqa: E402

OUT = os.path.join(HERE, "out")

# Pairs that are meant to overlap (press fits) and are skipped by the interference check.
PRESS_FIT = {("drive_wheel", "drive_tread"), ("caster_rim", "caster_tire")}


def apply(solid, ops):
    """ops: list of ("rx"|"ry"|"rz", deg) or ("t", (x, y, z)), applied in order about the world origin."""
    for op in ops:
        kind, val = op
        if kind == "t":
            solid = solid.translate(val)
        else:
            axis = {"rx": (1, 0, 0), "ry": (0, 1, 0), "rz": (0, 0, 1)}[kind]
            solid = solid.rotate((0, 0, 0), axis, val)
    return solid


def placements():
    """Yield (instance name, part name, step, ops)."""
    L, W = P.MOD_L, P.MOD_W
    for sx, sy, nm in ((-1, 1, "rear_left"), (-1, -1, "rear_right"), (1, 1, "front_left"), (1, -1, "front_right")):
        cx, cy = chassis.module_center(sx, sy)
        yield nm, f"chassis_module_{nm}", 1, [("t", (cx, cy, P.CH_BOTTOM))]
    # motor mounts (with the motors bolted on) and axle housings go in before the lids: the housing nuts are inside
    for sy, nm in ((1, "left"), (-1, "right")):
        yield f"motor_mount_{nm}", "motor_mount_bracket", 2, [("rx", 90 * sy), ("t", (P.AXLE_X, sy * (P.CH_W / 2 - P.CH_WALL), P.AXLE_Z))]
        yield f"axle_housing_{nm}", "drive_axle_housing", 2, [("rx", -90 * sy), ("t", (P.AXLE_X, sy * P.CH_W / 2, P.AXLE_Z))]
    yield "lid_rear", "chassis_lid_rear", 2, [("t", (P.CH_CX - L / 2, 0, P.CH_TOP))]
    yield "lid_front", "chassis_lid_front", 2, [("t", (P.CH_CX + L / 2, 0, P.CH_TOP))]
    for sy, nm in ((1, "left"), (-1, "right")):
        yield f"wheel_{nm}", "drive_wheel", 2, [("rx", -90 * sy), ("t", (P.AXLE_X, sy * P.WHEEL_INNER_Y, P.AXLE_Z))]
        yield f"tread_{nm}", "drive_tread", 2, [("rx", -90 * sy), ("t", (P.AXLE_X, sy * P.WHEEL_INNER_Y, P.AXLE_Z))]

    for sy, nm in ((1, "left"), (-1, "right")):
        yield f"leg_{nm}", "rear_deck_leg", 3, [("t", (P.LEG_X, sy * P.LEG_Y, P.CH_LID_TOP))]
    # battery and skirts go on before the boom frame and the deck: the side skirts cannot pass the cross members
    # or the wheels later, and their flange bolts are reached from above
    yield "battery_tray", "battery_tray", 3, [("t", (P.BATTERY_X, 0, P.CH_LID_TOP))]
    yield "skirt_rear", "skirt_rear", 3, [("rz", -90), ("t", (P.CH_REAR + P.SKIRT_T / 2, 0, P.SKIRT_Z0))]
    yield "skirt_front", "skirt_front", 3, [("rz", 90), ("t", (P.CH_FRONT - P.SKIRT_T / 2, 0, P.SKIRT_Z0))]
    for sy, nm in ((1, "left"), (-1, "right")):
        for key in ("rear", "front"):
            part = f"skirt_side_{key}"
            cx = shell.SIDE_PANELS[key][0]
            yield f"{part}_{nm}", part, 3, [("rz", 180 if sy > 0 else 0), ("t", (cx, sy * (P.CH_W / 2 - P.SKIRT_T / 2), P.SKIRT_Z0))]

    # risers are bolted to the rear cross member first (subassembly), then the pair stands on the lid
    for sy, nm in ((1, "left"), (-1, "right")):
        yield f"riser_{nm}", "riser_column", 4, [("t", (P.RISER_X, sy * P.RISER_Y, P.CH_LID_TOP))]
        yield f"cross_rear_{nm}", "boom_cross_rear_half", 4, [("rz", 90 * sy), ("t", (P.CROSS_REAR_X, 0, P.BOOM_Z))]
    for sy, nm in ((1, "left"), (-1, "right")):
        yield f"brace_{nm}", "riser_brace", 4, [("t", (0, sy * P.RISER_Y, P.CH_LID_TOP))]
        yield f"boom_arm_{nm}", f"boom_arm_{nm}", 4, [("t", (P.BOOM_ARM_X0, sy * 200.0, P.BOOM_Z))]
    for sy, nm in ((1, "left"), (-1, "right")):
        yield f"cross_front_{nm}", "boom_cross_front_half", 4, [("rz", 90 * sy), ("t", (P.CROSS_FRONT_X, 0, P.BOOM_Z))]
    for sy, nm in ((1, "left"), (-1, "right")):
        yield f"tower_{nm}", "caster_spindle_tower", 5, [("t", (P.CASTER_X, sy * P.CASTER_Y, P.TOWER_Z0))]
        yield f"sleeve_{nm}", "caster_spindle_sleeve", 5, [("t", (P.CASTER_X, sy * P.CASTER_Y, P.CROWN_TOP))]
        yield f"fork_{nm}", "caster_fork", 5, [("t", (P.CASTER_X, sy * P.CASTER_Y, P.CASTER_TIRE_D / 2))]
        yield f"caster_rim_{nm}", "caster_rim", 5, [("rx", -90), ("t", (P.CASTER_X - P.CASTER_TRAIL, sy * P.CASTER_Y - P.CASTER_W / 2, P.CASTER_TIRE_D / 2))]
        yield f"caster_tire_{nm}", "caster_tire", 5, [("rx", -90), ("t", (P.CASTER_X - P.CASTER_TRAIL, sy * P.CASTER_Y - P.CASTER_W / 2, P.CASTER_TIRE_D / 2))]

    seam_x = (P.DECK_X0 + P.DECK_X1) / 2
    ql, qw = (P.DECK_X1 - P.DECK_X0) / 2, P.DECK_W / 2
    # quadrants with pockets go in before the ones whose tabs lap over them
    for sx, sy, nm in ((-1, -1, "rear_right"), (-1, 1, "rear_left"), (1, -1, "front_right"), (1, 1, "front_left")):
        yield f"deck_{nm}", f"deck_{nm}", 6, [("t", (seam_x + sx * ql / 2, sy * qw / 2, P.DECK_Z0))]
    yield "enclosure_tub", "enclosure_tub", 6, [("t", (P.ENC_X, 0, P.DECK_TOP))]
    yield "enclosure_lid", "enclosure_lid", 6, [("t", (P.ENC_X, 0, P.DECK_TOP + P.ENC_H))]
    yield "mast_standoff", "mast_standoff", 6, [("t", (P.MAST_X, 0, P.DECK_TOP))]
    cseam = shell.CAN_CX
    cql, cqw = shell.CAN_L / 2, P.CANOPY_W / 2
    for sx, sy, nm in ((1, 1, "front_left"), (1, -1, "front_right"), (-1, 1, "rear_left"), (-1, -1, "rear_right")):
        yield f"canopy_{nm}", f"canopy_{nm}", 7, [("t", (cseam + sx * cql / 2, sy * cqw / 2, P.CANOPY_Z0))]
    for sy, nm in ((1, "left"), (-1, "right")):
        yield f"fender_{nm}", "fender", 7, [("rz", 0 if sy > 0 else 180), ("t", (P.AXLE_X, sy * P.CANOPY_W / 2, P.AXLE_Z))]
    # carrier ears (20 deep) sit against the canopy nose; the bar is 24 deep; the skin's channel takes the bar's front 8 mm
    yield "bumper_carrier", "bumper_carrier", 7, [("rz", -90), ("t", (P.CANOPY_X1 + 20.0 + 12.0, 0, P.BUMPER_Z - 30.0))]
    yield "bumper_skin", "bumper_skin", 7, [("rz", -90), ("t", (P.CANOPY_X1 + 20.0 + 24.0 - 1.0, 0, P.BUMPER_Z - 34.0))]
    yield "oak_mount", "oak_mount", 7, [("rz", -90), ("t", (P.CANOPY_X1 + 6.0, 0, P.CANOPY_Z1 - 70.0))]
    yield "estop_housing", "estop_housing", 7, [("t", (P.CANOPY_X0 + 45.0, P.ESTOP_Y, P.CANOPY_Z1))]
    yield "light_bar_housing", "light_bar_housing", 7, [("rz", 90), ("t", (P.CANOPY_X0 - 8.0, 0, P.CANOPY_Z1 - 37.0))]

    yield "mast_base", "mast_base", 8, [("t", (P.MAST_X, 0, P.CANOPY_Z1))]
    for i in range(P.MAST_SEGMENTS):
        yield f"mast_segment_{i}", "mast_segment", 8, [("t", (P.MAST_X, 0, P.CANOPY_Z1 + 8.0 + i * P.MAST_SEG_L))]
    top = P.CANOPY_Z1 + 8.0 + P.MAST_SEGMENTS * P.MAST_SEG_L
    yield "pan_base", "pan_base", 8, [("t", (P.MAST_X, 0, top))]
    yield "tilt_bracket", "tilt_bracket", 8, [("t", (P.MAST_X, 0, top + 74.0))]
    yield "camera_housing", "camera_housing", 8, [("t", (P.MAST_X, 0, top + 74.0 + 16.0))]
    yield "gps_mount", "gps_mount", 8, [("t", (P.MAST_X - 28.0, 0, top + 10.0))]


MODULES = [chassis, drivetrain, casters, boom, enclosure, shell, mast, rear]


def build_all():
    built = {}
    for mod in MODULES:
        for p in mod.parts():
            built[p.name] = p
    cache = {}

    def get(name):
        if name not in cache:
            cache[name] = built[name].build()
        return cache[name]
    return get


def main(check=True):
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    get = build_all()
    items = [(inst, part, step, ops, apply(get(part), ops)) for inst, part, step, ops in placements()]
    print(f"placed {len(items)} instances in {time.time() - t0:.1f}s")
    with open(os.path.join(OUT, "assembly.json"), "w") as fh:
        json.dump([{"instance": i, "part": p, "step": s, "ops": o} for i, p, s, o, _ in items], fh, indent=1)
    asm = cq.Assembly(name="LawnBot")
    for inst, part, step, ops, solid in items:
        asm.add(solid, name=inst)
    asm.export(os.path.join(OUT, "assembly.step"))
    comp = cq.Compound.makeCompound([s.val() for *_, s in items])
    cq.exporters.export(cq.Workplane().add(comp), os.path.join(OUT, "assembly.stl"), tolerance=0.1, angularTolerance=0.2)
    bb = comp.BoundingBox()
    print(f"assembly envelope: {bb.xlen:.0f} x {bb.ylen:.0f} x {bb.zlen:.0f} mm  (x {bb.xmin:.0f}..{bb.xmax:.0f}, y {bb.ymin:.0f}..{bb.ymax:.0f}, z {bb.zmin:.0f}..{bb.zmax:.0f})")
    if not check:
        return
    print("checking interferences...")
    problems = []
    placed_lookup = {inst: s for inst, *_, s in items}
    boxes = {inst: s.val().BoundingBox() for inst, *_, s in items}
    for (ia, pa, _, _, sa), (ib, pb, _, _, sb) in itertools.combinations(items, 2):
        if (pa, pb) in PRESS_FIT or (pb, pa) in PRESS_FIT:
            continue
        a, b = boxes[ia], boxes[ib]
        if a.xmax < b.xmin or b.xmax < a.xmin or a.ymax < b.ymin or b.ymax < a.ymin or a.zmax < b.zmin or b.zmax < a.zmin:
            continue
        try:
            vol = sa.intersect(sb).val().Volume()
        except Exception:
            vol = 0.0
        if vol > 50.0:   # mm^3; ignore tangent slivers
            problems.append((ia, ib, vol))
    if problems:
        print(f"{len(problems)} interferences:")
        for ia, ib, vol in sorted(problems, key=lambda p: -p[2]):
            bb = placed_lookup[ia].intersect(placed_lookup[ib]).val().BoundingBox()
            print(f"  {ia:24s} x {ib:24s} {vol / 1000:.2f} cm3  at x {bb.xmin:.0f}..{bb.xmax:.0f} y {bb.ymin:.0f}..{bb.ymax:.0f} z {bb.zmin:.0f}..{bb.zmax:.0f}")
        sys.exit(1)
    print("no interferences")


if __name__ == "__main__":
    main(check="--no-check" not in sys.argv)
