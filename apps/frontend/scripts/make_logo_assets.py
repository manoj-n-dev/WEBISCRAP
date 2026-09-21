#!/usr/bin/env python3
"""Generate every favicon / app-icon / OG / navbar logo file from public/assets/inner-logo.png and branding-logo.png.
Run from apps/frontend:  python3 scripts/make_logo_assets.py   (needs: pip install pillow)"""
import os
from PIL import Image, ImageChops

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_MARK = os.path.join(ROOT, "public", "assets", "inner-logo.png")
SRC_BRAND = os.path.join(ROOT, "public", "assets", "branding-logo.png")
BG = (5, 7, 12, 255)            # --bg-0 (#05070c)


def transparent_mark(path: str) -> Image.Image:
    """The source has a solid black background: derive alpha from brightness so the blue mark sits cleanly on any background."""
    im = Image.open(path).convert("RGB")
    lum = im.convert("L").point(lambda v: 0 if v < 14 else min(255, int((v - 14) * 255 / 60)))
    rgba = im.convert("RGBA")
    rgba.putalpha(lum)
    bbox = lum.getbbox()
    return rgba.crop(bbox)


def square(im: Image.Image, size: int, pad_ratio: float = 0.14, bg=None) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), bg or (0, 0, 0, 0))
    inner = int(size * (1 - 2 * pad_ratio))
    w, h = im.size
    scale = inner / max(w, h)
    fitted = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    canvas.alpha_composite(fitted, ((size - fitted.width) // 2, (size - fitted.height) // 2))
    return canvas


def out(*parts):
    p = os.path.join(ROOT, *parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


mark = transparent_mark(SRC_MARK)

# Next.js file conventions (auto-added to <head>)
square(mark, 512, 0.10, BG).save(out("src", "app", "icon.png"), optimize=True)
square(mark, 180, 0.12, BG).save(out("src", "app", "apple-icon.png"), optimize=True)
square(mark, 64, 0.06, BG).save(out("src", "app", "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])

# PWA / manifest icons + navbar mark (transparent)
square(mark, 192, 0.10, BG).save(out("public", "icon-192.png"), optimize=True)
square(mark, 512, 0.10, BG).save(out("public", "icon-512.png"), optimize=True)
square(mark, 128, 0.02).save(out("public", "logo-mark.png"), optimize=True)      # navbar + e-mail

# Open Graph / Twitter card 1200x630 from the brand lock-up (mark + tagline)
brand = Image.open(SRC_BRAND).convert("RGB")
w, h = brand.size
crop = brand.crop((int(w * 0.25), int(h * 0.22), int(w * 0.75), int(h * 0.80)))     # mark + tagline
og = Image.new("RGB", (1200, 630), BG[:3])
scale = min(1000 / crop.width, 560 / crop.height)
crop = crop.resize((int(crop.width * scale), int(crop.height * scale)), Image.LANCZOS)
og.paste(crop, ((1200 - crop.width) // 2, (630 - crop.height) // 2))
og.save(out("src", "app", "opengraph-image.png"), optimize=True)
og.save(out("src", "app", "twitter-image.png"), optimize=True)
print("Logo assets written.")
