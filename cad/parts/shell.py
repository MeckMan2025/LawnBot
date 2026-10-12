"""Body shell: lower skirt panels, canopy quadrants, fenders, bumper, depth camera mount.

Skirts close the gap between the chassis lid and the canopy. The canopy is one rounded hollow
shape over the upper deck, split into four quadrants that fit the printer and bolt back together
with internal tabs.
"""
import math

import cadquery as cq

import params as P
from lib.features import (Part, box, cylinder, cut_cyl, insert_holes, through_holes, holes_x, holes_y,
                          rounded_box, hollow_rounded, cbore_holes, cyl_y)

SK_H = P.SKIRT_Z1 - P.SKIRT_Z0        # 134
SK_T = P.SKIRT_T
CAN_L = P.CANOPY_X1 - P.CANOPY_X0     # 620
CAN_CX = (P.CANOPY_X1 + P.CANOPY_X0) / 2   # 25
CAN_H = P.CANOPY_Z1 - P.CANOPY_Z0     # 140
SPLICE_Y_HOLES = (-210.0, -100.0, 10.0, 40.0, 150.0, 260.0)
SPLICE_WALL_Z = (60.0, 120.0)
FENDER_FLANGE_PTS = [(P.AXLE_X + 154.0 * math.cos(math.radians(a)), P.AXLE_Z + 154.0 * math.sin(math.radians(a))) for a in P.FENDER_FLANGE_ANGLES]
# Side skirt panels: (global centre x, length). Shortened by one panel thickness at each outer end so
# they tuck inside the rear and front panels.
SIDE_PANELS = {"rear": ((P.CH_REAR + SK_T + P.CH_REAR + P.MOD_L) / 2, P.MOD_L - SK_T),
               "front": ((P.CH_REAR + P.MOD_L + P.CH_FRONT - SK_T) / 2, P.MOD_L - SK_T)}
TAB_INSET = 25.0
END_TAB_XS = (-45.0, 45.0)       # end panel top tabs sit near the centre, clear of the riser and leg feet
SKIRT_TAB_Z = P.SKIRT_Z0 + SK_H - 10.0     # global z of the canopy screw into each skirt tab


def side_tab_xs():
    """Global x of every side-skirt top tab (both sides share them)."""
    out = []
    for cx, ln in SIDE_PANELS.values():
        out += [cx - ln / 2 + TAB_INSET, cx + ln / 2 - TAB_INSET]
    return out


def skirt(length, holes_x_local, fender_pts=None, wire_hole=None, flange_gaps=(), end_notch=0.0, tab_xs=None):
    """Flat panel, length along X, SK_H tall, with a bottom flange to the lid and top tabs for the canopy.

    flange_gaps: (x0, x1) ranges where the bottom flange is left out (riser and leg feet).
    end_notch: trim the flange by this much at both ends so it clears the neighbouring panel.
    """
    def build():
        s = box(length, SK_T, SK_H)
        # bottom flange, inward (+y), bolts down into the lid edge inserts
        s = s.union(box(length, 15.0, 4.0, 0, 7.5 + SK_T / 2 - SK_T / 2, 0))
        for (x0, x1) in flange_gaps:
            s = s.cut(box(x1 - x0, 16.0, 5.0, (x0 + x1) / 2, SK_T / 2 + 8.0, -0.5))
        if end_notch:
            for sx in (1, -1):
                s = s.cut(box(end_notch, 16.0, 5.0, sx * (length / 2 - end_notch / 2), SK_T / 2 + 8.0, -0.5))
        s = through_holes(s, "M4", [(x, 9.0) for x in holes_x_local], 0, 4.0)
        # top tabs with M4 inserts for the canopy skirt screws (horizontal, from outside)
        for x in (tab_xs or (-length / 2 + TAB_INSET, length / 2 - TAB_INSET)):
            s = s.union(box(20.0, 10.0, 24.0, x, 5.0 + SK_T / 2, SK_H - 24.0))
            s = s.cut(cq.Workplane("XZ").circle(P.INSERT["M4"][0] / 2).extrude(-9.0).translate((x, -SK_T / 2 - 0.01, SK_H - 10.0)))
        # stiffening ribs on the inside, kept clear of the flange bolts
        for x in (-length / 4, length / 4):
            s = s.union(box(4.0, 6.0, SK_H - 30.0, x, SK_T / 2 + 3.0, 4.0))
        if fender_pts:
            for (x, z) in fender_pts:
                s = s.union(cyl_y(12.0, 8.0, x, SK_T / 2 - 0.5, z))
                s = s.cut(cyl_y(P.INSERT["M4"][0], 11.0, x, -SK_T / 2 - 0.01, z))
        if wire_hole:
            s = s.cut(cyl_y(20.0, 40.0, wire_hole[0], -20.0, wire_hole[1]))
        return s
    return build


def fender():
    r_out, r_in, w = P.FENDER_R, P.FENDER_R - 4.0, P.FENDER_W
    a0, a1 = 25.0, 155.0

    def sector(ri, ro, b0, b1, depth):
        c, s = math.cos, math.sin
        r0, r1 = math.radians(b0), math.radians(b1)
        return (cq.Workplane("XZ").moveTo(ri * c(r0), ri * s(r0)).lineTo(ro * c(r0), ro * s(r0))
                .threePointArc((0, ro), (ro * c(r1), ro * s(r1))).lineTo(ri * c(r1), ri * s(r1))
                .threePointArc((0, ri), (ri * c(r0), ri * s(r0))).close().extrude(-depth))   # toward +y

    def build():
        f = sector(r_in, r_out, a0, a1, w)
        # inner flange plate: ring sector r 140..168, 4 thick, at the inner edge (sits on the canopy wall)
        f = f.union(sector(140.0, r_out, 60.0, 120.0, 4.0))
        pts = [(154.0 * math.cos(math.radians(a)), 154.0 * math.sin(math.radians(a))) for a in P.FENDER_FLANGE_ANGLES]
        f = holes_y(f, P.CLEAR["M4"], pts, -1, 6)
        # drip lip on the outer edge
        f = f.union(sector(r_in - 6.0, r_in, a0, a1, 3.0).translate((0, w - 3.0, 0)))
        return f
    return build


def canopy_full():
    c = hollow_rounded(CAN_L, P.CANOPY_W, CAN_H, P.CANOPY_R, P.CANOPY_WALL, CAN_CX, 0, 0, top_r=12.0)
    # notches in both side walls for the two cross members
    for gx in (P.CROSS_REAR_X, P.CROSS_FRONT_X):
        c = c.cut(box(P.BOOM_SEC + 6.0, P.CANOPY_W + 2, P.BOOM_TOP - P.CANOPY_Z0 + 2.0, gx, 0, -1))
    # roof openings: mast, E-stop, charge port
    c = cut_cyl(c, P.MAST_OD + 1.5, 30, P.MAST_X, 0, CAN_H - 10)
    c = through_holes(c, "M5", [(P.MAST_X + dx, dy) for dx in (-40, 40) for dy in (-20, 20)], CAN_H - 8, 10)
    c = cut_cyl(c, 22.5, 30, P.CANOPY_X0 + 45.0, P.ESTOP_Y, CAN_H - 10)
    c = c.cut(box(32.0, 40.0, 30, P.CANOPY_X0 + 45.0, -P.ESTOP_Y, CAN_H - 10))
    # rear face: light bar mount holes; front face: depth camera and bumper carrier holes
    c = holes_x(c, P.CLEAR["M3"], [(y, CAN_H - 30.0) for y in (-80.0, 80.0)], P.CANOPY_X0 - 2, 10)
    c = holes_x(c, P.CLEAR["M4"], [(y, CAN_H - 40.0) for y in (-40.0, 40.0)], P.CANOPY_X1 - 8, 10)
    c = holes_x(c, P.CLEAR["M5"], [(y, P.BUMPER_Z - P.CANOPY_Z0) for y in (-100.0, 100.0)], P.CANOPY_X1 - 8, 10)
    # bottom edge: screws into the skirt top tabs (both sides), at the tab insert height
    tz = SKIRT_TAB_Z - P.CANOPY_Z0
    c = holes_y(c, P.CLEAR["M4"], [(x, tz) for x in side_tab_xs()], -P.CANOPY_W / 2 - 2, 10)
    c = holes_y(c, P.CLEAR["M4"], [(x, tz) for x in side_tab_xs()], P.CANOPY_W / 2 - 8, 10)
    # fender bolts pass through the side walls into the skirt bosses behind
    fpts = [(x, z - P.CANOPY_Z0) for (x, z) in FENDER_FLANGE_PTS]
    c = holes_y(c, P.CLEAR["M4"], fpts, -P.CANOPY_W / 2 - 2, 10)
    c = holes_y(c, P.CLEAR["M4"], fpts, P.CANOPY_W / 2 - 8, 10)
    # ahead of the chassis the bottom band comes off so the caster yoke crowns can sweep underneath
    c = c.cut(box(P.CANOPY_X1 - P.CANOPY_FRONT_CUT_X + 10, P.CANOPY_W + 10, P.CANOPY_FRONT_CUT_Z - P.CANOPY_Z0 + 1,
                  (P.CANOPY_X1 + P.CANOPY_FRONT_CUT_X) / 2 + 5, 0, -1))
    return c


def canopy_quadrant(sx, sy):
    seam_x = CAN_CX
    ql, qw = CAN_L / 2, P.CANOPY_W / 2

    def build():
        c = canopy_full()
        region = box(ql + 1, qw + 1, CAN_H + 2, seam_x + sx * (ql + 1) / 2, sy * (qw + 1) / 2, -1)
        q = c.intersect(region)
        # Seam screw holes (M3). Separate splice strips (canopy_splice_*) bridge the seams on the inside.
        # Roof, x seam: strip along Y with holes either side of the y seam.
        xpts = [(seam_x, y) for y in (-75.0, -30.0, 30.0, 75.0)]
        # Roof, y seam: two 250 mm strips centred at x = -100 and 150.
        ypts = [(x, 0.0) for x in SPLICE_Y_HOLES]
        q = through_holes(q, "M3", xpts + ypts, CAN_H - 8, 10)
        # Walls: x seam through both side walls; y seam through the front and rear faces.
        q = holes_y(q, P.CLEAR["M3"], [(seam_x, z) for z in SPLICE_WALL_Z], -qw - 1, 2 * qw + 2)
        q = holes_x(q, P.CLEAR["M3"], [(0.0, z) for z in SPLICE_WALL_Z], CAN_CX - ql - 1, 2 * ql + 2)
        # bring the quadrant to its own origin for printing
        q = q.translate((-(seam_x + sx * ql / 2), -sy * qw / 2, 0))
        return q
    return build


def splice(length, hole_offsets):
    """Flat 30 x 3 strip with M3 inserts; bridges a canopy seam from the inside."""
    def build():
        s = box(length, 30.0, 3.0)
        s = s.union(box(length, 30.0, 4.0, 0, 0, 3.0).cut(box(length + 2, 22.0, 6.0, 0, 0, 3.0)))
        return insert_holes(s, "M3", [(x, 0.0) for x in hole_offsets], 7.0, 6.0)
    return build


def bumper_carrier():
    w, d, h = P.BUMPER_W, 24.0, 60.0

    def build():
        b = box(w, d, h).edges("|Y").fillet(6.0)
        # two ears on the back (-y) that sit against the canopy nose and slide on M5 shoulder bolts (6 mm shoulder)
        for x in (-100.0, 100.0):
            b = b.union(box(30.0, 20.0, 30.0, x, -d / 2 - 10.0, 15.0))
            b = b.cut(cyl_y(6.3, 40.0, x, -d / 2 - 25.0, 30.0))
            # microswitch pocket in the ear's rear face, lever toward the canopy
            b = b.cut(box(20.5, 7.0, 10.5, x, -d / 2 - 20.0 + 3.5, 5.0))
        # spring pockets (10 mm springs) in the bar's rear face, between the ears
        for x in (-50.0, 50.0):
            b = b.cut(cyl_y(10.6, 12.0, x, -d / 2 - 0.5, 30.0))
        # front grooves for the TPU skin lips (the skin sits 4 mm lower than the bar so its channel floor clears)
        b = b.cut(box(w + 2, 4.0, 4.0, 0, d / 2 - 2.0, 4.0))
        b = b.cut(box(w + 2, 4.0, 4.0, 0, d / 2 - 2.0, 44.0))
        return b
    return build


def bumper_skin():
    w = P.BUMPER_W + 4.0

    def build():
        s = box(w, 14.0, 70.0).edges("|X").fillet(6.0)
        s = s.cut(box(w + 2, 8.0, 62.0, 0, -3.0, 4.0))          # channel open to the rear (-y)
        # lips on the inside of the front wall drop into the carrier's grooves
        s = s.union(box(w - 4.0, 4.0, 3.8, 0, -0.5, 8.1))
        s = s.union(box(w - 4.0, 4.0, 3.8, 0, -0.5, 48.1))
        return s
    return build


def oak_mount():
    tilt = P.OAK_TILT_DEG

    def build():
        base = box(120.0, 12.0, 60.0)
        wedge = (cq.Workplane("YZ").polyline([(0, 0), (12.0 + 60.0 * math.tan(math.radians(tilt)), 0), (12.0, 60.0), (0, 60.0)])
                 .close().extrude(60.0, both=True))
        m = base.union(wedge)
        # camera face: 1/4-20 clearance and two M4 slots; back: two M4 holes into the canopy nose
        m = m.cut(cq.Workplane("XZ").circle(3.4).extrude(60, both=True).translate((0, 0, 30.0)))
        for x in (-40.0, 40.0):
            m = m.cut(cq.Workplane("XZ").slot2D(12.0, P.CLEAR["M4"], 90).extrude(60, both=True).translate((x, 0, 30.0)))
        m = m.cut(box(70.0, 30.0, 70.0, 0, -10.0, -5.0).translate((0, 0, 0)).cut(box(200, 200, 200, 0, 0, -200)))
        return m
    return build


def oak_hood():
    def build():
        h = box(136.0, 50.0, 6.0)
        for sx in (1, -1):
            h = h.union(box(6.0, 50.0, 30.0, sx * 65.0, 0, -30.0))
        h = through_holes(h, "M4", [(-40.0, -15.0), (40.0, -15.0)], 0, 6.0)
        return h
    return build


def parts():
    out = []
    # skirts: rear (300 wide), front (300 wide, between the risers), and two halves per side (175)
    from parts.chassis import END_SKIRT_HOLES, SIDE_SKIRT_HOLES
    # end panels: the lid holes run along y; in the panel's own frame that is its x axis (mirrored for the rear)
    # The rear panel's local +x is global -y (it is rotated -90), the front panel's local +x is global +y.
    rw, rd = P.RISER_PATTERN[1] + 20.0, P.LEG_PATTERN[1] + 20.0
    riser_gaps = [(-s * P.RISER_Y - rw / 2 - 3, -s * P.RISER_Y + rw / 2 + 3) for s in (1, -1)]
    out.append(Part("skirt_rear", skirt(P.CH_W, [-y for y in END_SKIRT_HOLES], end_notch=SK_T + 1.0, tab_xs=END_TAB_XS), 1, "PETG", "Bolts to the rear lid edge inserts (3x M4). Canopy screws into the top tabs.", walls=3, infill=20, orientation="flat on its back"))
    out.append(Part("skirt_front", skirt(P.CH_W, list(END_SKIRT_HOLES), wire_hole=(30.0, 60.0), flange_gaps=riser_gaps, end_notch=SK_T + 1.0, tab_xs=END_TAB_XS), 1, "PETG", "Between the risers; the bottom flange is gapped around the riser feet. Wire hole for the bumper loom.", walls=3, infill=20, orientation="flat on its back"))
    for key, lid_cx in (("rear", P.CH_REAR + P.MOD_L / 2), ("front", P.CH_FRONT - P.MOD_L / 2)):
        cx, ln = SIDE_PANELS[key]
        holes = [lid_cx + hx - cx for hx in SIDE_SKIRT_HOLES]
        fpts = [(x - cx, z - P.SKIRT_Z0) for (x, z) in FENDER_FLANGE_PTS if abs(x - cx) < ln / 2 - 8]
        # the left panel is rotated 180 in the assembly, so its local x runs opposite to global x; the gaps are
        # symmetric about the panel centre on both sides only if we gap both the riser and the leg on every panel
        gaps = []
        for gx, gw in ((P.RISER_X, P.RISER_PATTERN[0] + 20.0), (P.LEG_X, P.LEG_PATTERN[0] + 20.0)):
            if abs(gx - cx) < ln / 2:
                gaps.append((gx - cx - gw / 2 - 3, gx - cx + gw / 2 + 3))
                gaps.append((-(gx - cx) - gw / 2 - 3, -(gx - cx) + gw / 2 + 3))
        out.append(Part(f"skirt_side_{key}", skirt(ln, holes, fender_pts=fpts, flange_gaps=gaps, end_notch=16.0), 2, "PETG",
                        "One per side; mirror for the right side in the slicer. Fender bolts pass through the canopy into the bosses.", walls=3, infill=20, orientation="flat on its back"))
    out.append(Part("fender", fender(), 2, "PETG", "Half round over each drive wheel. 3x M4 into the skirt bosses. Print on its side (flange down).", walls=3, infill=20, orientation="on its side", tags=("large",)))
    for sx, sy, nm in ((1, 1, "front_left"), (1, -1, "front_right"), (-1, 1, "rear_left"), (-1, -1, "rear_right")):
        out.append(Part(f"canopy_{nm}", canopy_quadrant(sx, sy), 1, "PETG", "Print upside down (roof on the bed). Join with M3 x 10 screws through the seam tabs.", walls=3, infill=15, orientation="upside down", tags=("large",)))
    out.append(Part("canopy_splice_wall", splice(120.0, (-25.0, 25.0)), 4, "PETG", "Inside the canopy across each wall seam, M3 x 8 screws from outside.", walls=3, infill=100, orientation="flat"))
    out.append(Part("canopy_splice_roof_x", splice(180.0, (-75.0, -30.0, 30.0, 75.0)), 1, "PETG", "Inside the roof across the front/rear seam.", walls=3, infill=100, orientation="flat"))
    out.append(Part("canopy_splice_roof_y", splice(250.0, (-110.0, 0.0, 110.0)), 2, "PETG", "Inside the roof along the left/right seam; one behind the mast, one ahead.", walls=3, infill=100, orientation="flat"))
    out.append(Part("bumper_carrier", bumper_carrier(), 1, "PETG", "Slides on two M5 x 30 shoulder bolts in the canopy nose with 10 mm springs. Two subminiature microswitches.", walls=4, infill=30))
    out.append(Part("bumper_skin", bumper_skin(), 1, "TPU 95A", "Clips over the carrier's front lips.", walls=3, infill=20, orientation="on its back", tags=("tpu",)))
    out.append(Part("oak_mount", oak_mount(), 1, "PETG", "10 degree down wedge. Camera on the 1/4-20 and M4 slots; 2x M4 into the canopy nose.", walls=4, infill=40))
    out.append(Part("oak_hood", oak_hood(), 1, "PETG", "Rain hood over the depth camera, 2x M4.", walls=3, infill=20, orientation="upside down"))
    return out
