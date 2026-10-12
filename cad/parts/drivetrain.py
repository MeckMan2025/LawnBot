"""Rear drive: axle housing, motor mount bracket, wheel, bearing spacer, TPU tread.

Each part is modelled with its rotation axis along Z (print orientation).
"""
import cadquery as cq

import params as P
from lib.features import (Part, box, cylinder, tube, cut_cyl, through_holes, insert_holes, polar, square_pattern, cbore_holes)

B6808 = P.BEARING["6808"]


def axle_housing():
    fx, fz = P.AXLE_FLANGE
    px, pz = P.AXLE_FLANGE_PATTERN

    def build():
        h = box(fx, fz, P.AXLE_FLANGE_T)
        h = h.edges("|Z").fillet(6.0)
        tube_len = P.AXLE_HOUSING_LEN - P.AXLE_FLANGE_T
        h = h.union(cylinder(P.AXLE_HOUSING_OD + P.SHAFT_FIT, tube_len, 0, 0, P.AXLE_FLANGE_T))
        # fillet-like gusset ring at the flange
        h = h.union(cylinder(P.AXLE_HOUSING_OD + 12.0, 6.0, 0, 0, P.AXLE_FLANGE_T))
        h = h.union(cq.Workplane("XY").circle((P.AXLE_HOUSING_OD + 12.0) / 2).workplane(offset=6.0)
                    .circle(P.AXLE_HOUSING_OD / 2).loft().translate((0, 0, P.AXLE_FLANGE_T + 6.0)))
        h = cut_cyl(h, P.AXLE_HOUSING_BORE, P.AXLE_HOUSING_LEN + 2, 0, 0, -1)
        h = cut_cyl(h, P.AXLE_HOUSING_COUPLER_BORE, P.AXLE_HOUSING_COUPLER_LEN + 1, 0, 0, -1)   # coupler sits here
        # bolt heads sit in counterbores on the wheel side (z = flange top) so they clear the hub
        h = cbore_holes(h, "M5", [(dx, dz) for dx in (-px / 2, px / 2) for dz in (-pz / 2, pz / 2)], P.AXLE_FLANGE_T, P.AXLE_FLANGE_T, 6.0)
        # lead-in chamfer at the tip for the bearings
        h = h.faces(">Z").edges().chamfer(1.0)
        return h
    return build


def motor_mount():
    fx, fz = P.AXLE_FLANGE
    px, pz = P.AXLE_FLANGE_PATTERN

    def build():
        t = 6.0
        m = box(fx, fz, t).edges("|Z").fillet(6.0)
        m = m.union(cylinder(50.0, P.MOTOR_MOUNT_STANDOFF, 0, 0, t))
        m = cut_cyl(m, P.AXLE_HOUSING_COUPLER_BORE, 100, 0, 0, -1)
        m = through_holes(m, "M5", [(dx, dz) for dx in (-px / 2, px / 2) for dz in (-pz / 2, pz / 2)], 0, t)
        # motor face pattern: M4 through holes (bolts into the gearbox's threaded face); pilot recess for the boss.
        # The heads are counterbored into the wall face, because the motor is bolted on before the bracket meets the wall.
        m = through_holes(m, "M4", square_pattern(P.MOTOR_PATTERN), 0, t + P.MOTOR_MOUNT_STANDOFF)
        for (x, y) in square_pattern(P.MOTOR_PATTERN):
            m = cut_cyl(m, P.HEAD_D["M4"] + 0.6, 5.0, x, y, -1)
        m = cut_cyl(m, P.MOTOR_BOSS_D + 0.4, 3.0, 0, 0, t + P.MOTOR_MOUNT_STANDOFF - 2.0)
        return m
    return build


def wheel():
    rim_od, rim_id = P.RIM_D, P.RIM_D - 10.0
    w = P.WHEEL_W
    bore = B6808[1] + P.BEARING_SEAT_FIT
    web_z = w - P.WHEEL_WEB_T

    def build():
        wh = tube(rim_od, rim_id, w)
        # retention ribs on the rim OD
        for z in (10.0, w / 2 - 3.0, w - 16.0):
            wh = wh.union(tube(rim_od + 6.0, rim_od - 2.0, 6.0, 0, 0, z))
        # hub boss: bore for the two bearings and the spacer, closed by the outer web
        wh = wh.union(cylinder(P.HUB_OD, w))
        wh = cut_cyl(wh, bore, web_z + 1, 0, 0, -1)
        # spokes
        for ang in range(0, 360, 60):
            spoke = box(rim_id / 2 - P.HUB_OD / 2 + 8.0, 14.0, w - 10.0, (rim_id / 2 + P.HUB_OD / 2) / 2 - 2.0, 0, 5.0)
            wh = wh.union(spoke.rotate((0, 0, 0), (0, 0, 1), ang))
        # mud web between the spokes
        wh = wh.union(tube(rim_id + 2.0, P.HUB_OD - 2.0, 3.0, 0, 0, w / 2 - 1.5))
        # outer web: REX hub bolt pattern and shaft clearance
        wh = cut_cyl(wh, P.REX_HUB_CLEAR_D, 20, 0, 0, web_z - 1)
        wh = through_holes(wh, "M4", square_pattern(P.REX_HUB_PATTERN), web_z, 7.0)
        # bearing lead-in chamfer
        wh = wh.faces("<Z").edges("%CIRCLE").edges(cq.selectors.RadiusNthSelector(0)).chamfer(0.8)
        return wh
    return build


def bearing_spacer():
    length = P.WHEEL_W - P.WHEEL_WEB_T - 2 * (B6808[2] + 0.3)

    def build():
        return tube(B6808[1] - 0.5, B6808[1] - 9.0, length)
    return build


def tread():
    od, idd, w = P.WHEEL_D, P.RIM_D - 1.0, P.WHEEL_W

    def build():
        t = tube(od, idd, w)
        t = t.edges("%CIRCLE").edges(cq.selectors.RadiusNthSelector(-1)).chamfer(3.0)
        # grooves matching the rim ribs (slightly wider)
        for z in (10.0, w / 2 - 3.0, w - 16.0):
            t = t.cut(tube(P.RIM_D + 7.0, idd - 1.0, 6.6, 0, 0, z - 0.3))
        # shallow turf grooves around the outside: wide, rounded, low-impact
        for ang in range(0, 360, 15):
            g = box(8.0, 3.0, w - 16.0, od / 2, 0, 8.0).rotate((0, 0, 0), (0, 0, 1), ang)
            t = t.cut(g)
        return t
    return build


def parts():
    return [
        Part("drive_axle_housing", axle_housing(), 2, "PETG",
             "Flange bolts to the rear module outer wall with 4x M5 x 35 (heads in the counterbores, nuts on the motor mount inside). Fit before the wheel. Tube carries both 6808 bearings.",
             walls=6, infill=60, orientation="flange down"),
        Part("motor_mount_bracket", motor_mount(), 2, "PETG",
             "Inside the chassis. Shares the M5 bolts with the axle housing. 4x M4 x 16 bolt the motor face through the standoff; the clamping coupler sits inside the housing's 20 mm bore.",
             walls=5, infill=40, orientation="plate down"),
        Part("drive_wheel", wheel(), 2, "PETG",
             "284 mm rim and hub in one piece. Press both 6808 bearings in from the inner (flat) face with the spacer between them. goBILDA REX hub bolts to the outer web.",
             walls=4, infill=25, orientation="inner face down", tags=("large",)),
        Part("bearing_spacer", bearing_spacer(), 2, "PETG", "Sits between the two 6808 bearings inside the hub.", walls=4, infill=100),
        Part("drive_tread", tread(), 2, "TPU 95A",
             "Stretch over the rim; the three grooves snap onto the rim ribs. Print with 3 walls and 20 percent gyroid.",
             walls=3, infill=20, orientation="flat", tags=("large", "tpu")),
    ]
