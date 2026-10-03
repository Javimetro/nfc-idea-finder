"""Render docs/anim/pipeline.html to docs/img/32-pipeline.gif (800x450, 12 fps, loops).

    python3 scripts/render_animation.py                 # embed cases.json, render every frame, build the GIF
    python3 scripts/render_animation.py --keyframes 1,5,13,22,26 --out /some/dir   # just a few PNGs to look at

Frames are drawn by the page's own render(t) in headless Chromium (Docker image tapwise-ui, no network),
then Pillow (installed in a throwaway container) scales them 2x nearest-neighbour and builds the GIF."""
import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGE = os.path.join(ROOT, "docs", "anim", "pipeline.html")
CASES = os.path.join(ROOT, "docs", "anim", "cases.json")
GIF = os.path.join(ROOT, "docs", "img", "32-pipeline.gif")
IMAGE = "tapwise-ui:latest"

CAPTURE = r"""
import base64, json, sys
from playwright.sync_api import sync_playwright
times = json.loads(sys.argv[1])
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.goto("file:///anim/pipeline.html?export")
    pg.wait_for_function("window.READY === true")
    err = pg.evaluate("window.ANIM.error")
    if err:
        sys.exit("page refused the data: " + err)
    for n, t in times:
        url = pg.evaluate(f"window.frameDataURL({t})")
        open(f"/frames/{n:04d}.png", "wb").write(base64.b64decode(url.split(",", 1)[1]))
    b.close()
"""

ASSEMBLE = r"""
import glob, sys
from PIL import Image
files = sorted(glob.glob("/frames/*.png"))
frames = [Image.open(f).convert("RGB").resize((800, 450), Image.NEAREST) for f in files]
colors = set()
for f in frames:
    cs = f.getcolors(maxcolors=256)
    if cs is None:
        sys.exit("a frame has more than 256 colours: the palette isn't fixed")
    colors.update(c for _, c in cs)
colors = sorted(colors)
pal = Image.new("P", (1, 1))
pal.putpalette([v for c in colors for v in c] + [0, 0, 0] * (256 - len(colors)))
idx = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
durations = [(80, 80, 90)[i % 3] for i in range(len(idx))]       # averages 83.3 ms = 12 fps
idx[0].save("/out/32-pipeline.gif", save_all=True, append_images=idx[1:], duration=durations, loop=0, optimize=False)
print(f"{len(idx)} frames, {len(colors)} colours")
"""


def embed():
    data = json.load(open(CASES))
    text = json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")
    html = open(PAGE).read()
    new, n = re.subn(r'(<script id="cases" type="application/json">\n).*?(\n</script>)',
                     lambda m: m.group(1) + text + m.group(2), html, flags=re.S)
    if n != 1:
        raise SystemExit("couldn't find the embedded data block in pipeline.html")
    open(PAGE, "w").write(new)


def capture(times, frames_dir):
    subprocess.run(["docker", "run", "--rm", "--network", "none",
                    "-v", f"{os.path.dirname(PAGE)}:/anim:ro", "-v", f"{frames_dir}:/frames",
                    IMAGE, "python", "-c", CAPTURE, json.dumps(times)], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keyframes", help="comma-separated times in seconds; writes PNGs only")
    ap.add_argument("--out", help="where to put keyframe PNGs")
    a = ap.parse_args()
    embed()
    if a.keyframes:
        out = os.path.abspath(a.out or tempfile.mkdtemp())
        os.makedirs(out, exist_ok=True)
        capture([[i, float(t)] for i, t in enumerate(a.keyframes.split(","))], out)
        print("keyframes in", out)
        return
    fps, dur = 12, 28
    frames_dir = tempfile.mkdtemp(prefix="tapwise-frames-")
    try:
        capture([[n, n / fps] for n in range(fps * dur)], frames_dir)
        subprocess.run(["docker", "run", "--rm", "-v", f"{frames_dir}:/frames:ro",
                        "-v", f"{os.path.dirname(GIF)}:/out", IMAGE, "sh", "-c",
                        "pip install -q pillow >/dev/null 2>&1 && python -c \"$0\"", ASSEMBLE], check=True)
    finally:
        shutil.rmtree(frames_dir, ignore_errors=True)
    print(f"{GIF}: {os.path.getsize(GIF) / 1e6:.2f} MB")


main()
