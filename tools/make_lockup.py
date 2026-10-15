#!/usr/bin/env python3
"""Render the UCCL horizontal lockup (mark + wordmark + tagline) to PNG.

Recreates the client-supplied logo artwork at the proportions of the
reference image: the charcoal/red mark on the left, the two-line company
name in condensed bold caps, and the red italic tagline underneath,
justified to the wordmark width.

Output:
  assets/img/logo-lockup.png   transparent, 1600px wide — drop-in
      replaceable with the official file under the same name

Run:  python3 tools/make_lockup.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from make_logo import CHARCOAL, RED, draw_mark

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img"

FONT_DIR = Path(
    "/opt/freestyle/python/lib/python3.12/site-packages/matplotlib/mpl-data/fonts/ttf"
)
SANS_BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"
SERIF_BOLD_ITALIC = FONT_DIR / "DejaVuSerif-BoldItalic.ttf"

# --- layout, in final (downsampled) pixels, from the reference image ------
S = 3                 # supersample factor
W = 1600              # final canvas width
PAD = 4               # edge padding
MARK_H = 218          # mark ink height
GAP = 26              # mark -> wordmark gap
CAP = 93              # wordmark cap height (line 1 ink height)
L2_TOP = 124          # ink top of line 2
TAG_TOP = 270         # ink top of tagline
TAG_INK = 86          # tagline ascender-to-descender height

LINE1 = "UNIQUE CONSULTANCY"
LINE2 = "& COLLECTION LTD."
TAGLINE = "we think different, we think unique"

_margin = 200  # drawing margin inside supersampled render canvas


def _canvas():
    return Image.new("RGBA", (W * S + 2 * _margin, H * S + 2 * _margin), (0, 0, 0, 0))


def render_ink(text, f, fill, sp=0.0):
    """Draw text (optionally letter-spaced) and return its tight ink crop."""
    img = _canvas()
    d = ImageDraw.Draw(img)
    x = float(_margin)
    if sp == 0.0:
        d.text((x, _margin), text, font=f, fill=fill)
    else:
        for ch in text:
            d.text((x, _margin), ch, font=f, fill=fill)
            x += d.textlength(ch, font=f) + sp
    return img.crop(img.getbbox())


def cap_size_for(target_cap):
    """Font size whose 'U' ink height equals target_cap."""
    f = ImageFont.truetype(str(SANS_BOLD), 200)
    probe = render_ink("U", f, CHARCOAL).height
    size = round(200 * target_cap / probe)
    f = ImageFont.truetype(str(SANS_BOLD), size)
    h = render_ink("U", f, CHARCOAL).height
    if h and h != target_cap:
        size = round(size * target_cap / h)
        f = ImageFont.truetype(str(SANS_BOLD), size)
    return f


def size_for_ink_height(path, text, target_h):
    """Binary-search a font size giving the requested ink height."""
    lo, hi = 30, 500
    best = None
    for _ in range(24):
        mid = (lo + hi) // 2
        f = ImageFont.truetype(str(path), mid)
        h = render_ink(text, f, CHARCOAL).height
        if best is None or abs(h - target_h) < abs(best[1] - target_h):
            best = (mid, h)
        if h < target_h:
            lo = mid + 1
        else:
            hi = mid - 1
    return ImageFont.truetype(str(path), best[0])


def fit_spacing(text, f, fill, target_w):
    """Letter-spacing making the text's ink width reach target_w."""
    w0 = render_ink(text, f, fill).width
    sp = (target_w - w0) / max(len(text) - 1, 1)
    return sp


def main():
    global H
    # --- mark ----------------------------------------------------------
    mark = draw_mark(CHARCOAL, RED, size=1024)
    mark = mark.crop(mark.getbbox())
    mark_w = round(MARK_H * mark.width / mark.height)
    mark = mark.resize((mark_w * S, MARK_H * S), Image.LANCZOS)

    text_x = mark_w + GAP
    text_w = W - text_x - PAD
    tw = text_w * S

    # --- wordmark, both lines justified to the same width --------------
    f1 = cap_size_for(CAP * S)
    ink1 = render_ink(LINE1, f1, CHARCOAL)
    squeeze = tw / ink1.width
    line1 = ink1.resize((tw, ink1.height), Image.LANCZOS)

    sp2 = fit_spacing(LINE2, f1, CHARCOAL, ink1.width)
    ink2 = render_ink(LINE2, f1, CHARCOAL, sp2)
    line2 = ink2.resize((tw, ink2.height), Image.LANCZOS)

    # --- tagline: ink height from the reference, tracked to full width -
    ft = size_for_ink_height(SERIF_BOLD_ITALIC, TAGLINE, TAG_INK * S)
    spt = fit_spacing(TAGLINE, ft, RED, tw)
    inkt = render_ink(TAGLINE, ft, RED, spt)
    if inkt.width != tw:
        inkt = inkt.resize((tw, inkt.height), Image.LANCZOS)

    # --- canvas --------------------------------------------------------
    global H
    H = max(
        MARK_H,
        L2_TOP + line2.height // S,
        TAG_TOP + inkt.height // S,
    ) + PAD

    img = _canvas()
    img.paste(mark, (_margin, _margin), mark)
    img.paste(line1, (_margin + text_x * S, _margin), line1)
    img.paste(line2, (_margin + text_x * S, _margin + L2_TOP * S), line2)
    img.paste(inkt, (_margin + text_x * S, _margin + TAG_TOP * S), inkt)

    out = img.crop((_margin, _margin, _margin + W * S, _margin + H * S))
    out = out.resize((W, H), Image.LANCZOS)
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "logo-lockup.png"
    out.save(path)

    print(f"{path.name}: {W}x{H}, {path.stat().st_size} bytes")
    print(f"mark {mark_w}px, text_x {text_x}, text_w {text_w}, squeeze {squeeze:.3f}")
    print(f"line2 spacing {sp2:.1f}px@{S}x, tagline spacing {spt:.1f}px@{S}x")


H = 360  # reassigned in main before _canvas() is first used

if __name__ == "__main__":
    main()
