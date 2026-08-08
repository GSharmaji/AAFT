#!/usr/bin/env python3
"""
Redact + crop the real ad-account screenshots into clean proof clips.

Rule: blur client name + campaign names; keep email + the numbers.
- Google Ads overviews: crop to the colored metric-tile bar (no client name is
  present there). The Jan-Sep aggregate additionally keeps the header row (email
  + date range) since it shows no client name.
- Meta tables: keep the table, Gaussian-blur the Campaign-name column, keep the
  Purchase ROAS numbers.

Output -> assets/proof/clip-*.png
"""
import os
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "proof-screenshots")
OUT = os.path.join(ROOT, "assets", "proof")
os.makedirs(OUT, exist_ok=True)

# Google metric-tile brand colors (approx RGB) to detect the bar.
G_COLORS = [(66, 133, 244), (234, 67, 53), (251, 171, 4), (52, 168, 83)]

def close(px, c, tol=45):
    return abs(px[0]-c[0]) <= tol and abs(px[1]-c[1]) <= tol and abs(px[2]-c[2]) <= tol

def find_metric_band(im):
    """Return (x0,y0,x1,y1) bounding box of the 4-color metric bar."""
    rgb = im.convert("RGB")
    W, H = rgb.size
    px = rgb.load()
    step = 2
    rows = []
    for y in range(0, H, step):
        seen = set()
        xs = []
        for x in range(0, W, step):
            p = px[x, y]
            for i, c in enumerate(G_COLORS):
                if close(p, c):
                    seen.add(i); xs.append(x)
                    break
        if len(seen) >= 3 and xs:            # row is inside the tile bar
            rows.append((y, min(xs), max(xs)))
    if not rows:
        return None
    y0 = rows[0][0]; y1 = rows[-1][0]
    x0 = min(r[1] for r in rows); x1 = max(r[2] for r in rows)
    padx, pady = 6, 10
    return (max(0, x0-padx), max(0, y0-pady), min(W, x1+padx), min(H, y1+pady))

def gblur_box(im, box, radius=18):
    """Blur a rectangular region in-place."""
    region = im.crop(box).filter(ImageFilter.GaussianBlur(radius))
    im.paste(region, box)

def do_google(fname, out, hero=False):
    im = Image.open(os.path.join(SRC, fname)).convert("RGB")
    W, H = im.size
    band = find_metric_band(im)
    if not band:
        print("  ! no band found in", fname); return
    x0, y0, x1, y1 = band
    if hero:
        # keep everything from the top (email + date row) down to the tiles
        clip = im.crop((0, 0, W, y1))
    else:
        clip = im.crop((x0, y0, x1, y1))
    clip.save(os.path.join(OUT, out))
    print(f"  google {out}: {clip.size}")

def do_meta(fname, out, camp_x1_frac=0.225):
    im = Image.open(os.path.join(SRC, fname)).convert("RGB")
    W, H = im.size
    # Blur the entire left column (checkbox/toggle + "Campaign" header + names),
    # full height — robust across both the wide and tightly-cropped Meta layouts.
    box = (0, 0, int(W*camp_x1_frac), H)
    gblur_box(im, box, radius=16)
    im.save(os.path.join(OUT, out))
    print(f"  meta   {out}: {im.size}  blurred x[{box[0]}:{box[2]}] y[{box[1]}:{box[3]}]")

GOOGLE = {
    "image-1786172653171.png": ("clip-g-jansep.png", True),   # HERO: keeps email+date
    "image-1786172801218.png": ("clip-g-apr.png", False),
    "image-1786172805606.png": ("clip-g-may.png", False),
    "image-1786172808742.png": ("clip-g-jun.png", False),
    "image-1786172812331.png": ("clip-g-jul.png", False),
    "image-1786172815208.png": ("clip-g-aug.png", False),
    "Screenshot 2024-11-26 122942.png": ("clip-g-oct.png", False),
    "Screenshot 2024-11-26 123003.png": ("clip-g-nov.png", False),
}
META = {
    "image-1786172779346.png": "clip-m-may.png",
    "image-1786172784952.png": "clip-m-jun.png",
    "image-1786172790030.png": "clip-m-jul.png",
    "image-1786172793757.png": "clip-m-aug.png",
    "Screenshot 2024-11-26 123725.png": "clip-m-sep.png",
    "Screenshot 2024-11-26 123808.png": "clip-m-oct.png",
    "Screenshot 2024-11-26 123949.png": "clip-m-nov.png",
}

if __name__ == "__main__":
    print("Google clips:")
    for f, (o, hero) in GOOGLE.items():
        do_google(f, o, hero)
    print("Meta clips:")
    for f, o in META.items():
        do_meta(f, o)
    print("done ->", OUT)
