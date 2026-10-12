"""Raised front boom and upper deck: arms, cross member halves, risers, braces, legs, deck quadrants.

Arm local frame: x along the arm from the rear end (global x = BOOM_ARM_X0), y across with +y
outboard, z up from the arm underside (global BOOM_Z). The left arm is modelled; the right arm is
its mirror.
"""
import cadquery as cq

import params as P
from lib.features import (Part, box, cylinder, cut_cyl, insert_holes, through_holes, holes_x, holes_y, cbore_holes, grid)

S, WALL = P.BOOM_SEC, P.BOOM_WALL
ARM_L = P.BOOM_ARM_X1 - P.BOOM_ARM_X0          # 310
PAD_X0 = ARM_L - P.PAD_L                       # 210 local
SPINDLE_LX = P.CASTER_X - P.BOOM_ARM_X0        # 260 local
PAD_CY = P.CASTER_Y - 200.0                    # pad center offset from the arm centerline (+5 outboard)
CROSS_FRONT_LX = P.CROSS_FRONT_X - P.BOOM_ARM_X0   # 260
CROSS_REAR_LX = P.CROSS_REAR_X - P.BOOM_ARM_X0     # 20
ARM_IN_FACE = -S / 2                           # inner face at local y = -20 (global 180)
PAD_IN_FACE = PAD_CY - P.PAD_W / 2             # local y = -45 (global 155)


def box_section(l, s, wall, cx, cy, z0, ribs_every=None):
    b = box(l, s, s, cx, cy, z0).cut(box(l + 2, s - 2 * wall, s - 2 * wall, cx, cy, z0 + wall))
    if ribs_every:
        n = int(l // ribs_every)
        for i in range(1, n):
            b = b.union(box(3.0, s - 2, s - 2 * wall, cx - l / 2 + i * ribs_every, cy, z0 + wall))
    return b


def arm(side):
    """side = +1 left (modelled), -1 right (mirrored about XZ)."""
    def build():
        a = box_section(PAD_X0 + 10.0, S, WALL, (PAD_X0 + 10.0) / 2, 0, 0, ribs_every=50.0)
        # end caps close the tube
        a = a.union(box(WALL, S, S, WALL / 2, 0, 0))
        # tower pad: hollow block with ribs and a spindle boss
        pad = box(P.PAD_L, P.PAD_W, S, PAD_X0 + P.PAD_L / 2, PAD_CY, 0)
        pad = pad.cut(box(P.PAD_L - 2 * WALL, P.PAD_W - 2 * WALL, S - 2 * WALL, PAD_X0 + P.PAD_L / 2, PAD_CY, WALL))
        pad = pad.union(cylinder(P.SPINDLE_HOLE + 16.0, S, SPINDLE_LX, PAD_CY, 0))
        for dx in (-25.0, 25.0):
            pad = pad.union(box(3.0, P.PAD_W - 2, S - 2 * WALL, SPINDLE_LX + dx, PAD_CY, WALL))
        for dy in (-25.0, 25.0):
            pad = pad.union(box(P.PAD_L - 2, 3.0, S - 2 * WALL, PAD_X0 + P.PAD_L / 2, PAD_CY + dy, WALL))
        a = a.union(pad)
        a = cut_cyl(a, P.SPINDLE_HOLE, S + 2, SPINDLE_LX, PAD_CY, -1)
        # tower bolts: M6 inserts in the pad top, with solid bosses underneath
        tpts = [(SPINDLE_LX + dx, PAD_CY + dy) for dx in (-P.TOWER_PATTERN / 2, P.TOWER_PATTERN / 2) for dy in (-P.TOWER_PATTERN / 2, P.TOWER_PATTERN / 2)]
        for (x, y) in tpts:
            a = a.union(cylinder(14.0, S, x, y, 0))
        a = insert_holes(a, "M6", tpts, S, 12.0)
        # cross member bolts through the inner wall: rear at x = 20 local, front at 270 local (into the pad inner wall)
        rear_pts = [(CROSS_REAR_LX - 10, S / 2), (CROSS_REAR_LX + 10, S / 2)]
        front_pts = [(CROSS_FRONT_LX - 10, S / 2), (CROSS_FRONT_LX + 10, S / 2)]
        a = holes_y(a, P.CLEAR["M5"], rear_pts, ARM_IN_FACE - 5, WALL + 10)
        a = holes_y(a, P.CLEAR["M5"], front_pts, PAD_IN_FACE - 5, WALL + 10)
        # 9 mm access bores from the outer wall through to the inner wall (and through the pad ribs) for the driver
        a = holes_y(a, 9.0, rear_pts, ARM_IN_FACE + WALL + 0.5, S)
        a = holes_y(a, 9.0, front_pts, PAD_IN_FACE + WALL + 0.5, P.PAD_W)
        if side < 0:
            a = a.mirror("XZ")
        return a
    return build


def cross_half(front):
    """From the center splice (local x = 0) to the arm inner face (local x = half length)."""
    HL = P.CROSS_FRONT_HALF_L if front else P.CROSS_REAR_HALF_L

    def build():
        c = box_section(HL, S, WALL, HL / 2, 0, 0, ribs_every=45.0)
        c = c.union(box(WALL, S, S, HL - WALL / 2, 0, 0))
        # end plate: M5 inserts into the end face for the arm bolts
        c = c.union(box(12.0, S - 2 * WALL, S - 2 * WALL, HL - 6.0, 0, WALL))
        end = cq.Workplane("YZ").pushPoints([(-10.0, S / 2), (10.0, S / 2)]).circle(P.INSERT["M5"][0] / 2).extrude(-9.0).translate((HL + 0.01, 0, 0))
        c = c.cut(end)
        # Splice: a full-height, half-width solid tab centred on the member's centre (local x = -30..30) on the +y
        # side; the first 30 mm of the body on the -y side is cleared for the other half's tab. The mating half is
        # the same part turned 180 degrees, so the two tabs lap side by side. Two M5 x 45 bolts run across them.
        TL = P.CROSS_TAB_L
        c = c.cut(box(TL / 2 + 0.2, S / 2 + 0.2, S + 2, TL / 4, -S / 4, -1))
        c = c.union(box(TL, S / 2 - 0.2, S, 0, S / 4 + 0.1, 0))
        # deck bolts: M5 inserts in the top face
        top_pts = [(x, 0.0) for x in P.CROSS_INSERTS["front" if front else "rear"]]
        for (x, y) in top_pts:
            c = c.union(cylinder(12.0, S - WALL, x, y, 0))
        rp = []
        if not front:
            # riser bolts up into the underside at y = RISER_Y, along the member's width
            rp = [(P.RISER_Y, dy) for dy in (-P.RISER_TOP_DX, P.RISER_TOP_DX)]
            for (x, y) in rp:
                c = c.union(cylinder(12.0, S - WALL, x, y, WALL))
        # all holes after all unions
        c = holes_y(c, P.CLEAR["M5"], [(-TL / 4, S / 2), (TL / 4, S / 2)], -S / 2 - 1, S + 2)
        c = insert_holes(c, "M5", top_pts, S)
        for (x, y) in rp:   # blind insert holes going UP from the underside
            c = cut_cyl(c, P.INSERT["M5"][0], 10.0, x, y, -1)
        return c
    return build


def riser():
    w, d = P.RISER_SEC
    px, py = P.RISER_PATTERN

    def build():
        r = box(w, d, P.RISER_H).cut(box(w - 2 * WALL, d - 2 * WALL, P.RISER_H - 6.0 - 6.0, 0, 0, 6.0))
        r = r.union(box(px + 12.0, py + 12.0, 6.0))
        foot = [(dx, dy) for dx in (-px / 2, px / 2) for dy in (-py / 2, py / 2)]
        r = through_holes(r, "M5", foot, 0, 6.0)
        r = r.cut(box(w - 2 * WALL, d - 2 * WALL, 8.0, 0, 0, -1))     # open bottom
        r = through_holes(r, "M5", [(-P.RISER_TOP_DX, 0.0), (P.RISER_TOP_DX, 0.0)], P.RISER_H - 6.0, 6.0)
        # brace inserts on the rear face (-x), either side of the brace's gusset plate
        brace = cq.Workplane("YZ").pushPoints([(10.0, 34.0), (-10.0, 74.0)]).circle(P.INSERT["M5"][0] / 2).extrude(9.0).translate((-w / 2 - 0.01, 0, 0))
        r = r.cut(brace)
        return r
    return build


def brace():
    """Triangular gusset in the XZ plane between the chassis lid and the riser rear face."""
    t = 6.0
    riser_face = P.RISER_X - P.RISER_SEC[0] / 2          # 5 (global x of the riser's rear face)
    foot_x0 = P.BRACE_X - 15.0                           # -85
    foot_x1 = riser_face - 12.0                          # stops short of the riser foot flange
    step = 8.0                                           # clears the 6 mm riser foot flange
    h = 110.0

    def build():
        g = (cq.Workplane("XZ").polyline([(foot_x0, 0), (foot_x1, 0), (foot_x1, step), (riser_face, step), (riser_face, h)]).close()
             .extrude(t / 2, both=True))
        g = g.union(box(foot_x1 - foot_x0, 26.0, 6.0, (foot_x0 + foot_x1) / 2, 0, 0))
        g = g.union(box(6.0, 30.0, h - step, riser_face - 3.0, 0, step))
        # bolts sit beside the gusset plate, not under it
        g = through_holes(g, "M5", [(P.BRACE_X - 10, 10.0), (P.BRACE_X + 10, -10.0)], 0, 6.0)
        g = holes_x(g, P.CLEAR["M5"], [(10.0, 34.0), (-10.0, 74.0)], riser_face - 8, 10)
        return g
    return build


def leg():
    w, d = P.LEG_SEC
    px, py = P.LEG_PATTERN
    h = P.DECK_Z0 - P.CH_LID_TOP   # 169

    def build():
        l = box(w, d, h).cut(box(w - 2 * WALL, d - 2 * WALL, h - 12.0, 0, 0, 6.0))
        l = l.union(box(px + 12.0, py + 12.0, 6.0))
        l = through_holes(l, "M5", [(dx, dy) for dx in (-px / 2, px / 2) for dy in (-py / 2, py / 2)], 0, 6.0)
        l = l.cut(box(w - 2 * WALL, d - 2 * WALL, 8.0, 0, 0, -1))
        l = insert_holes(l, "M5", [(-P.LEG_TOP_DX, 0.0), (P.LEG_TOP_DX, 0.0)], h)
        return l
    return build


def deck_quadrant(sx, sy):
    """sx = +1 front, -1 rear; sy = +1 left, -1 right. Local origin at the quadrant's own corner on the seams."""
    seam_x = (P.DECK_X0 + P.DECK_X1) / 2.0     # 15
    ql = (P.DECK_X1 - P.DECK_X0) / 2.0         # 285
    qw = P.DECK_W / 2.0                        # 145
    x0 = seam_x if sx > 0 else seam_x - ql
    y0 = 0.0 if sy > 0 else -qw

    def to_local(gx, gy):
        return (gx - x0 - ql / 2, gy - y0 - qw / 2)

    def build():
        d = box(ql, qw, P.DECK_T)
        rib_h = P.DECK_RIB
        # round the outer corner so it clears the canopy's plan-view corner radius
        r = P.DECK_CORNER_R
        cx_, cy_ = sx * ql / 2, sy * qw / 2
        corner = box(r, r, 60.0, cx_ - sx * r / 2, cy_ - sy * r / 2, -30.0).cut(cylinder(2 * r, 60.0, cx_ - sx * r, cy_ - sy * r, -30.0))
        d = d.cut(corner)
        # edge ribs and two cross ribs underneath (modelled ribs-down; print ribs-up)
        d = d.union(box(ql, 4.0, rib_h, 0, sy * (qw / 2 - 2.0), -rib_h))
        d = d.union(box(4.0, qw, rib_h, sx * (ql / 2 - 2.0), 0, -rib_h))
        for fx in (-ql / 4, ql / 4):
            d = d.union(box(4.0, qw - 8, rib_h, fx, 0, -rib_h))
        d = d.union(box(ql - 8, 4.0, rib_h, 0, 0, -rib_h))
        d = d.cut(corner)
        # notch the ribs where the cross members and the deck legs pass underneath
        for gx in (P.CROSS_REAR_X, P.CROSS_FRONT_X):
            lx, _ = to_local(gx, 0)
            d = d.cut(box(P.BOOM_SEC + 6.0, qw + 2, rib_h + 1, lx, 0, -rib_h - 1))
        lx, ly = to_local(P.LEG_X, sy * P.LEG_Y)
        d = d.cut(box(P.LEG_SEC[0] + 8.0, P.LEG_SEC[1] + 8.0, rib_h + 1, lx, ly, -rib_h - 1))
        # seam lap tabs on the top half of the plate: front quadrants lap over the rear ones, left over right.
        # The receiving quadrant has its top half pocketed along that edge so the joint sits flush.
        # The y-seam tab stops 35 mm short of the x seam so the two tabs never meet.
        if sx > 0:
            d = d.union(box(30.0, qw - 10, P.DECK_T / 2, -ql / 2 - 15.0, 0, P.DECK_T / 2))
        else:
            d = d.cut(box(30.4, qw + 2, P.DECK_T / 2 + 1, ql / 2 - 15.0, 0, P.DECK_T / 2))
        if sy > 0:
            d = d.union(box(ql - 70, 30.0, P.DECK_T / 2, 0, -qw / 2 - 15.0, P.DECK_T / 2))
        else:
            d = d.cut(box(ql - 69.6, 30.4, P.DECK_T / 2 + 1, 0, qw / 2 - 15.0, P.DECK_T / 2))
        seam_pts = [(-sx * (ql / 2 - 7.0), y) for y in (-qw / 3, 0.0, qw / 3)]
        seam_pts += [(x, -sy * (qw / 2 - 7.0)) for x in (-ql / 4, 0.0, ql / 4)]
        d = through_holes(d, "M4", seam_pts, -rib_h - 1, rib_h + P.DECK_T + 2)
        # bolts down into the cross members (x = 40 and 280 global) and legs (x = -240), only where they fall in this quadrant
        anchors = []
        for gx, key in ((P.CROSS_REAR_X, "rear"), (P.CROSS_FRONT_X, "front")):
            for off in P.CROSS_INSERTS[key]:
                anchors.append((gx, sy * off))
        anchors.append((P.LEG_X - P.LEG_TOP_DX, sy * P.LEG_Y))
        anchors.append((P.LEG_X + P.LEG_TOP_DX, sy * P.LEG_Y))
        anchors = [to_local(gx, gy) for (gx, gy) in anchors]
        anchors = [(x, y) for (x, y) in anchors if abs(x) < ql / 2 - 6 and abs(y) < qw / 2 - 6]
        d = cbore_holes(d, "M5", anchors, P.DECK_T, P.DECK_T, 3.0)
        # M4 insert grid on top for the enclosure, mast standoff, and anything else
        gpts = []
        blocked_x = [(P.CROSS_REAR_X - P.BOOM_SEC / 2 - 8, P.CROSS_REAR_X + P.BOOM_SEC / 2 + 8),
                     (P.CROSS_FRONT_X - P.BOOM_SEC / 2 - 8, P.CROSS_FRONT_X + P.BOOM_SEC / 2 + 8)]
        gx = P.DECK_GRID_X0
        while gx < P.DECK_X1:
            gy = P.DECK_GRID_Y0
            while gy < P.DECK_W / 2:
                for s in (1, -1):
                    lx, ly = to_local(gx, s * gy)
                    over_leg = abs(gx - P.LEG_X) < P.LEG_SEC[0] / 2 + 10 and abs(s * gy - sy * P.LEG_Y) < P.LEG_SEC[1] / 2 + 10
                    over_cross = any(a < gx < b for a, b in blocked_x)
                    if (abs(lx) < ql / 2 - 12 and abs(ly) < qw / 2 - 12 and abs(lx - (-sx * (ql / 2 - 7))) > 20
                            and not over_leg and not over_cross):
                        gpts.append((lx, ly))
                gy += P.DECK_GRID
            gx += P.DECK_GRID
        # bosses under each grid point so the insert has 7 mm of material
        for (x, y) in gpts:
            d = d.union(cylinder(10.0, 8.0, x, y, -8.0))
        d = insert_holes(d, "M4", gpts, P.DECK_T)
        return d
    return build


def parts():
    out = [
        Part("boom_arm_left", arm(1), 1, "PETG", "310 mm box section with the tower pad. Print flat, pad up. M6 x 50 tower bolts, M5 x 45 cross member bolts.", walls=5, infill=40, orientation="flat"),
        Part("boom_arm_right", arm(-1), 1, "PETG", "Mirror of the left arm.", walls=5, infill=40, orientation="flat"),
        Part("boom_cross_front_half", cross_half(True), 2, "PETG", "Two halves lap at the center (turn one 180 degrees) with 2x M5 x 45 and nuts across the joint; the end plate bolts to the arm pad with 2x M5 x 16 through the pad wall.", walls=5, infill=40, orientation="flat"),
        Part("boom_cross_rear_half", cross_half(False), 2, "PETG", "Same as the front halves, plus riser inserts underneath.", walls=5, infill=40, orientation="flat"),
        Part("riser_column", riser(), 2, "PETG", "Bolt the risers to the rear cross member first (2x M5 x 20 up through the top plate, from inside the open column), then stand that subassembly on the lid and bolt the feet (4x M5 x 16).", walls=5, infill=40, orientation="foot down"),
        Part("riser_brace", brace(), 2, "PETG", "Gusset from the lid to the riser rear face. Print flat on its side.", walls=4, infill=30, orientation="flat"),
        Part("rear_deck_leg", leg(), 2, "PETG", "Chassis lid to upper deck. Foot: 4x M5 x 16. Deck bolts into the top inserts.", walls=5, infill=40, orientation="foot down"),
    ]
    for sx, sy, nm in ((1, 1, "front_left"), (1, -1, "front_right"), (-1, 1, "rear_left"), (-1, -1, "rear_right")):
        out.append(Part(f"deck_{nm}", deck_quadrant(sx, sy), 1, "PETG",
                        "Ribbed plate. Print ribs up (flip the model). M4 insert grid on 40 mm for mounting.", walls=4, infill=30, orientation="ribs up (flipped)"))
    return out
