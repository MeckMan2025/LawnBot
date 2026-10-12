"""Low chassis: four tray modules, two lid plates, battery tray, dowels.

Module frame: module center at the origin, bottom face at z = 0 (print orientation).
sx = +1 for front modules, -1 for rear. sy = +1 for left, -1 for right.
The seam walls (toward the chassis center) are thicker and carry bolts and dowels.
"""
import cadquery as cq

import params as P
from lib.features import (Part, box, cylinder, tray, insert_holes, through_holes, holes_x, holes_y,
                          dowel_holes, cbore_holes, grid, square_pattern, cut_cyl)

L, W, H = P.MOD_L, P.MOD_W, P.CH_H
WALL, SEAM, FLOOR = P.CH_WALL, P.SEAM_WALL, P.CH_FLOOR
BOSS = 12.0
SEAM_BOLT_Z = (25.0, 65.0)
SEAM_BOLT_Y = (-45.0, 45.0)     # on the lateral seam wall (runs along Y)
SEAM_BOLT_X = (-60.0, 10.0)     # on the longitudinal seam wall (runs along X); clear of the motor window
DOWEL_Z = 45.0
SIDE_SKIRT_HOLES = (-30.0, 30.0)           # lid-local x, along each side edge (clear of the skirt ribs and tabs)
END_SKIRT_HOLES = (-140.0, 0.0, 140.0)     # y, along the front and rear edges (clear of the riser feet)


def module_center(sx, sy):
    """Global XY of a module's center."""
    return (P.CH_CX + sx * L / 2.0, sy * W / 2.0)


def boss_points(sx, sy):
    """Lid bolt bosses: inside each corner plus mid outer walls, in module-local XY."""
    pts = []
    for cx in (-1, 1):
        for cy in (-1, 1):
            # pull the boss inward past whichever wall is on that side
            wx = SEAM if cx == -sx else WALL
            wy = SEAM if cy == -sy else WALL
            x = cx * (L / 2 - wx - BOSS / 2)
            if sx > 0 and cx > 0:
                x -= 20.0      # front-outer corner: step back so the riser foot insert boss on the lid clears it
            pts.append((x, cy * (W / 2 - wy - BOSS / 2)))
    pts.append((sx * 60.0, sy * (W / 2 - WALL - BOSS / 2)))    # outer long wall, away from the motor mount
    return pts


def module(sx, sy):
    def build():
        m = tray(L, W, H, WALL, FLOOR, r=5.0)
        # Thicken the two seam walls by adding material inside.
        m = m.union(box(SEAM - WALL, W - 2 * WALL, H - FLOOR, -sx * (L / 2 - WALL - (SEAM - WALL) / 2), 0, FLOOR))
        m = m.union(box(L - 2 * WALL, SEAM - WALL, H - FLOOR, 0, -sy * (W / 2 - WALL - (SEAM - WALL) / 2), FLOOR))
        # Lid bosses (full height, M4 insert at the top)
        for (x, y) in boss_points(sx, sy):
            m = m.union(box(BOSS, BOSS, H - FLOOR, x, y, FLOOR))
        m = insert_holes(m, "M4", boss_points(sx, sy), H)
        # Floor ribs along X
        for y in (-40.0, 0.0, 40.0):
            m = m.union(box(L - 2 * SEAM, 3.0, 8.0, 0, y, FLOOR))
        # Drain holes
        for x in (-50.0, 50.0):
            m = cut_cyl(m, 6.0, FLOOR + 2, x, sy * 20.0, -1)
        # Seam bolts: lateral seam wall at x = -sx*L/2 (holes along X), longitudinal at y = -sy*W/2 (along Y)
        xs = -sx * L / 2
        m = holes_x(m, P.CLEAR["M5"], [(y, z) for y in SEAM_BOLT_Y for z in SEAM_BOLT_Z], xs - 10, 20)
        m = holes_x(m, P.DOWEL_D + P.DOWEL_FIT, [(-15.0, DOWEL_Z), (15.0, DOWEL_Z)], xs - 10, 20)
        ys = -sy * W / 2
        m = holes_y(m, P.CLEAR["M5"], [(x, z) for x in SEAM_BOLT_X for z in SEAM_BOLT_Z], ys - 10, 20)
        m = holes_y(m, P.DOWEL_D + P.DOWEL_FIT, [(-40.0, DOWEL_Z), (0.0, DOWEL_Z)], ys - 10, 20)
        # Rear modules: axle housing flange pattern and coupler hole on the outer long wall
        if sx < 0:
            ax = P.AXLE_X - module_center(sx, sy)[0]
            az = P.AXLE_Z - P.CH_BOTTOM
            px, pz = P.AXLE_FLANGE_PATTERN
            pts = [(ax + dx, az + dz) for dx in (-px / 2, px / 2) for dz in (-pz / 2, pz / 2)]
            yo = sy * W / 2
            m = holes_y(m, P.CLEAR["M5"], pts, yo - 10, 20)
            m = holes_y(m, P.AXLE_HOUSING_COUPLER_BORE + 2.0, [(ax, az)], yo - 10, 20)
        # Front modules: a wire pass-through on the front wall for the bumper/camera loom
        if sx > 0:
            m = holes_x(m, 16.0, [(sy * 30.0, 50.0)], L / 2 - 10, 20)
        return m
    return build


def lid(sx):
    """Lid plate covering the two modules at the same sx. Local frame: lid center, z = 0 bottom."""
    def build():
        lw = 2 * W
        p = box(L, lw, P.LID_T)
        # ribs underneath, inside the modules (the top stays flat for the battery and the feet)
        for y in (-100.0, 100.0):
            p = p.union(box(L - 30, 4.0, 8.0, 0, y, -8.0))
        pts = []
        for sy in (1, -1):
            cy = sy * W / 2
            pts += [(x, y + cy) for (x, y) in boss_points(sx, sy)]
        p = cbore_holes(p, "M4", pts, P.LID_T, P.LID_T, 3.0)
        lid_cx = P.CH_CX + sx * L / 2.0
        # M5 insert points for the feet of the risers, braces and legs. Each gets a boss under the lid so the
        # insert has 14 mm of material (the lid alone is only 6 mm).
        m5 = []
        if sx > 0:
            for sy in (1, -1):
                rx = P.RISER_X - lid_cx
                m5 += square_pattern_xy(P.RISER_PATTERN[0], P.RISER_PATTERN[1], rx, sy * P.RISER_Y)
                bx = P.BRACE_X - lid_cx
                m5 += [(bx - 10, sy * P.RISER_Y + 10), (bx + 10, sy * P.RISER_Y - 10)]
        else:
            for sy in (1, -1):
                lx = P.LEG_X - lid_cx
                m5 += square_pattern_xy(P.LEG_PATTERN[0], P.LEG_PATTERN[1], lx, sy * P.LEG_Y)
        tray_pts = [(gx - lid_cx, gy) for (gx, gy) in P.BATTERY_FEET if abs(gx - lid_cx) < L / 2 - 10]
        for (x, y) in m5 + tray_pts:
            p = p.union(cylinder(12.0, 8.0, x, y, -8.0))
        p = insert_holes(p, "M5", m5, P.LID_T)
        p = insert_holes(p, "M4", tray_pts, P.LID_T)
        # cable pass-through, away from the tray and the feet
        p = cut_cyl(p, 30.0, P.LID_T + 20, sx * 60.0, 0, -1)
        # skirt panel inserts along the outer edges
        edge_pts = [(x, sy * (lw / 2 - 8)) for sy in (1, -1) for x in SIDE_SKIRT_HOLES]
        edge_pts += [(sx * (L / 2 - 8), y) for y in END_SKIRT_HOLES]
        p = insert_holes(p, "M4", edge_pts, P.LID_T, 7.0)
        return p
    return build


def square_pattern_xy(px, py, cx, cy):
    return [(cx + dx, cy + dy) for dx in (-px / 2, px / 2) for dy in (-py / 2, py / 2)]


def battery_tray():
    bl, bw, bh = P.BATTERY
    ow = 160.0                      # outer width; keeps the tabs inside the riser braces

    def build():
        t = box(bl + 12, ow, 20.0).cut(box(bl + 1, bw + 1, 20.0, 0, 0, 4.0))
        # strap slots
        for x in (-50.0, 50.0):
            for sy in (1, -1):
                t = t.cut(box(30.0, 6.0, 30.0, x, sy * (bw / 2 + 2.5), -1))
        # bolt tabs outside the cradle, reachable with the battery in place
        tabs = [(gx - P.BATTERY_X, gy) for (gx, gy) in P.BATTERY_FEET]
        for (x, y) in tabs:
            t = t.union(box(16.0, 16.0, 4.0, x, y, 0))
        t = through_holes(t, "M4", tabs, 0, 4.0)
        return t
    return build


def dowel():
    def build():
        return cylinder(P.DOWEL_D, 16.0).edges().chamfer(0.8)
    return build


def parts():
    out = []
    for sx, sy, nm in ((-1, 1, "rear_left"), (-1, -1, "rear_right"), (1, 1, "front_left"), (1, -1, "front_right")):
        out.append(Part(f"chassis_module_{nm}", module(sx, sy), 1, "PETG",
                        "Open tray. Seam walls bolt to the neighbour with M5 x 20 and nuts; 6 mm dowels locate them.",
                        walls=5, infill=30, orientation="open top up"))
    out.append(Part("chassis_lid_rear", lid(-1), 1, "PETG", "Bolts to the rear modules with M4 x 12. Legs bolt into the M5 inserts.", walls=4, infill=30, orientation="flat, ribs up"))
    out.append(Part("chassis_lid_front", lid(1), 1, "PETG", "Bolts to the front modules with M4 x 12. Risers and braces bolt into the M5 inserts.", walls=4, infill=30, orientation="flat, ribs up"))
    out.append(Part("battery_tray", battery_tray(), 1, "PETG", "Sits on the chassis lid under the deck, just ahead of the axle. 2x M4 into the lid inserts, two 25 mm straps.", walls=3, infill=20))
    out.append(Part("alignment_dowel", dowel(), 16, "PETG", "6 x 16 mm. Print standing up.", walls=3, infill=100))
    return out
