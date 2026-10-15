#!/usr/bin/env python3
"""Generate a geographically accurate Bangladesh map for the coverage section.

Reads tools/data/BGD.geo.json (geoBoundaries ADM0, CC-BY 4.0), simplifies the
rings with Ramer-Douglas-Peucker, projects them (equirectangular, cos-lat
corrected) into the 400x560 viewBox, positions city markers from real
lat/lon, splices the resulting SVG into index.html, and renders
tools/data/map-preview.png for visual verification.
"""

import json
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "tools" / "data" / "BGD.geo.json"
PREVIEW = ROOT / "tools" / "data" / "map-preview.png"
HTML = ROOT / "index.html"

VB_W, VB_H = 400, 560
PAD = 26
RDP_EPS = 0.012          # degrees — keeps shape, drops noise
MIN_POLY_PX2 = 10        # drop islands smaller than this after scaling

CITIES_MAJOR = [
    # name, lat, lon, label anchor side
    ("Dhaka", 23.8103, 90.4125, "start"),
    ("Chattogram", 22.3569, 91.7832, "start"),
    ("Khulna", 22.8170, 89.5600, "end"),
    ("Sylhet", 24.8949, 91.8687, "start"),
    ("Rajshahi", 24.3745, 88.6042, "end"),
    ("Rangpur", 25.7439, 89.2752, "start"),
    ("Barishal", 22.7010, 90.3535, "start"),
    ("Mymensingh", 24.7471, 90.4110, "start"),
]
CITIES_MINOR = [
    ("Gazipur", 23.9987, 90.4167),
    ("Narayanganj", 23.6225, 90.4990),
    ("Faridpur", 23.5975, 89.8425),
    ("Jashore", 23.1634, 89.2182),
    ("Kushtia", 23.9013, 89.1206),
    ("Bogura", 24.8481, 89.3730),
    ("Cumilla", 23.4579, 91.1871),
    ("Noakhali", 22.8720, 91.1020),
    ("Feni", 23.0190, 91.3960),
]


def rdp(points, eps):
    """Iterative Ramer-Douglas-Peucker line simplification."""
    if len(points) < 3:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        x1, y1 = points[i]
        x2, y2 = points[j]
        dx, dy = x2 - x1, y2 - y1
        norm = math.hypot(dx, dy) or 1e-12
        dmax, idx = 0.0, i
        for k in range(i + 1, j):
            x0, y0 = points[k]
            d = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / norm
            if d > dmax:
                dmax, idx = d, k
        if dmax > eps:
            keep[idx] = True
            stack.append((i, idx))
            stack.append((idx, j))
    return [p for p, k in zip(points, keep) if k]


def shoelace(pts):
    s = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


def main():
    data = json.loads(GEO.read_text())
    geom = data["features"][0]["geometry"]
    raw_polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    rings = [[tuple(pt) for pt in poly[0]] for poly in raw_polys]

    # --- projection constants from the data bbox ---
    all_pts = [p for r in rings for p in r]
    minlon = min(p[0] for p in all_pts)
    maxlon = max(p[0] for p in all_pts)
    minlat = min(p[1] for p in all_pts)
    maxlat = max(p[1] for p in all_pts)
    kx = math.cos(math.radians((minlat + maxlat) / 2))
    span_x = (maxlon - minlon) * kx
    span_y = (maxlat - minlat)
    scale = min((VB_W - 2 * PAD) / span_x, (VB_H - 2 * PAD) / span_y)
    off_x = (VB_W - span_x * scale) / 2
    off_y = (VB_H - span_y * scale) / 2

    def project(lon, lat):
        x = off_x + (lon - minlon) * kx * scale
        y = off_y + (maxlat - lat) * scale
        return (x, y)

    # --- simplify + project, keep significant polygons only ---
    projected = []
    for ring in rings:
        if ring[0] == ring[-1]:
            ring = ring[:-1]
        simp = rdp(ring, RDP_EPS)
        proj = [project(lon, lat) for lon, lat in simp]
        if len(proj) >= 3 and shoelace(proj) >= MIN_POLY_PX2:
            projected.append(proj)
    projected.sort(key=shoelace, reverse=True)
    projected = projected[:8]

    total_pts = sum(len(p) for p in projected)

    def f(v):
        return f"{v:.1f}"

    def to_path(proj):
        d = "M " + " L ".join(f"{f(x)} {f(y)}" for x, y in proj) + " Z"
        return d

    land_paths = "\n                ".join(
        f'<path class="bd-map__land" d="{to_path(p)}"/>' for p in projected
    )

    # --- markers ---
    markers = []
    for name, lat, lon, side in CITIES_MAJOR:
        x, y = project(lon, lat)
        anchor = "end" if side == "end" else "start"
        dx = -11 if side == "end" else 11
        ring = '<circle class="mk__ring" r="10"/>' if name == "Dhaka" else ""
        r = 5.5 if name == "Dhaka" else 4.8
        title = "Dhaka — Head office" if name == "Dhaka" else name
        markers.append(
            f'<g class="mk mk--major" transform="translate({f(x)} {f(y)})">'
            f'<circle r="{r}"/>{ring}'
            f'<text x="{dx}" y="4" text-anchor="{anchor}">{name}</text>'
            f"<title>{title}</title></g>"
        )
    for name, lat, lon in CITIES_MINOR:
        x, y = project(lon, lat)
        markers.append(
            f'<g class="mk" transform="translate({f(x)} {f(y)})">'
            f'<circle r="3.4"><title>{name}</title></circle></g>'
        )
    marker_block = "\n              ".join(markers)

    svg = (
        '<svg class="bd-map" viewBox="0 0 400 560" role="img" '
        'aria-label="Map of Bangladesh showing UCCL operational locations">\n'
        '            <defs>\n'
        '              <linearGradient id="mapFill" x1="0" y1="0" x2="0" y2="1">\n'
        '                <stop offset="0" stop-color="#3A3436"/>\n'
        '                <stop offset="1" stop-color="#201C1E"/>\n'
        "              </linearGradient>\n"
        "            </defs>\n"
        f"            {land_paths}\n"
        '            <g class="bd-map__markers">\n'
        f"              {marker_block}\n"
        "            </g>\n"
        "          </svg>"
    )

    html = HTML.read_text()
    new_html, n = re.subn(r'<svg class="bd-map"[\s\S]*?</svg>', svg, html, count=1)
    if n != 1:
        raise SystemExit("ERROR: bd-map svg block not found in index.html")
    HTML.write_text(new_html)

    # --- preview render for visual verification ---
    S = 2
    img = Image.new("RGB", (VB_W * S, VB_H * S), (255, 255, 255))
    dr = ImageDraw.Draw(img)
    for proj in projected:
        pts = [(x * S, y * S) for x, y in proj]
        dr.polygon(pts, fill=(44, 39, 41))
        dr.line(pts + [pts[0]], fill=(225, 37, 27), width=3)
    for name, lat, lon, side in CITIES_MAJOR:
        x, y = project(lon, lat)
        dr.ellipse([x * S - 6, y * S - 6, x * S + 6, y * S + 6], fill=(225, 37, 27))
    for name, lat, lon in CITIES_MINOR:
        x, y = project(lon, lat)
        dr.ellipse([x * S - 4, y * S - 4, x * S + 4, y * S + 4], fill=(255, 128, 120))
    img.save(PREVIEW)

    print(f"polygons: {len(projected)}, total points after simplify: {total_pts}")
    print(f"scale {scale:.1f}px/deg-equiv, off=({off_x:.1f},{off_y:.1f})")
    print(f"spliced SVG into {HTML.name}; preview at {PREVIEW}")
    dx_, dy_ = project(90.4125, 23.8103)
    print(f"Dhaka marker lands at ({dx_:.1f}, {dy_:.1f}) — expect near centre")


if __name__ == "__main__":
    main()
