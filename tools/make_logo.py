#!/usr/bin/env python3
"""Render the UCCL brand mark into PNG assets.

Draws the charcoal abstract form + red crescent at 4x scale, then downsamples
with LANCZOS for smooth edges. Outputs:
  assets/img/logo-mark.png        (charcoal + red, transparent — for light bg)
  assets/img/logo-mark-white.png  (white + red, transparent — for dark bg)
  assets/img/favicon.png          (padded square, light variant)

If the official logo PNGs are later dropped into assets/img/ under the same
file names, the site picks them up with no code changes.
"""

from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "assets" / "img"
OUT.mkdir(parents=True, exist_ok=True)

S = 4                      # supersample factor
W = H = 512                # final canvas
CHARCOAL = (34, 31, 33, 255)
RED = (225, 37, 27, 255)
WHITE = (255, 255, 255, 255)


def qbez(p0, p1, p2, n=40):
    """Sample a quadratic bezier curve into n points."""
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((x, y))
    return pts


def chain(*segments):
    """Concatenate sampled curves into one point list without duplicates."""
    out = []
    for seg in segments:
        if out and seg and out[-1] == seg[0]:
            out.extend(seg[1:])
        else:
            out.extend(seg)
    return out


def draw_mark(body_color, accent_color, size=W):
    """Render the mark on a transparent canvas of size x size."""
    cw = W * S
    img = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def sc(pts):
        return [(x * S, y * S) for x, y in pts]

    # --- charcoal body: abstract knight-like form -------------------
    body = chain(
        # top-right point, long slope down-left to the muzzle tip
        qbez((352, 58), (245, 70), (118, 152)),
        # gentle concave notch below the tip (rounded, not a V)
        qbez((118, 152), (148, 178), (205, 208)),
        # notch out to the chest bulge (leftmost)
        qbez((205, 208), (142, 270), (132, 340)),
        # chest down to the rounded base
        qbez((132, 340), (122, 400), (148, 428)),
        # base bottom curve to the right
        qbez((148, 428), (195, 456), (252, 452)),
        # up to the bottom-right corner
        qbez((252, 452), (315, 452), (352, 426)),
        # straight-ish right edge back to the top point
        qbez((352, 426), (356, 240), (352, 58)),
    )
    d.polygon(sc(body), fill=body_color)

    # --- red crescent hugging the right edge ------------------------
    # outer edge (top point -> sweeping down to the tail tip)
    outer = qbez((328, 86), (400, 130), (400, 210))
    outer += qbez((400, 210), (415, 350), (455, 450))[1:]
    # inner edge back up, hugging the body's right edge
    inner = qbez((455, 450), (380, 380), (352, 300))
    inner += qbez((352, 300), (350, 190), (328, 86))[1:]
    crescent = outer + inner
    d.polygon(sc(crescent), fill=accent_color)

    return img.resize((size, size), Image.LANCZOS)


def main():
    light = draw_mark(CHARCOAL, RED)
    light.save(OUT / "logo-mark.png")

    white = draw_mark(WHITE, RED)
    white.save(OUT / "logo-mark-white.png")

    # all-white monochrome mark (header + footer on dark tiles)
    mono = draw_mark(WHITE, WHITE)
    mono.save(OUT / "logo-mark-mono.png")

    # favicon: light variant padded onto a square with small margin
    pad = int(W * 0.06)
    mark = light.resize((W - 2 * pad, W - 2 * pad), Image.LANCZOS)
    fav = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    fav.paste(mark, (pad, pad), mark)
    fav.save(OUT / "favicon.png")

    for name in ("logo-mark.png", "logo-mark-white.png", "logo-mark-mono.png", "favicon.png"):
        p = OUT / name
        print(f"{name}: {p.stat().st_size} bytes, mode={Image.open(p).mode}")


if __name__ == "__main__":
    main()
