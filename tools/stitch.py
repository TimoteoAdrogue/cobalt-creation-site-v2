#!/usr/bin/env python3
"""Stitch verify.mjs viewport segments into one tall image per page and width (last segment trimmed)."""
import re, sys
from pathlib import Path
from PIL import Image
d = Path(sys.argv[1])
groups = {}
for f in sorted(d.glob("*-seg*.jpg")):
    groups.setdefault(re.sub(r"-seg\d+\.jpg$", "", f.name), []).append(f)
for name, files in groups.items():
    ims = [Image.open(f) for f in files]
    W, h = ims[0].size
    out = Image.new("RGB", (W, h * len(ims)))
    for i, im in enumerate(ims):
        out.paste(im, (0, i * h))
    out.save(d / f"{name}.jpg", quality=78)
    for f in files:
        f.unlink()
print(len(groups), "pages stitched")
