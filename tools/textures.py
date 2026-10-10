#!/usr/bin/env python3
"""Seamless textures for V3: cobalt leather grain (shading only, blended over ink in CSS)
and gold leaf (fill for the « Feuille d'or » finish). Deterministic (fixed seeds)."""
import numpy as np
from PIL import Image
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "media"


def worley(size, cells, seed, warp=None):
    rng = np.random.default_rng(seed)
    pts = (np.arange(cells)[:, None, None] * 0 + rng.random((cells, cells, 2)))  # jitter in cell units
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32) * cells / size
    if warp is not None:                      # domain warp: curved, irregular cell borders
        xx = (xx + warp[0]) % cells
        yy = (yy + warp[1]) % cells
    cy, cx = np.floor(yy).astype(int), np.floor(xx).astype(int)
    d1 = np.full((size, size), 9.0, np.float32); d2 = d1.copy(); idx = np.zeros((size, size), int)
    for oy in (-1, 0, 1):
        for ox in (-1, 0, 1):
            ny, nx = (cy + oy) % cells, (cx + ox) % cells
            p = pts[ny, nx]
            px, py = cx + ox + p[..., 0], cy + oy + p[..., 1]
            d = np.hypot(xx - px, yy - py)
            closer = d < d1
            d2 = np.where(closer, d1, np.minimum(d2, d))
            idx = np.where(closer, ny * cells + nx, idx)
            d1 = np.where(closer, d, d1)
    return d1, d2, idx


def fine_noise(size, seed, scale=2):
    """Smooth value noise that tiles seamlessly (built from a 3 x 3 repeat, centre cropped)."""
    rng = np.random.default_rng(seed)
    k = max(2, size // scale)
    n = rng.random((k, k)).astype(np.float32)
    big = Image.fromarray((np.tile(n, (3, 3)) * 255).astype(np.uint8)).resize((size * 3, size * 3), Image.BICUBIC)
    return np.asarray(big).astype(np.float32)[size:2 * size, size:2 * size] / 255


def shade(h, light=(-0.6, -0.7, 0.9), strength=6.0):
    gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) / 2   # periodic: the tile stays seamless
    gy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) / 2
    nx, ny, nz = -gx * strength, -gy * strength, np.ones_like(h)
    nrm = np.sqrt(nx * nx + ny * ny + nz * nz)
    l = np.array(light) / np.linalg.norm(light)
    return (nx * l[0] + ny * l[1] + nz * l[2]) / nrm


def leather(size=1024):
    """Pebbled leather: domed, irregular grains with curved creases (domain-warped cells).
    Writes the raw height map for the WebGL hero, plus shaded tiles for CSS grounds."""
    from PIL import ImageFilter
    w = (fine_noise(size, 41, 64) - 0.5) * 1.1, (fine_noise(size, 43, 64) - 0.5) * 1.1
    d1, d2, _ = worley(size, 34, 11, warp=w)
    grain = np.clip(1 - d1 / (d2 + 1e-6), 0, 1) ** 0.6          # 1 at the pebble centre, 0 in the crease
    swell = fine_noise(size, 7, 128) * 0.25                        # slow undulation of the hide
    h = grain * 0.8 + swell + fine_noise(size, 3, 3) * 0.05 + fine_noise(size, 5, 16) * 0.06
    h = (h - h.min()) / (h.max() - h.min())
    tiled = Image.fromarray(np.tile((h * 255).astype(np.uint8), (3, 3))).filter(ImageFilter.GaussianBlur(0.9))
    him = tiled.crop((size, size, 2 * size, 2 * size))
    him.save(OUT / "leather-height.png", optimize=True)
    h = np.asarray(him).astype(np.float32) / 255
    s = shade(h, strength=6.0)
    s = (s - s.mean()) / (s.std() + 1e-6)
    Image.fromarray(np.clip(128 + s * 18, 0, 255).astype(np.uint8)).save(OUT / "leather.jpg", quality=86, optimize=True)
    Image.fromarray(np.clip(128 + s * 8, 0, 255).astype(np.uint8)).save(OUT / "leather-soft.jpg", quality=82, optimize=True)


def goldleaf(size=1024):
    d1, d2, idx = worley(size, 4, 23)
    rng = np.random.default_rng(5)
    tone = rng.uniform(0.92, 1.06, idx.max() + 1)[idx]           # each sheet sits at its own angle
    tear = np.exp(-((d2 - d1) / 0.035) ** 2)                      # thin seams where sheets overlap
    crumple = fine_noise(size, 9, 64) * 0.45 + fine_noise(size, 13, 24) * 0.35 + fine_noise(size, 17, 6) * 0.2
    s = shade(crumple, light=(-0.5, -0.8, 0.6), strength=26.0)
    spec = np.clip(s, 0, 1) ** 6                                   # metallic glints on the crumples
    lum = np.clip(tone * (0.46 + 0.46 * s + 0.7 * spec) - tear * 0.3, 0, 1.3)
    base = np.array([208, 171, 126], np.float32) / 255           # #D0AB7E
    hi = np.array([250, 234, 196], np.float32) / 255
    lo = np.array([118, 84, 44], np.float32) / 255
    t = np.clip(lum, 0, 1)[..., None]
    rgb = np.where(t < 0.62, lo + (base - lo) * (t / 0.62), base + (hi - base) * ((t - 0.62) / 0.38))
    rgb = np.clip(rgb * 255, 0, 255).astype(np.uint8)
    Image.fromarray(rgb).save(OUT / "goldleaf.jpg", quality=86)


if __name__ == "__main__":
    leather()
    goldleaf()
    print("ok")
