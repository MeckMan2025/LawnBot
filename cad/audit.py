"""Virtual build: assemble ClaudeBot in order and look for anything a human could not do.

Three checks:
1. Insertion sweeps. Every part is slid along its insertion path (120 mm) into its final position with
   all previously assembled parts present. Any collision on the way means the part cannot be fitted
   in that order.
2. Bolt alignment. For every fastener, a shank-sized probe runs the bolt's full length through the
   parts it joins. Any material inside the probe means a hole is missing or misaligned.
3. Driver access. An 8 mm driver probe extends 60 mm back from each bolt head. Anything in the way
   means you cannot reach the bolt at that point in the build.

Bought parts that matter for clearance (motors, battery) are included as envelopes.

Usage:  .venv/bin/python cad/audit.py        -> prints the report and writes docs/assembly-audit.md
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cadquery as cq  # noqa: E402

import params as P  # noqa: E402
import assembly as A  # noqa: E402
from parts import chassis, boom, shell  # noqa: E402

OUT_MD = os.path.join(os.path.dirname(HERE), "docs", "assembly-audit.md")
SWEEP_MM, SWEEP_STEPS = 120.0, 8
DRIVER_D, DRIVER_L, HEAD_H = 8.0, 60.0, 7.0
HOLE_TOL = 30.0     # mm3: a probe tip touching the bottom of a blind hole is not a problem
# parts that are stretched, pressed or snapped onto their partner; the sweep ignores that partner
FIT_PARTNERS = {"drive_tread": "drive_wheel", "caster_tire": "caster_rim", "camera_housing": "tilt_bracket"}


def cyl_along(p, d, diameter, length):
    """Cylinder from point p along unit direction d."""
    x, y, z = p
    dx, dy, dz = d
    plane = cq.Plane(origin=(x, y, z), normal=(dx, dy, dz))
    return cq.Workplane(plane).circle(diameter / 2).extrude(length)


def vol_in(probe, solids):
    total = 0.0
    pb = probe.val().BoundingBox()
    for s in solids:
        b = s.val().BoundingBox()
        if pb.xmax < b.xmin or b.xmax < pb.xmin or pb.ymax < b.ymin or b.ymax < pb.ymin or pb.zmax < b.zmin or b.zmax < pb.zmin:
            continue
        try:
            total += probe.intersect(s).val().Volume()
        except Exception:
            pass
    return total


# ---------------------------------------------------------------------------------------------
# Insertion directions (unit vectors pointing AWAY from the final position, i.e. where the part comes from)
def insertion_dir(inst):
    sy = 1 if inst.endswith("_left") else -1
    if inst.startswith(("axle_housing", "wheel_", "tread_")):
        return (0, sy, 0)
    if inst.startswith("motor_mount"):
        return (0, -sy, 0)
    if inst.startswith(("fork_", "sleeve_")):
        return (0, 0, -1)          # comes up from underneath the boom pad
    if inst.startswith(("caster_rim", "caster_tire")):
        return (1, 0, 0)           # rolls in between the yoke legs from the front
    if inst in ("skirt_rear", "light_bar_housing", "gps_mount"):
        return (-1, 0, 0)
    if inst in ("bumper_carrier", "bumper_skin", "oak_mount", "camera_housing"):
        return (1, 0, 0)
    if inst.startswith("cross_"):
        return (0, 0, 1)
    return (0, 0, 1)


# ---------------------------------------------------------------------------------------------
# Bought-part envelopes: (name, solid, present_after_instance)
def envelopes():
    out = []
    for sy, nm in ((1, "left"), (-1, "right")):
        face_y = sy * (P.CH_W / 2 - P.CH_WALL - 6.0 - P.MOTOR_MOUNT_STANDOFF)
        motor = cyl_along((P.AXLE_X, face_y, P.AXLE_Z), (0, -sy, 0), P.MOTOR_FACE_D, P.MOTOR_LENGTH)
        out.append((f"motor_{nm}", motor, f"motor_mount_{nm}"))
    bl, bw, bh = P.BATTERY
    batt = cq.Workplane("XY").box(bl, bw, bh, centered=(True, True, False)).translate((P.BATTERY_X, 0, P.CH_LID_TOP + 4.0))
    out.append(("battery", batt, "battery_tray"))
    return out


# ---------------------------------------------------------------------------------------------
# Fasteners: dicts with name, size, head (xyz), dir (unit, head -> tip), length, present ("after"
# instance name, or a list of instance names for an off-robot subassembly).
def joints():
    J = []
    L, W = P.MOD_L, P.MOD_W

    def add(name, size, head, d, length, present):
        J.append({"name": name, "size": size, "head": head, "dir": d, "length": length, "present": present})

    # 1. chassis seams
    for y in (30.0, 120.0, -30.0, -120.0):
        for z in (P.CH_BOTTOM + 25.0, P.CH_BOTTOM + 65.0):
            add("seam bolt (lateral)", "M5", (P.CH_CX - P.SEAM_WALL - 1.0, y, z), (1, 0, 0), 20.0, "front_right")
    for cx in (P.CH_CX - L / 2, P.CH_CX + L / 2):
        for lx in chassis.SEAM_BOLT_X:
            for z in (P.CH_BOTTOM + 25.0, P.CH_BOTTOM + 65.0):
                add("seam bolt (longitudinal)", "M5", (cx + lx, -P.SEAM_WALL - 1.0, z), (0, 1, 0), 20.0, "front_right")
    # 2. lids
    for sx, sy, nm in ((-1, 1, "rear_left"), (-1, -1, "rear_right"), (1, 1, "front_left"), (1, -1, "front_right")):
        cx, cy = chassis.module_center(sx, sy)
        for (bx, by) in chassis.boss_points(sx, sy):
            add("lid bolt", "M4", (cx + bx, cy + by, P.CH_LID_TOP), (0, 0, -1), 12.0, "lid_front")
    # 3. drive: axle housing bolts (heads in the flange counterbores, outside), motor bolts (off robot)
    px, pz = P.AXLE_FLANGE_PATTERN
    for sy, nm in ((1, "left"), (-1, "right")):
        for dx in (-px / 2, px / 2):
            for dz in (-pz / 2, pz / 2):
                add("axle housing bolt", "M5", (P.AXLE_X + dx, sy * (P.CH_W / 2 + P.AXLE_FLANGE_T - 6.0), P.AXLE_Z + dz), (0, -sy, 0), 35.0, f"axle_housing_{nm}")
        for (mx, mz) in ((-8, -8), (-8, 8), (8, -8), (8, 8)):
            add("motor bolt", "M4", (P.AXLE_X + mx, sy * (P.CH_W / 2 - P.CH_WALL - 5.0), P.AXLE_Z + mz), (0, -sy, 0), 16.0, [f"motor_mount_{nm}"])
    # 4. boom frame
    rpx, rpy = P.RISER_PATTERN
    lpx, lpy = P.LEG_PATTERN
    for sy, nm in ((1, "left"), (-1, "right")):
        for dx in (-rpx / 2, rpx / 2):
            for dy in (-rpy / 2, rpy / 2):
                add("riser foot bolt", "M5", (P.RISER_X + dx, sy * P.RISER_Y + dy, P.CH_LID_TOP + 6.0), (0, 0, -1), 16.0, f"riser_{nm}")
        for dx in (-P.RISER_TOP_DX, P.RISER_TOP_DX):
            add("riser top bolt", "M5", (P.RISER_X + dx, sy * P.RISER_Y, P.CH_LID_TOP + P.RISER_H - 6.0), (0, 0, 1), 15.0, [f"riser_{nm}", f"cross_rear_{nm}"])
        add("brace foot bolt", "M5", (P.BRACE_X - 10.0, sy * P.RISER_Y + 10.0, P.CH_LID_TOP + 6.0), (0, 0, -1), 16.0, f"brace_{nm}")
        add("brace foot bolt", "M5", (P.BRACE_X + 10.0, sy * P.RISER_Y - 10.0, P.CH_LID_TOP + 6.0), (0, 0, -1), 16.0, f"brace_{nm}")
        riser_face = P.RISER_X - P.RISER_SEC[0] / 2
        for (dy, z) in ((10.0, 34.0), (-10.0, 74.0)):
            add("brace to riser bolt", "M5", (riser_face - 6.0, sy * P.RISER_Y + dy, P.CH_LID_TOP + z), (1, 0, 0), 15.0, f"brace_{nm}")
        for dx in (-lpx / 2, lpx / 2):
            for dy in (-lpy / 2, lpy / 2):
                add("leg foot bolt", "M5", (P.LEG_X + dx, sy * P.LEG_Y + dy, P.CH_LID_TOP + 6.0), (0, 0, -1), 16.0, f"leg_{nm}")
        # arm to cross members: heads inside the arm/pad against the inner wall, driver through the 9 mm bores
        for gx in (P.CROSS_REAR_X - 10.0, P.CROSS_REAR_X + 10.0):
            add("arm to rear cross bolt", "M5", (gx, sy * (200.0 - P.BOOM_SEC / 2 + P.BOOM_WALL), P.BOOM_Z + P.BOOM_SEC / 2), (0, -sy, 0), 12.0, f"boom_arm_{nm}")
        for gx in (P.CROSS_FRONT_X - 10.0, P.CROSS_FRONT_X + 10.0):
            add("arm pad to front cross bolt", "M5", (gx, sy * (P.PAD_Y_IN + P.BOOM_WALL), P.BOOM_Z + P.BOOM_SEC / 2), (0, -sy, 0), 12.0, f"boom_arm_{nm}")
    # cross member splices: across the joint along y, through both tabs
    for gx_c, inst in ((P.CROSS_REAR_X, "cross_rear_right"), (P.CROSS_FRONT_X, "cross_front_right")):
        for dy in (-P.CROSS_TAB_L / 4, P.CROSS_TAB_L / 4):
            add("cross splice bolt", "M5", (gx_c - P.BOOM_SEC / 2 - 1.0, dy, P.BOOM_Z + P.BOOM_SEC / 2), (1, 0, 0), 45.0, inst)
    # 5. casters
    for sy, nm in ((1, "left"), (-1, "right")):
        for dx in (-P.TOWER_PATTERN / 2, P.TOWER_PATTERN / 2):
            for dy in (-P.TOWER_PATTERN / 2, P.TOWER_PATTERN / 2):
                add("tower bolt", "M6", (P.CASTER_X + dx, sy * P.CASTER_Y + dy, P.TOWER_Z0 + P.TOWER_FLANGE_T), (0, 0, -1), 20.0, f"tower_{nm}")
        crown_bottom = P.CROWN_TOP - P.CROWN_T
        add("spindle bolt (insert before the wheel)", "M12", (P.CASTER_X, sy * P.CASTER_Y, crown_bottom + 8.0), (0, 0, 1), 180.0, [f"fork_{nm}", f"sleeve_{nm}", f"tower_{nm}"])
        leg_out = P.CASTER_W / 2 + P.FORK_LEG_GAP + P.FORK_LEG_T
        add("caster axle bolt", "M8", (P.CASTER_X - P.CASTER_TRAIL, sy * (P.CASTER_Y + leg_out), P.CASTER_TIRE_D / 2), (0, -sy, 0), 140.0, [f"fork_{nm}", f"caster_rim_{nm}", f"caster_tire_{nm}"])
    # 6. deck anchors and enclosure
    for sy in (1, -1):
        for gx, key in ((P.CROSS_REAR_X, "rear"), (P.CROSS_FRONT_X, "front")):
            for off in P.CROSS_INSERTS[key]:
                add("deck to cross member bolt", "M5", (gx, sy * off, P.DECK_TOP), (0, 0, -1), 15.0, "deck_front_left")
        for dx in (-P.LEG_TOP_DX, P.LEG_TOP_DX):
            add("deck to leg bolt", "M5", (P.LEG_X + dx, sy * P.LEG_Y, P.DECK_TOP), (0, 0, -1), 15.0, "deck_front_left")
    fx, fy = P.ENC_FEET
    for sx in (1, -1):
        for sy in (1, -1):
            add("enclosure foot bolt", "M4", (P.ENC_X + sx * fx / 2, sy * fy / 2, P.DECK_TOP + 6.0), (0, 0, -1), 12.0, "enclosure_tub")
    # 7. skirts (bolted before the deck goes on) and canopy
    for (gx, gy) in P.BATTERY_FEET:
        add("battery tray bolt", "M4", (gx, gy, P.CH_LID_TOP + 4.0), (0, 0, -1), 10.0, "battery_tray")
    for sy, nm in ((1, "left"), (-1, "right")):
        for key, lid_cx in (("rear", P.CH_REAR + L / 2), ("front", P.CH_FRONT - L / 2)):
            for hx in chassis.SIDE_SKIRT_HOLES:
                add("side skirt bolt", "M4", (lid_cx + hx, sy * (P.CH_W / 2 - 9.0), P.CH_LID_TOP + 4.0), (0, 0, -1), 10.0, f"skirt_side_{key}_{nm}")
    for y in chassis.END_SKIRT_HOLES:
        add("rear skirt bolt", "M4", (P.CH_REAR + 9.0, y, P.CH_LID_TOP + 4.0), (0, 0, -1), 10.0, "skirt_rear")
        add("front skirt bolt", "M4", (P.CH_FRONT - 9.0, y, P.CH_LID_TOP + 4.0), (0, 0, -1), 10.0, "skirt_front")
    for sy in (1, -1):
        for x in shell.side_tab_xs():
            add("canopy to skirt screw", "M4", (x, sy * (P.CANOPY_W / 2 + 1.0), shell.SKIRT_TAB_Z), (0, -sy, 0), 12.0, "canopy_rear_right")
        for (x, z) in shell.FENDER_FLANGE_PTS:
            add("fender bolt", "M4", (x, sy * (P.CANOPY_W / 2 + 4.0), z), (0, -sy, 0), 16.0, "fender_right")
    # 8. mast
    for dx in (-40, 40):
        for dy in (-20, 20):
            add("mast standoff bolt", "M4", (P.MAST_X + dx, dy, P.DECK_TOP + 6.0), (0, 0, -1), 10.0, "mast_standoff")
            add("mast base bolt", "M5", (P.MAST_X + dx, dy, P.CANOPY_Z1 + 8.0), (0, 0, -1), 25.0, "mast_base")
    return J


# ---------------------------------------------------------------------------------------------
def main():
    t0 = time.time()
    get = A.build_all()
    seq = list(A.placements())
    order = [inst for inst, *_ in seq]
    placed = {}
    for inst, part, step, ops in seq:
        placed[inst] = A.apply(get(part), ops)
    env = envelopes()
    print(f"built and placed {len(seq)} instances in {time.time() - t0:.0f}s")

    def present_solids(upto_inst=None, only=None):
        if only is not None:
            return [placed[n] for n in only]
        idx = order.index(upto_inst)
        names = order[: idx + 1]
        solids = [placed[n] for n in names]
        for ename, esolid, after in env:
            if after in names:
                solids.append(esolid)
        return solids

    report = {"sweeps": [], "joints": []}

    # 1. insertion sweeps
    print("insertion sweeps...")
    for i, (inst, part, step, ops) in enumerate(seq):
        partner = FIT_PARTNERS.get(part)
        prior = [placed[n] for n in order[:i] if not (partner and seq[order.index(n)][1] == partner)]
        for ename, esolid, after in env:
            if after in order[:i]:
                prior.append(esolid)
        d = insertion_dir(inst)
        blocked = None
        for k in range(1, SWEEP_STEPS + 1):
            off = SWEEP_MM * k / SWEEP_STEPS
            moved = placed[inst].translate((d[0] * off, d[1] * off, d[2] * off))
            v = vol_in(moved, prior)
            if v > 50.0:
                blocked = (off, v)
                break
        report["sweeps"].append((inst, part, step, d, blocked))
        if blocked:
            print(f"  BLOCKED {inst} ({part}) moving along {d}: hits {blocked[1] / 1000:.1f} cm3 at {blocked[0]:.0f} mm out")

    # 2 + 3. bolts
    print("bolt alignment and driver access...")
    for j in joints():
        solids = present_solids(only=j["present"]) if isinstance(j["present"], list) else present_solids(j["present"])
        d = j["dir"]
        shank = cyl_along(j["head"], d, P.CLEAR[j["size"]] - 1.0, j["length"])
        hit = vol_in(shank, solids)
        back = (-d[0], -d[1], -d[2])
        start = tuple(j["head"][i] + back[i] * HEAD_H for i in range(3))
        driver = cyl_along(start, back, DRIVER_D, DRIVER_L)
        access = vol_in(driver, solids)
        report["joints"].append((j, hit, access))
        if hit > HOLE_TOL or access > HOLE_TOL:
            print(f"  {j['name']:40s} {j['size']:4s} at ({j['head'][0]:.0f}, {j['head'][1]:.0f}, {j['head'][2]:.0f}): "
                  f"{'hole blocked ' + format(hit / 1000, '.2f') + ' cm3 ' if hit > HOLE_TOL else ''}{'driver blocked ' + format(access / 1000, '.2f') + ' cm3' if access > HOLE_TOL else ''}")

    # report
    n_block = sum(1 for s in report["sweeps"] if s[4])
    n_hole = sum(1 for j, h, a in report["joints"] if h > HOLE_TOL)
    n_acc = sum(1 for j, h, a in report["joints"] if a > HOLE_TOL)
    lines = ["# Virtual assembly audit", "",
             f"Generated by `cad/audit.py`. {len(seq)} placed parts, {len(report['joints'])} fasteners checked.", "",
             "| Check | Result |", "|---|---|",
             f"| Insertion sweeps (part can reach its position in build order) | {len(seq) - n_block} of {len(seq)} clear |",
             f"| Bolt holes line up through every joined part | {len(report['joints']) - n_hole} of {len(report['joints'])} clear |",
             f"| Driver can reach the bolt head at that point in the build | {len(report['joints']) - n_acc} of {len(report['joints'])} clear |", ""]
    if n_block:
        lines += ["## Blocked insertions", "", "| Part | Direction it comes from | Collides at |", "|---|---|---|"]
        for inst, part, step, d, b in report["sweeps"]:
            if b:
                lines.append(f"| {inst} ({part}) | {d} | {b[0]:.0f} mm out, {b[1] / 1000:.1f} cm3 |")
        lines.append("")
    bad = [(j, h, a) for j, h, a in report["joints"] if h > HOLE_TOL or a > HOLE_TOL]
    if bad:
        lines += ["## Fastener problems", "", "| Fastener | Size | Head at (x, y, z) | Hole | Driver |", "|---|---|---|---|---|"]
        for j, h, a in bad:
            lines.append(f"| {j['name']} | {j['size']} | ({j['head'][0]:.0f}, {j['head'][1]:.0f}, {j['head'][2]:.0f}) | {'blocked' if h > HOLE_TOL else 'ok'} | {'blocked' if a > HOLE_TOL else 'ok'} |")
        lines.append("")
    lines += ["## Build order used", ""]
    cur = None
    for inst, part, step, d, b in report["sweeps"]:
        if step != cur:
            lines.append(f"- Step {step}:")
            cur = step
        lines.append(f"  - {inst} ({part}), from {d}")
    lines += ["", "## Fasteners checked", "", "| Fastener | Size | Count |", "|---|---|---|"]
    counts = {}
    for j, h, a in report["joints"]:
        counts[(j["name"], j["size"])] = counts.get((j["name"], j["size"]), 0) + 1
    for (nm, sz), n in counts.items():
        lines.append(f"| {nm} | {sz} | {n} |")
    with open(OUT_MD, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"\n{n_block} blocked insertions, {n_hole} misaligned holes, {n_acc} inaccessible bolts. Report: {OUT_MD}  ({time.time() - t0:.0f}s)")
    sys.exit(1 if (n_block or n_hole or n_acc) else 0)


if __name__ == "__main__":
    main()
