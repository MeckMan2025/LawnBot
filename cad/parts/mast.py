"""Sensor mast: standoff, base, tube segments, pan base, tilt bracket, camera housing, window, GPS mount.

All tube joints are a 30 mm spigot into the next tube's bore with an M4 cross bolt.
"""
import cadquery as cq

import params as P
from lib.features import (Part, box, cylinder, tube, cut_cyl, insert_holes, through_holes, holes_x, holes_y, cbore_holes, cyl_x, cyl_y)

OD, WALL = P.MAST_OD, P.MAST_WALL
BORE = OD - 2 * WALL                 # 32
SPIGOT = BORE - 0.3
SPIGOT_L = 30.0
SW, SD, SH = P.SERVO                 # 40.5 x 20.5 x 40 (body), horn on top
STANDOFF_H = P.CANOPY_Z1 - P.CANOPY_WALL - P.DECK_TOP   # 102


def standoff():
    def build():
        s = tube(60.0, 50.0, STANDOFF_H)
        s = s.union(box(100.0, 50.0, 6.0))
        s = through_holes(s, "M4", [(dx, dy) for dx in (-40, 40) for dy in (-20, 20)], 0, 6.0)
        s = s.union(cylinder(80.0, 6.0, 0, 0, STANDOFF_H - 6.0))
        s = s.union(tube(60.0, 20.0, 6.0, 0, 0, STANDOFF_H - 6.0))
        s = insert_holes(s, "M5", [(dx, dy) for dx in (-40, 40) for dy in (-20, 20)], STANDOFF_H, 9.0)
        # wire exit at the bottom
        s = s.cut(cyl_x(20.0, 40.0, 10.0, 0, 20.0))
        return s
    return build


def base():
    def build():
        b = cylinder(90.0, 8.0)
        b = through_holes(b, "M5", [(dx, dy) for dx in (-40, 40) for dy in (-20, 20)], 0, 8.0)
        b = b.union(cylinder(SPIGOT, SPIGOT_L + 8.0, 0, 0, 0))
        b = cut_cyl(b, 20.0, 100, 0, 0, -1)
        b = b.cut(cyl_x(P.CLEAR["M4"], 60, -30, 0, 8.0 + SPIGOT_L - 12.0))
        return b
    return build


def segment():
    def build():
        s = tube(OD, BORE, P.MAST_SEG_L)
        s = s.union(tube(OD, 20.0, 4.0, 0, 0, P.MAST_SEG_L - 4.0))      # web joins tube and spigot
        s = s.union(tube(SPIGOT, 20.0, SPIGOT_L, 0, 0, P.MAST_SEG_L))
        s = s.cut(cyl_x(P.CLEAR["M4"], 60, -30, 0, P.MAST_SEG_L + SPIGOT_L - 12.0))
        s = s.cut(cyl_x(P.CLEAR["M4"], 60, -30, 0, 18.0))
        return s
    return build


def pan_base():
    def build():
        b = box(56.0, 56.0, 70.0).edges("|Z").fillet(6.0)
        b = cut_cyl(b, BORE, SPIGOT_L + 2.0, 0, 0, -1)
        b = b.cut(cyl_x(P.CLEAR["M4"], 80, -40, 0, 18.0))
        # servo pocket, open at the top, horn centred
        b = b.cut(box(SW, SD, SH + 1, 0, 0, 70.0 - SH))
        b = b.cut(box(SW + 16.0, 8.0, 8.0, 0, 0, 70.0 - 8.0))          # ear slots
        b = b.cut(box(10.0, 14.0, 30.0, -SW / 2 - 4.0, 0, 70.0 - SH))     # wire channel
        b = b.cut(cyl_x(14.0, 30.0, -28.0 - 10.0, 0, 20.0))               # wire exit to the mast bore
        # GPS bracket inserts on the rear face
        b = b.cut(cyl_x(P.INSERT["M4"][0], 9.0, -28.0 - 0.01, 0, 40.0))
        b = b.cut(cyl_x(P.INSERT["M4"][0], 9.0, -28.0 - 0.01, 0, 58.0))
        return b
    return build


def tilt_bracket():
    """U bracket: floor plate bolts to the pan servo horn, arms carry the tilt axis."""
    def build():
        t = box(70.0, 60.0, 4.0)
        t = through_holes(t, "M3", [(dx, dy) for dx in (-10, 10) for dy in (-10, 10)], 0, 4.0)   # 25 mm horn pattern
        t = cut_cyl(t, 8.0, 10, 0, 0, -1)
        for sy in (1, -1):
            arm = box(50.0, 4.0, 64.0, 0, sy * 28.0, 0)
            t = t.union(arm)
        # tilt axis: servo pocket on one arm, 6 mm bearing-less pivot hole on the other
        t = t.cut(box(SW, SD + 2, SH + 2, 0, 28.0, 64.0 - 26.0))
        t = t.cut(cyl_y(6.4, 10, 0, -28.0 - 5.0, 48.0))
        return t
    return build


def camera_housing():
    def build():
        h = box(60.0, 50.0, 64.0).edges("|Y").fillet(5.0)
        h = h.cut(box(52.0, 42.0, 56.0, 0, 0, 4.0))
        # window opening on the front (+x) face and a recess for the window plate
        h = h.cut(box(10.0, 36.0, 26.0, 30.0, 0, 20.0))
        h = h.cut(box(3.0, 42.0, 32.0, 30.0 - 1.0, 0, 17.0))
        # IR illuminator hole beside the window
        h = h.cut(cyl_x(11.0, 20.0, 20.0, 0, 54.0))
        # Pi Camera Module 3 sits on four standoffs on an internal bulkhead behind the window
        h = h.union(box(3.0, 44.0, 57.0, 15.5, 0, 3.5))
        h = h.cut(box(5.0, 20.0, 5.0, 15.5, 0, 50.0))                   # ribbon cable slot
        pts = [(dx, dy) for dx in (-10.5, 10.5) for dy in (-6.25, 6.25)]
        for (y, z) in pts:
            h = h.union(cyl_x(5.0, 6.0, 17.0, y, 32.0 + z))
            h = h.cut(cyl_x(1.8, 8.0, 16.0, y, 32.0 + z))
        # pivot stubs on both sides at the tilt axis (z = 32): horn recess (+y) and 6 mm pin (-y)
        h = h.union(cyl_y(6.0, 8.0, 0, -32.0, 32.0))
        h = h.cut(cyl_y(21.0, 2.5, 0, 25.0 - 0.01, 32.0))                 # servo horn recess
        h = h.cut(cyl_y(P.CLEAR["M3"], 10, 0, 20.0, 32.0))
        # cable slot at the rear bottom
        h = h.cut(box(12.0, 8.0, 12.0, -30.0, 0, -1))
        # rear lid is the open -x face; add two M3 inserts for a cover plate
        h = h.cut(cyl_x(P.INSERT["M3"][0], 7.0, -30.0 - 0.01, 18.0, 58.0))
        h = h.cut(cyl_x(P.INSERT["M3"][0], 7.0, -30.0 - 0.01, -18.0, 58.0))
        return h
    return build


def camera_cover():
    def build():
        c = box(3.0, 50.0, 64.0)
        c = c.cut(cyl_x(P.CLEAR["M3"], 10, -5, 18.0, 58.0))
        c = c.cut(cyl_x(P.CLEAR["M3"], 10, -5, -18.0, 58.0))
        return c
    return build


def window():
    def build():
        return box(2.6, 41.4, 31.4)
    return build


def gps_mount():
    def build():
        g = box(8.0, 40.0, 60.0, -4.0, 0, 0)
        g = g.cut(cyl_x(P.CLEAR["M4"], 20, -10, 0, 30.0))
        g = g.cut(cyl_x(P.CLEAR["M4"], 20, -10, 0, 48.0))
        g = g.union(box(50.0, 40.0, 6.0, -8.0 - 25.0 + 4.0, 0, 54.0))
        cup = cylinder(P.GPS_PUCK_D + 10.0, 14.0, -54.0, 0, 54.0)
        cup = cup.cut(cylinder(P.GPS_PUCK_D, 12.0, -54.0, 0, 56.0))
        g = g.union(cup)
        g = g.cut(box(12.0, 8.0, 14.0, -54.0 - 30.0, 0, 55.0))     # cable slot
        return g
    return build


def parts():
    return [
        Part("mast_standoff", standoff(), 1, "PETG", "Deck grid to canopy roof. 4x M4 x 12 down into the deck, 4x M5 inserts on top for the mast base through the roof.", walls=5, infill=40),
        Part("mast_base", base(), 1, "PETG", "Sits on the canopy roof over the standoff. 4x M5 x 25. First tube slides over the spigot, M4 cross bolt.", walls=5, infill=50),
        Part("mast_segment", segment(), P.MAST_SEGMENTS, "PETG", "200 mm tube with a 30 mm spigot. Print standing. M4 x 45 cross bolts.", walls=4, infill=30, orientation="standing"),
        Part("pan_base", pan_base(), 1, "PETG", "Top of the mast. Standard-size pan servo drops in from the top.", walls=4, infill=30),
        Part("tilt_bracket", tilt_bracket(), 1, "PETG", "Bolts to the pan servo horn (25 mm pattern). Tilt servo in one arm, 6 mm pin on the other.", walls=4, infill=30, supports=True),
        Part("camera_housing", camera_housing(), 1, "PETG", "Pi Camera Module 3 on M2 screws, IR LED in the side hole. Rear cover on 2x M3.", walls=3, infill=20, orientation="open back down", supports=True),
        Part("camera_cover", camera_cover(), 1, "PETG", "Rear cover for the camera housing.", walls=3, infill=20, orientation="flat"),
        Part("camera_window", window(), 1, "clear PETG", "Press into the housing recess; seal with a bead of silicone.", walls=2, infill=100, orientation="flat"),
        Part("gps_mount", gps_mount(), 1, "PETG", "L bracket off the pan base rear face holding a 60 mm GPS puck. 2x M4.", walls=4, infill=30, supports=True),
    ]
