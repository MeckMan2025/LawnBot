"""Charging dock: four lap-jointed floor tiles, guide rails, contact block, rain cover, AprilTag frame.

The robot reverses onto the dock: the rails steer the caster tires, the rear contact pads meet the
spring contacts in the block.
"""
import cadquery as cq

import params as P
from lib.features import (Part, box, cylinder, cut_cyl, through_holes, insert_holes, holes_x, cyl_x)

TL, TW, TT = P.DOCK_TILE


def tile():
    def build():
        t = box(TL, TW, TT)
        # lap tabs on +x and +y edges (bottom half), matching pockets on -x and -y edges (top half removed)
        t = t.union(box(20.0, TW - 20.0, TT / 2, TL / 2 + 10.0, 0, 0))
        t = t.union(box(TL - 20.0, 20.0, TT / 2, 0, TW / 2 + 10.0, 0))
        t = t.cut(box(20.4, TW + 2, TT / 2 + 1, -TL / 2 + 10.0, 0, TT / 2))
        t = t.cut(box(TL + 2, 20.4, TT / 2 + 1, 0, -TW / 2 + 10.0, TT / 2))
        # lap bolts (M5) and ground stake holes (10 mm) at the corners
        t = through_holes(t, "M5", [(TL / 2 + 10.0, y) for y in (-100.0, 0.0, 100.0)], 0, TT)
        t = through_holes(t, "M5", [(x, TW / 2 + 10.0) for x in (-90.0, 0.0, 90.0)], 0, TT)
        t = through_holes(t, "M5", [(-TL / 2 + 10.0, y) for y in (-100.0, 0.0, 100.0)], 0, TT)
        t = through_holes(t, "M5", [(x, -TW / 2 + 10.0) for x in (-90.0, 0.0, 90.0)], 0, TT)
        for sx in (1, -1):
            for sy in (1, -1):
                t = cut_cyl(t, 10.5, TT + 2, sx * (TL / 2 - 40.0), sy * (TW / 2 - 40.0), -1)
        # rail and block mounting inserts on a 60 mm grid
        pts = [(x, y) for x in (-90.0, -30.0, 30.0, 90.0) for y in (-120.0, -60.0, 0.0, 60.0, 120.0)]
        t = insert_holes(t, "M5", pts, TT, 9.0)
        # drainage grooves on top
        for x in (-60.0, 0.0, 60.0):
            t = t.cut(box(3.0, TW - 60.0, 2.0, x, 0, TT - 2.0))
        return t
    return build


def rail():
    def build():
        r = (cq.Workplane("YZ").polyline([(-10.0, 0), (10.0, 0), (6.0, 40.0), (-6.0, 40.0)]).close()
             .extrude(P.DOCK_RAIL_L / 2, both=True))
        r = r.union(box(P.DOCK_RAIL_L, 40.0, 5.0))
        r = through_holes(r, "M5", [(x, dy) for x in (-90.0, -30.0, 30.0, 90.0) for dy in (-15.0, 15.0)], 0, 5.0)
        # half-lap end so two halves make one straight rail
        r = r.cut(box(20.0, 30.0, 25.0, P.DOCK_RAIL_L / 2 - 10.0, 0, 20.0))
        r = r.union(box(20.0, 12.0, 20.0, -P.DOCK_RAIL_L / 2 - 10.0, 0, 0))
        return r
    return build


def contact_block():
    def build():
        b = box(40.0, 140.0, 150.0)
        b = b.cut(box(32.0, 132.0, 150.0, 0, 0, 4.0))                 # hollow, open at the top for a lid
        b = b.union(box(40.0, 140.0, 4.0, 0, 0, 146.0))
        b = b.union(box(80.0, 160.0, 5.0))                            # foot flange
        b = through_holes(b, "M5", [(x, y) for x in (-30.0, 30.0) for y in (-60.0, 60.0)], 0, 5.0)
        b = b.cut(box(32.0, 132.0, 20.0, 0, 0, -1))
        # spring contact windows facing the robot (+x), at the robot pad height
        for y in (-50.0, 50.0):
            b = b.cut(box(20.0, 24.0, 14.0, 20.0, y, P.CH_BOTTOM + 30.0 - 7.0 - TT))
        return b
    return build


def rain_cover():
    def build():
        c = box(100.0, 220.0, 5.0).edges("|Z").fillet(10.0)
        for y in (-80.0, 80.0):
            c = c.union(box(12.0, 12.0, 60.0, -30.0, y, -60.0))
        c = through_holes(c, "M4", [(-30.0, -80.0), (-30.0, 80.0)], -60.0, 10.0)
        return c
    return build


def tag_frame():
    def build():
        f = box(140.0, 140.0, 6.0)
        f = f.cut(box(120.0, 120.0, 4.0, 0, 0, 2.0))
        f = f.cut(box(110.0, 110.0, 10.0, 0, 0, -1))
        f = f.union(box(140.0, 10.0, 30.0, 0, -65.0, -30.0))
        f = through_holes(f, "M4", [(-50.0, -65.0), (50.0, -65.0)], -30.0, 10.0)
        return f
    return build


def parts():
    return [
        Part("dock_tile", tile(), 4, "PETG", "275 x 310 floor tile with the lap tabs. Four tiles lap together with M5 x 20; 10 mm ground stakes at the corners.", walls=3, infill=15, tags=("large",)),
        Part("dock_rail_half", rail(), 4, "PETG", "Two halves per rail. Bolt to the tile inserts to funnel the caster tires.", walls=3, infill=20),
        Part("dock_contact_block", contact_block(), 1, "PETG", "Holds two spring contacts facing the robot's rear pads. Bolt to the tiles.", walls=4, infill=25),
        Part("dock_rain_cover", rain_cover(), 1, "PETG", "Over the contact block. Print upside down.", walls=3, infill=20, orientation="upside down"),
        Part("dock_tag_frame", tag_frame(), 1, "PETG", "Holds a 120 mm printed AprilTag for final docking alignment. Bolts to the rain cover posts.", walls=3, infill=20),
    ]
