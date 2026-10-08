#!/usr/bin/env python3
"""Cut the 56 client logos out of the live site's logo wall (7 x 8 white tiles).

Output: media/logos/<slug>.png, black ink on transparent, trimmed to the mark,
plus data/logos.json (row-major order, as on cobaltcreation.com) and a contact sheet.
"""
import json, re, unicodedata
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src-media/53e2f6_61ffb11644664713932a2e78b41f8871~mv2.jpg"
OUT = ROOT / "media/logos"
NAMES = """Louis Vuitton|LVMH|Chanel|Ruinart|Hennessy|Diptyque|Galeries Lafayette
Montblanc|Louis XIII|Hermès|Dior|Guerlain|Cartier|Breguet
Yves Saint Laurent|Givenchy|L'Oréal|Chloé|Christian Louboutin|Aerin|Chaumet
Estée Lauder|Lalique|Dom Pérignon|Les Parfumables|Celine|Bonpoint|Kenzo
Éditions de Parfums Frédéric Malle|Shiseido|Dolce & Gabbana|Clarins|Issey Miyake|Moët & Chandon|Messika
Caron|Bobbi Brown|Narciso Rodriguez|Sisley|Rémy Martin|Jo Malone London|Tiffany & Co.
L'Artisan Parfumeur|Prada|Kilian|Marc Jacobs|Burberry|Puig|Miu Miu
Tumi|Penhaligon's|Maison Francis Kurkdjian|Maison Psyché|Jacadi|Annick Goutal|Clinique"""


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def runs(profile, th, minlen=100):
    on, out, s = profile > th, [], None
    for i, v in enumerate(on):
        if v and s is None:
            s = i
        if not v and s is not None:
            out.append((s, i)); s = None
    if s is not None:
        out.append((s, len(on)))
    return [r for r in out if r[1] - r[0] > minlen]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    grey = np.asarray(Image.open(SRC).convert("L")).astype(np.float32)
    white = grey >= 253
    cols = [r for r in runs(white.mean(0), 0.3) if 400 < r[1] - r[0] < 700]
    rows = [r for r in runs(white.mean(1), 0.3) if 400 < r[1] - r[0] < 700]
    assert len(cols) == 7 and len(rows) == 8, (cols, rows)
    names = [n.split("|") for n in NAMES.splitlines()]
    out, sheet = [], Image.new("RGB", (7 * 260, 8 * 140), "white")
    for r, (y0, y1) in enumerate(rows):
        for c, (x0, x1) in enumerate(cols):
            pad = 18  # stay clear of the tile's soft shadow
            cell = grey[y0 + pad:y1 - pad, x0 + pad:x1 - pad]
            ink = cell < 200
            ys, xs = np.where(ink)
            by0, by1, bx0, bx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            m = 6
            crop = cell[max(0, by0 - m):by1 + m, max(0, bx0 - m):bx1 + m]
            alpha = np.clip((255 - crop) * (255 / 235), 0, 255).astype(np.uint8)  # darkness -> opacity
            rgba = np.zeros(crop.shape + (4,), np.uint8)
            rgba[..., 3] = alpha
            img = Image.fromarray(rgba, "RGBA")
            if img.height > 220:
                img = img.resize((round(img.width * 220 / img.height), 220), Image.LANCZOS)
            name = names[r][c]
            f = f"{slug(name)}.png"
            img.save(OUT / f, optimize=True)
            out.append({"name": name, "file": f, "w": img.width, "h": img.height})
            th = img.copy(); th.thumbnail((240, 110))
            sheet.paste(th, (c * 260 + 10, r * 140 + 10), th)
    (ROOT / "data/logos.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    sheet.save(ROOT / "data/sheets/logos.png")
    print(len(out), "logos")


if __name__ == "__main__":
    main()
