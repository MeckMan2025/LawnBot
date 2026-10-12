"""Front casters, zero-turn mower style: spindle tower, spindle sleeve, yoke fork, rim, tire, spacers.

The tower sits on top of the boom arm pad. The spindle sleeve runs from the yoke crown (below the
pad) up through the pad and the tower, on two 6004 bearings. A 51104 thrust bearing between the
crown and the pad underside carries the weight. An M12 bolt clamps the whole stack.
"""
import cadquery as cq

import params as P
from lib.features import (Part, box, cylinder, tube, cut_cyl, through_holes, bearing_seat, nut_pockets, polar)

B6004 = P.BEARING["6004"]
B608 = P.BEARING["608"]
TIRE_R = P.CASTER_TIRE_D / 2.0
SLEEVE_L = (P.TOWER_Z0 + P.TOWER_H) - P.CROWN_TOP   # 160


def tower():
    def build():
        t = cylinder(P.TOWER_OD, P.TOWER_H)
        # self-supporting skirt out to the square flange at the base
        t = t.union(cq.Workplane("XY").circle(P.TOWER_FLANGE / 2 * 0.72).workplane(offset=22.0)
                    .circle(P.TOWER_OD / 2).loft())
        t = t.union(box(P.TOWER_FLANGE, P.TOWER_FLANGE, P.TOWER_FLANGE_T).edges("|Z").fillet(8.0))
        t = cut_cyl(t, 30.0, P.TOWER_H + 2, 0, 0, -1)
        t = bearing_seat(t, "6004", 0, 0, 0)
        t = bearing_seat(t, "6004", 0, 0, P.TOWER_H - (B6004[2] + 0.3))
        pts = [(x, y) for x in (-P.TOWER_PATTERN / 2, P.TOWER_PATTERN / 2) for y in (-P.TOWER_PATTERN / 2, P.TOWER_PATTERN / 2)]
        t = through_holes(t, "M6", pts, 0, P.TOWER_FLANGE_T)
        t = t.faces(">Z").edges("%CIRCLE").edges(cq.selectors.RadiusNthSelector(-1)).chamfer(1.5)
        return t
    return build


def spindle_sleeve():
    def build():
        s = cylinder(P.SPINDLE_OD + P.SHAFT_FIT, SLEEVE_L)
        # hex boss at the bottom locks into the crown
        hexb = cq.Workplane("XY").polygon(6, 30.0 / 0.8660254).extrude(8.0)
        s = s.union(hexb)
        s = cut_cyl(s, P.CLEAR["M12"], SLEEVE_L + 2, 0, 0, -1)
        s = s.faces(">Z").edges("%CIRCLE").edges(cq.selectors.RadiusNthSelector(-1)).chamfer(1.0)
        return s
    return build


def fork():
    """Yoke. Local frame: spindle axis at x = 0, axle center at the origin (z = 0), wheel toward -X."""
    crown_z0 = TIRE_R + 11.0                 # 151, clears the tire
    crown_z1 = crown_z0 + P.CROWN_T          # 165
    leg_y = P.CASTER_W / 2 + P.FORK_LEG_GAP  # 60, inner face of each leg
    wx = -P.CASTER_TRAIL
    crown_l = 130.0

    def build():
        f = box(crown_l, 2 * (leg_y + P.FORK_LEG_T), P.CROWN_T, wx + 15.0, 0, crown_z0).edges("|Z").fillet(10.0)
        for sy in (1, -1):
            yc = sy * (leg_y + P.FORK_LEG_T / 2)
            leg = (cq.Workplane("XZ")
                   .polyline([(wx - 36, crown_z0 + 1), (wx + 36, crown_z0 + 1), (wx + 22, 0), (wx - 22, 0)]).close()
                   .extrude(P.FORK_LEG_T / 2, both=True)
                   .translate((0, yc, 0)))
            f = f.union(leg)
            f = f.union(cq.Workplane("XZ").circle(22.0).extrude(P.FORK_LEG_T / 2, both=True).translate((wx, yc, 0)))
            # gusset where the leg meets the crown
            f = f.union(box(60.0, P.FORK_LEG_T + 8.0, 10.0, wx, sy * (leg_y + P.FORK_LEG_T / 2 - 4.0 * sy * 0), crown_z0 - 10.0)
                        .translate((0, 0, 0)))
        # axle bolt
        f = f.cut(cq.Workplane("XZ").circle(P.CLEAR["M8"] / 2).extrude(200, both=True).translate((wx, 0, 0)))
        # spindle: hex pocket for the sleeve boss, M12 bolt hole
        hexp = cq.Workplane("XY").polygon(6, (30.0 + P.NUT_FIT) / 0.8660254).extrude(8.5).translate((0, 0, crown_z1 - 8.0))
        f = f.cut(hexp)
        f = cut_cyl(f, P.CLEAR["M12"], 40, 0, 0, crown_z0 - 1)
        # M12 head pocket under the crown
        f = cut_cyl(f, P.HEAD_D["M12"] + 1.0, 8.0, 0, 0, crown_z0 - 1)
        return f
    return build


def rim():
    od, idd, w = P.CASTER_RIM_D, P.CASTER_RIM_D - 12.0, P.CASTER_W
    boss = 40.0

    def build():
        r = tube(od, idd, w)
        for z in (12.0, w / 2 - 3.0, w - 18.0):
            r = r.union(tube(od + 6.0, od - 2.0, 6.0, 0, 0, z))
        r = r.union(cylinder(boss, w))
        r = cut_cyl(r, 14.5, w + 2, 0, 0, -1)
        r = bearing_seat(r, "608", 0, 0, 0)
        r = bearing_seat(r, "608", 0, 0, w - (B608[2] + 0.3))
        for ang in range(0, 360, 60):
            spoke = box(idd / 2 - boss / 2 + 6.0, 12.0, w - 12.0, (idd / 2 + boss / 2) / 2 - 1.0, 0, 6.0)
            r = r.union(spoke.rotate((0, 0, 0), (0, 0, 1), ang))
        r = r.union(tube(idd + 2.0, boss - 2.0, 3.0, 0, 0, w / 2 - 1.5))
        return r
    return build


def tire():
    od, idd, w = P.CASTER_TIRE_D, P.CASTER_RIM_D - 1.0, P.CASTER_W

    def build():
        t = tube(od, idd, w)
        t = t.edges("%CIRCLE").edges(cq.selectors.RadiusNthSelector(-1)).chamfer(4.0)
        for z in (12.0, w / 2 - 3.0, w - 18.0):
            t = t.cut(tube(P.CASTER_RIM_D + 7.0, idd - 1.0, 6.6, 0, 0, z - 0.3))
        for ang in range(0, 360, 18):
            g = box(8.0, 3.0, w - 20.0, od / 2, 0, 10.0).rotate((0, 0, 0), (0, 0, 1), ang)
            t = t.cut(g)
        return t
    return build


def axle_spacer_inner():
    length = P.CASTER_W - 2 * (B608[2] + 0.3)

    def build():
        return tube(13.5, P.CLEAR["M8"], length)
    return build


def axle_spacer_outer():
    def build():
        return tube(16.0, P.CLEAR["M8"], P.FORK_LEG_GAP - 0.5)
    return build


def parts():
    return [
        Part("caster_spindle_tower", tower(), 2, "PETG",
             "Sits on the boom arm pad, 4x M6 x 50 down into the pad inserts. Press a 6004 bearing into each end.",
             walls=6, infill=50, orientation="flange down"),
        Part("caster_spindle_sleeve", spindle_sleeve(), 2, "PETG",
             "Hex boss drops into the yoke crown. M12 x 180 bolt runs up through it; nylock nut and washer on top of the tower.",
             walls=8, infill=100, orientation="standing, hex down"),
        Part("caster_fork", fork(), 2, "PETG",
             "Yoke with 50 mm trail. Print on its side (one leg on the bed) with supports so layers run along the legs. M8 x 140 axle bolt.",
             walls=6, infill=50, supports=True, orientation="on its side"),
        Part("caster_rim", rim(), 2, "PETG",
             "258 mm rim. Press a 608 bearing into each end with the inner spacer between them.",
             walls=4, infill=25, orientation="flat", tags=("large",)),
        Part("caster_tire", tire(), 2, "TPU 95A",
             "280 x 100 mm. Stretch over the rim ribs. 3 walls, 15 percent gyroid for cushion.",
             walls=3, infill=15, orientation="flat", tags=("large", "tpu")),
        Part("caster_axle_spacer_inner", axle_spacer_inner(), 2, "PETG", "Between the two 608 inner races.", walls=4, infill=100),
        Part("caster_axle_spacer_outer", axle_spacer_outer(), 4, "PETG", "Between each 608 and the fork leg.", walls=4, infill=100),
    ]
