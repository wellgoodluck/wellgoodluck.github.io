#!/usr/bin/env python3
"""Write assets/us-map.json: one SVG path per state (50 states and DC), for the state tool's map.

Input: us-atlas 3.0.1's states-albers-10m.json (the Census Bureau's 2017 cartographic state
boundaries, projected with d3.geoAlbersUsa to fit a 975x610 viewport, Alaska and Hawaii inset).
Get it with `npm pack us-atlas@3.0.1` (or from https://cdn.jsdelivr.net/npm/us-atlas@3.0.1/) and
pass its path:

    python3 tools/make_us_map.py path/to/states-albers-10m.json [assets/us-map.json]

Stdlib only. Each shared border is one TopoJSON arc, simplified once (Douglas-Peucker), so
neighbouring states still meet exactly: no slivers or gaps. Run by hand; never by workflows.
State lines don't change, so this should rarely need rerunning.
"""
import json
import math
import sys

TOL = 0.55          # simplification tolerance, in viewport units (the map is drawn at 975 wide)
NDP = 1             # decimals kept in the path data

FIPS = {"01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE",
        "11": "DC", "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA",
        "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
        "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM",
        "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
        "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
        "54": "WV", "55": "WI", "56": "WY"}

LICENSE = ("Shapes: U.S. Census Bureau cartographic state boundaries, 2017 edition, via us-atlas 3.0.1 "
           "(states-albers-10m.json, d3.geoAlbersUsa, 975x610), simplified by tools/make_us_map.py. "
           "us-atlas: Copyright 2013-2019 Michael Bostock. Permission to use, copy, modify, and/or "
           "distribute this software for any purpose with or without fee is hereby granted, provided "
           "that the above copyright notice and this permission notice appear in all copies. THE "
           "SOFTWARE IS PROVIDED \"AS IS\" AND THE AUTHOR DISCLAIMS ALL WARRANTIES (ISC License).")


def decode_arcs(t):
    sx, sy = t["transform"]["scale"]
    tx, ty = t["transform"]["translate"]
    out = []
    for arc in t["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        out.append(pts)
    return out


def dp(pts, tol):
    """Douglas-Peucker, keeping both ends (an arc's ends are where three states meet)."""
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (x1, y1), (x2, y2) = pts[a], pts[b]
        dx, dy = x2 - x1, y2 - y1
        n = math.hypot(dx, dy)
        best, bi = -1.0, -1
        for i in range(a + 1, b):
            px, py = pts[i]
            d = abs(dy * (px - x1) - dx * (py - y1)) / n if n else math.hypot(px - x1, py - y1)
            if d > best:
                best, bi = d, i
        if best > tol:
            keep[bi] = True
            stack.append((a, bi))
            stack.append((bi, b))
    return [p for p, k in zip(pts, keep) if k]


def ring_pts(ring, arcs):
    pts = []
    for i in ring:
        a = arcs[i] if i >= 0 else arcs[~i][::-1]
        pts.extend(a if not pts else a[1:])
    return pts


def area(pts):
    return 0.5 * sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))


def fmt(v):
    s = ("%." + str(NDP) + "f") % v
    return s[:-2] if s.endswith(".0") else s


def path(polys, arcs):
    d = []
    for poly in polys:
        for k, ring in enumerate(poly):
            pts = ring_pts(ring, arcs)
            if len(pts) > 1 and pts[0] == pts[-1]:
                pts = pts[:-1]
            if len(pts) < 3 or (k == 0 and abs(area(pts)) < 0.4):   # drop specks too small to see
                if k == 0:
                    break
                continue
            d.append("M" + "L".join(fmt(x) + "," + fmt(y) for x, y in pts) + "Z")
    return "".join(d)


def main():
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else "assets/us-map.json"
    t = json.load(open(src))
    raw = decode_arcs(t)
    arcs = [dp(a, TOL) for a in raw]
    states, boxes = {}, {}
    for g in t["objects"]["states"]["geometries"]:
        ab = FIPS[g["id"]]
        polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
        states[ab] = path(polys, arcs)
        xs = [x for poly in polys for ring in poly[:1] for x, _ in ring_pts(ring, arcs)]
        ys = [y for poly in polys for ring in poly[:1] for _, y in ring_pts(ring, arcs)]
        boxes[ab] = [round(min(xs), 1), round(min(ys), 1), round(max(xs), 1), round(max(ys), 1)]
    if sorted(states) != sorted(FIPS.values()):
        sys.exit("make_us_map: expected the 50 states and DC, got %d" % len(states))
    out = {"note": LICENSE, "viewBox": [0, 0, 975, 610], "states": dict(sorted(states.items())),
           "boxes": dict(sorted(boxes.items()))}
    with open(dst, "w") as f:
        json.dump(out, f, separators=(",", ":"))
        f.write("\n")
    pts = sum(len(a) for a in arcs)
    print("us-map: %d states, %d of %d points kept (tolerance %s), %s" %
          (len(states), pts, sum(len(a) for a in raw), TOL, dst))


if __name__ == "__main__":
    main()
