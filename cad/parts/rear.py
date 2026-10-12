"""Rear deck fittings: E-stop housing, charge port housing, light bar housing, robot-side charge contacts."""
import cadquery as cq

import params as P
from lib.features import (Part, box, cylinder, cut_cyl, insert_holes, through_holes, holes_x, cyl_x, cyl_y)


def estop_housing():
    def build():
        h = box(56.0, 56.0, 45.0).edges("|Z").fillet(6.0)
        h = h.cut(box(48.0, 48.0, 45.0, 0, 0, -1))         # open bottom
        h = h.union(box(56.0, 56.0, 5.0, 0, 0, 40.0))      # top plate
        h = cut_cyl(h, 22.5, 20, 0, 0, 35.0)
        h = h.union(box(76.0, 76.0, 4.0))                  # foot flange
        h = h.cut(box(48.0, 48.0, 10.0, 0, 0, -1))
        h = through_holes(h, "M3", [(dx, dy) for dx in (-32, 32) for dy in (-32, 32)], 0, 4.0)
        h = h.cut(cyl_x(10.0, 20.0, -35.0, 0, 12.0))      # wire exit
        return h
    return build


def charge_port_housing():
    """Bolts on the rear face of the canopy. Two spring-loaded contact pads face rearward."""
    def build():
        h = box(26.0, 60.0, 44.0)
        h = h.union(box(6.0, 80.0, 60.0, -10.0, 0, -8.0))       # flange against the canopy
        h = through_holes_x(h, "M4", [(-32.0, 0.0), (32.0, 0.0), (-32.0, 44.0), (32.0, 44.0)], -14.0, 8.0)
        for y in (-18.0, 18.0):
            h = h.cut(box(20.0, 12.0, 30.0, 6.0, y, 7.0))           # contact pocket: 10 x 30 spring pad
            h = h.cut(cyl_x(6.0, 30.0, -20.0, y, 22.0))             # wire bore through the flange
        h = h.union(box(26.0, 64.0, 4.0, 0, 0, 44.0))               # rain lip
        return h
    return build


def through_holes_x(solid, size, yz_points, x0, length):
    return holes_x(solid, P.CLEAR[size], yz_points, x0, length)


def light_bar_housing():
    def build():
        l = box(180.0, 16.0, 14.0)
        l = l.cut(box(176.0, 12.5, 10.0, 0, 0, 2.0))               # 12 mm LED strip channel
        l = l.cut(box(176.0, 8.0, 6.0, 0, 0, 10.0))                # diffuser lip opening
        for x in (-80.0, 80.0):
            l = l.union(box(12.0, 16.0, 14.0, x, 0, 0))
        for x in (-80.0, 80.0):
            l = l.cut(cyl_y(P.CLEAR["M3"], 30.0, x, -15.0, 7.0))
        l = cut_cyl(l, 12.5, 20, 0, 0, -1)                         # buzzer mounts through the centre
        return l
    return build


def contact_pads():
    """Robot-side copper pad carrier: two 20 x 10 pads at z = 120 on the rear of the chassis."""
    def build():
        c = box(8.0, 120.0, 30.0)
        for y in (-50.0, 50.0):
            c = c.cut(box(2.5, 22.0, 12.0, 3.0, y, 9.0))
            c = c.cut(cyl_x(5.0, 20.0, -10.0, y, 15.0))
        c = holes_x(c, P.CLEAR["M4"], [(-20.0, 15.0), (20.0, 15.0)], -10.0, 20.0)
        return c
    return build


def parts():
    return [
        Part("estop_housing", estop_housing(), 1, "PETG", "22 mm mushroom E-stop. 4x M3 through the canopy roof.", walls=3, infill=20),
        Part("charge_port_housing", charge_port_housing(), 1, "PETG", "Rear face of the canopy. Two 10 x 30 mm spring pads face the dock.", walls=4, infill=30, supports=True),
        Part("light_bar_housing", light_bar_housing(), 1, "PETG", "12 mm LED strip plus a 12 mm buzzer. 2x M3 into the canopy rear face.", walls=3, infill=20),
        Part("contact_pad_carrier", contact_pads(), 1, "PETG", "Rear of the chassis, carries the two copper charge pads. 2x M4.", walls=3, infill=30),
    ]
