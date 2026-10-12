"""Electronics enclosure: tub, lid, TPU gasket. Sits on the upper deck grid."""
import cadquery as cq

import params as P
from lib.features import (Part, box, cylinder, cut_cyl, tray, insert_holes, through_holes, holes_x, cbore_holes, grid)

L, W, H, WALL = P.ENC_L, P.ENC_W, P.ENC_H, P.ENC_WALL
BOSS = 10.0
FEET_X, FEET_Y = P.ENC_FEET


def lid_boss_points():
    pts = [(sx * (L / 2 - WALL - BOSS / 2), sy * (W / 2 - WALL - BOSS / 2)) for sx in (1, -1) for sy in (1, -1)]
    pts += [(0.0, sy * (W / 2 - WALL - BOSS / 2)) for sy in (1, -1)]
    pts += [(sx * (L / 2 - WALL - BOSS / 2), 0.0) for sx in (1, -1)]
    return pts


def tub():
    def build():
        t = tray(L, W, H, WALL, WALL, r=6.0)
        for (x, y) in lid_boss_points():
            t = t.union(box(BOSS, BOSS, H - WALL, x, y, WALL))
        t = insert_holes(t, "M4", lid_boss_points(), H)
        # mounting feet at the corners, landing on the deck grid
        for sx in (1, -1):
            for sy in (1, -1):
                t = t.union(box(26.0, 26.0, 6.0, sx * FEET_X / 2, sy * FEET_Y / 2, 0))
        t = cbore_holes(t, "M4", [(sx * FEET_X / 2, sy * FEET_Y / 2) for sx in (1, -1) for sy in (1, -1)], 6.0, 6.0, 3.0)
        # Pi 5 standoffs (58 x 49 hole pattern) on the left half of the floor
        pi = [(-60.0 + dx, dy) for dx in (-29.0, 29.0) for dy in (-24.5, 24.5)]
        for (x, y) in pi:
            t = t.union(cylinder(7.0, 6.0, x, y, WALL))
        t = insert_holes(t, "M2.5", pi, WALL + 6.0)
        # M3 insert grid (20 mm) on the right half for the RoboClaw, buck converter and relay on adapter plates
        g = grid(4, 5, 20.0, 20.0, 50.0, 0.0)
        for (x, y) in g:
            t = t.union(cylinder(7.0, 4.0, x, y, WALL))
        t = insert_holes(t, "M3", g, WALL + 4.0)
        # PG9 cable glands on the rear wall, plus one on the front wall for the mast loom
        t = holes_x(t, P.GLAND_D, [(y, 40.0) for y in (-60.0, -20.0, 20.0, 60.0)], -L / 2 - 5, WALL + 10)
        t = holes_x(t, P.GLAND_D, [(0.0, 40.0)], L / 2 - 5, WALL + 10)
        # vent: a baffled slot on each side wall high up (covered by the canopy)
        for sy in (1, -1):
            t = t.cut(box(60.0, WALL + 2, 5.0, 0, sy * (W / 2), H - 12.0))
        return t
    return build


def lid():
    t = P.ENC_LID_T

    def build():
        l = box(L + 8.0, W + 8.0, t).edges("|Z").fillet(8.0)
        # gasket groove on the underside, centered on the tub wall
        gl, gw = L - WALL, W - WALL
        groove = (cq.Workplane("XY").rect(gl + P.GASKET_W, gw + P.GASKET_W).rect(gl - P.GASKET_W, gw - P.GASKET_W)
                  .extrude(P.GASKET_T + 1).translate((0, 0, -1)))
        l = l.cut(groove)
        l = cbore_holes(l, "M4", lid_boss_points(), t, t, 3.5)
        # stiffening ribs on top
        for y in (-50.0, 50.0):
            l = l.union(box(L - 30.0, 3.0, 5.0, 0, y, t))
        return l
    return build


def gasket():
    def build():
        gl, gw = L - WALL, W - WALL
        return (cq.Workplane("XY").rect(gl + P.GASKET_W - 0.4, gw + P.GASKET_W - 0.4)
                .rect(gl - P.GASKET_W + 0.4, gw - P.GASKET_W + 0.4).extrude(P.GASKET_T + 0.6))
    return build


def parts():
    return [
        Part("enclosure_tub", tub(), 1, "PETG", "4x M4 x 12 feet bolts into the deck grid. Pi 5 on M2.5 inserts, other boards on the M3 grid via adapter plates. Fit PG9 glands.", walls=4, infill=25, orientation="open top up"),
        Part("enclosure_lid", lid(), 1, "PETG", "8x M4 x 16 into the tub bosses. Gasket sits in the groove.", walls=4, infill=25, orientation="flat, ribs up"),
        Part("enclosure_gasket", gasket(), 1, "TPU 95A", "Press into the lid groove. 2 walls, 100 percent.", walls=2, infill=100, orientation="flat", tags=("tpu",)),
    ]
