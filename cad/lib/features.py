"""Reusable printed-part features for ClaudeBot.

All helpers take and return cq.Workplane objects with a single solid, in the part's own
frame. Parts are modelled in their print orientation unless noted.
"""
from dataclasses import dataclass, field
from typing import Callable, Iterable, Tuple

import cadquery as cq

import params as P


@dataclass
class Part:
    """One printable part and the metadata the export and the print guide need."""
    name: str
    build: Callable[[], cq.Workplane]
    qty: int = 1
    material: str = "PETG"
    notes: str = ""
    walls: int = 4
    infill: int = 25
    supports: bool = False
    orientation: str = "as modelled (Z up)"
    tags: Tuple[str, ...] = field(default_factory=tuple)


XY = lambda: cq.Workplane("XY")  # noqa: E731


def box(l, w, h, cx=0.0, cy=0.0, z0=0.0):
    """Box with its bottom face at z0, centered on (cx, cy)."""
    return XY().box(l, w, h, centered=(True, True, False)).translate((cx, cy, z0))


def cylinder(d, h, cx=0.0, cy=0.0, z0=0.0):
    return XY().circle(d / 2.0).extrude(h).translate((cx, cy, z0))


def tube(od, bore, h, cx=0.0, cy=0.0, z0=0.0):
    return XY().circle(od / 2.0).circle(bore / 2.0).extrude(h).translate((cx, cy, z0))


def rounded_box(l, w, h, r, cx=0.0, cy=0.0, z0=0.0):
    """Box with rounded vertical edges."""
    return XY().rect(l, w).extrude(h).edges("|Z").fillet(r).translate((cx, cy, z0))


def grid(nx, ny, px, py, cx=0.0, cy=0.0):
    """Hole centers for an nx by ny pattern with pitch px, py, centered on (cx, cy)."""
    xs = [cx + (i - (nx - 1) / 2.0) * px for i in range(nx)]
    ys = [cy + (j - (ny - 1) / 2.0) * py for j in range(ny)]
    return [(x, y) for x in xs for y in ys]


def square_pattern(s, cx=0.0, cy=0.0):
    return grid(2, 2, s, s, cx, cy)


def cut_cyl(solid, d, h, cx, cy, z0):
    return solid.cut(cylinder(d, h, cx, cy, z0))


def cyl_x(d, length, x0, y, z):
    """Cylinder along +X starting at x0."""
    return cq.Workplane("YZ").circle(d / 2.0).extrude(length).translate((x0, y, z))


def cyl_y(d, length, x, y0, z):
    """Cylinder along +Y starting at y0."""
    return cq.Workplane("XZ").circle(d / 2.0).extrude(-length).translate((x, y0, z))


def holes_x(solid, d, yz_points, x0, length):
    for (y, z) in yz_points:
        solid = solid.cut(cyl_x(d, length, x0, y, z))
    return solid


def holes_y(solid, d, xz_points, y0, length):
    for (x, z) in xz_points:
        solid = solid.cut(cyl_y(d, length, x, y0, z))
    return solid


def insert_holes(solid, size, points, z_top, depth=None, extra=2.0):
    """Blind heat-set insert holes going down from the face at z_top."""
    d, dd = P.INSERT[size]
    depth = depth or dd
    for (x, y) in points:
        solid = cut_cyl(solid, d, depth + extra, x, y, z_top - depth)
        # small lead-in chamfer substitute: a slightly wider mouth
        solid = cut_cyl(solid, d + 0.6, 0.8, x, y, z_top - 0.8)
    return solid


def through_holes(solid, size, points, z0, h):
    d = P.CLEAR[size]
    for (x, y) in points:
        solid = cut_cyl(solid, d, h + 2, x, y, z0 - 1)
    return solid


def cbore_holes(solid, size, points, z_top, depth, cbore_depth=None):
    """Clearance hole with a counterbore for a socket cap head, from the face at z_top."""
    cb = cbore_depth or (P.HEAD_D[size] * 0.9)
    for (x, y) in points:
        solid = cut_cyl(solid, P.CLEAR[size], depth + 2, x, y, z_top - depth - 1)
        solid = cut_cyl(solid, P.HEAD_D[size] + 0.6, cb + 1, x, y, z_top - cb)
    return solid


def nut_pockets(solid, size, points, z0, depth=None):
    """Hex nut pocket opening at z0 upward."""
    af = P.NUT_AF[size] + P.NUT_FIT
    depth = depth or (P.NUT_T[size] + 0.6)
    for (x, y) in points:
        hexagon = XY().polygon(6, af / 0.8660254).extrude(depth + 1).translate((x, y, z0 - 1))
        solid = solid.cut(hexagon)
    return solid


def bearing_seat(solid, bearing, cx, cy, z0, depth=None, through_bore=None):
    """Press-fit pocket for a bearing, opening at z0 upward; optional through bore below."""
    bore, od, w = P.BEARING[bearing]
    depth = depth or (w + 0.3)
    solid = cut_cyl(solid, od + P.BEARING_SEAT_FIT, depth + 1, cx, cy, z0 - 1)
    if through_bore:
        solid = cut_cyl(solid, through_bore, 500, cx, cy, z0 - 250)
    return solid


def dowel_holes(solid, points, z0, h, fit=P.DOWEL_FIT):
    for (x, y) in points:
        solid = cut_cyl(solid, P.DOWEL_D + fit, h + 1, x, y, z0 - 0.5)
    return solid


def ribs_x(solid, l, w, h, t, ys, cx=0.0, z0=0.0):
    """Ribs running along X at the given Y positions."""
    for y in ys:
        solid = solid.union(box(l, t, h, cx, y, z0))
    return solid


def ribs_y(solid, l, w, h, t, xs, cy=0.0, z0=0.0):
    for x in xs:
        solid = solid.union(box(t, w, h, x, cy, z0))
    return solid


def tray(l, w, h, wall, floor, cx=0.0, cy=0.0, z0=0.0, r=4.0):
    """Open-top box with rounded outer vertical edges."""
    outer = rounded_box(l, w, h, r, cx, cy, z0)
    inner = box(l - 2 * wall, w - 2 * wall, h, cx, cy, z0 + floor)
    return outer.cut(inner)


def hollow_rounded(l, w, h, r, wall, cx=0.0, cy=0.0, z0=0.0, top_r=None):
    """Rounded box shelled from the bottom (open underneath)."""
    outer = rounded_box(l, w, h, r, cx, cy, z0)
    inner = rounded_box(l - 2 * wall, w - 2 * wall, h - wall + 1, max(r - wall, 1.0), cx, cy, z0 - 1)
    if top_r:
        outer = outer.faces(">Z").edges().fillet(top_r)
        inner = inner.faces(">Z").edges().fillet(max(top_r - wall, 1.0))
    return outer.cut(inner)


def slot(solid, l, w, cx, cy, z0, h):
    s = XY().slot2D(l, w).extrude(h + 2).translate((cx, cy, z0 - 1))
    return solid.cut(s)


def polar(n, r, start_deg=0.0):
    import math
    return [(r * math.cos(math.radians(start_deg + i * 360.0 / n)), r * math.sin(math.radians(start_deg + i * 360.0 / n))) for i in range(n)]


def bbox(solid):
    bb = solid.val().BoundingBox()
    return (bb.xlen, bb.ylen, bb.zlen)


def fits_build(solid, dual=False):
    """True if the part fits the printer in some axis permutation."""
    vol = P.BUILD_DUAL if dual else P.BUILD_SINGLE
    dims = sorted(bbox(solid), reverse=True)
    limits = sorted(vol, reverse=True)
    return all(d <= lim for d, lim in zip(dims, limits))
