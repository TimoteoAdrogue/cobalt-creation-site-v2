#!/usr/bin/env python3
"""Download the live site's original media and build responsive derivatives.

    python3 tools/media.py        # -> src-media/ (originals) and media/ (derivatives)

Originals: https://static.wixstatic.com/media/<name> with no transform serves the upload.
(The /v1/fill/... transform crops to the requested box: never use it for sources.)
Derivatives: <stem>-<w>.avif and <stem>-<w>.jpg at the widths below, capped at the original.
"""
import json, subprocess, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "src-media", ROOT / "media"
UA = {"User-Agent": "Mozilla/5.0"}
WORK_W = (800, 1600)
WIDE_W = (1280, 1920, 2560)
Image.MAX_IMAGE_PIXELS = None


def stem(name):
    return name.split("~")[0].replace("53e2f6_", "")[:12]


def get(url, dest):
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    tmp = dest.with_suffix(dest.suffix + ".part")
    subprocess.run(["curl", "-sSfL", "--retry", "4", "--retry-delay", "2", "--max-time", "600",
                    "-A", UA["User-Agent"], "-o", str(tmp), url], check=True)
    tmp.rename(dest)
    return dest


def derive(name, widths):
    src = SRC / name
    im = ImageOps.exif_transpose(Image.open(src))
    if im.mode not in ("RGB", "L"):
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.convert("RGBA").split()[-1])
        im = bg
    im = im.convert("RGB")
    out = {"w": im.width, "h": im.height, "files": []}
    for w in widths:
        w = min(w, im.width)
        if w in [f["w"] for f in out["files"]]:
            continue
        h = round(im.height * w / im.width)
        r = im.resize((w, h), Image.LANCZOS)
        base = OUT / f"{stem(name)}-{w}"
        r.save(f"{base}.jpg", "JPEG", quality=82, optimize=True, progressive=True)
        r.save(f"{base}.avif", "AVIF", quality=60, speed=6)
        out["files"].append({"w": w, "h": h, "jpg": f"{base.name}.jpg", "avif": f"{base.name}.avif"})
    return name, out


def main():
    SRC.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    works = json.load(open(ROOT / "data/works.json"))
    meta = json.load(open(ROOT / "data/pages.json"))
    work_names = sorted({w["media"] for w in works} | set(meta["home_columns"]))
    wide_names = sorted({n for p in meta["pages"].values() for n in p["banner"]})
    names = sorted(set(work_names) | set(wide_names) | {meta["logo_wall"]})
    with ThreadPoolExecutor(8) as ex:
        list(ex.map(lambda n: get(f"https://static.wixstatic.com/media/{n}", SRC / n), names))
    get(meta["video"], SRC / "atelier-video.mp4")
    get(meta["book"], SRC / "cobalt-creation-book.pdf")
    get(f"https://i.ytimg.com/vi/{meta['youtube']}/maxresdefault.jpg", SRC / "youtube-poster.jpg")

    jobs = [(n, WORK_W) for n in work_names] + [(n, WIDE_W) for n in wide_names if n not in work_names]
    with ThreadPoolExecutor(6) as ex:
        index = dict(ex.map(lambda j: derive(*j), jobs))
    (ROOT / "data/media.json").write_text(json.dumps(index, indent=1))
    print("originals", len(names), "derived", len(index))


if __name__ == "__main__":
    main()
