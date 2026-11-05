"""Deterministic color-cast gate for generated Etsy product photos.

Measures how far the *should-be-neutral* pixels of each image drift toward
yellow/orange, plus how warm the whole frame's palette is. Optionally applies a
neutral-anchor white-balance correction (von Kries gains in linear sRGB).

Usage
-----
  python color_cast_check.py <dir-or-files...>                # measure only
  python color_cast_check.py <dir> --json color-cast-report.json
  python color_cast_check.py <dir> --fix --out <dir>/wb-fixed # measure + correct

Metrics per image
-----------------
  neutral_b   mean CIELAB b* of near-neutral, mid/high-luminance pixels.
              These are the pixels that should read white / gray.
              b* > 0 = yellow, b* < 0 = blue.
  neutral_a   mean a* of the same pixels. a* > 0 = red/magenta (peach cast).
  frame_rb    mean(R)/mean(B) over the whole frame. Palette warmth, not white
              balance: a neutral-WB photo full of wood, linen and gold still
              scores high here, and buyers still perceive it as "warm".
  neutral_pct share of pixels used as the neutral sample. Below ~8% the
              neutral_b reading is unreliable (nothing neutral in frame),
              which is itself a palette finding.

Thresholds (visual daylight target ~5000-5500 K, see scene-planning.md §3)
--------------------------------------------------------------------------
  neutral_b <= 3.0            pass
  3.0 < neutral_b <= 6.0      borderline  (fix or regenerate; never silently accept)
  neutral_b > 6.0             reject      (regenerate with restated neutral anchors)
  frame_rb  >  1.25           palette_warm_dominant (scene planning problem, not WB)
  neutral_pct < 8             no_neutral_anchor     (scene has nothing neutral in it)

--fix applies a per-channel gain so the neutral sample's mean becomes gray.
It refuses to correct when the required gain exceeds +/-20% (the image is too
far off; regenerate instead) or when there is no reliable neutral sample.
A corrected file still needs a product-color re-check against the reference.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

PASS_B, BORDER_B = 3.0, 6.0
WARM_RB = 1.25
MIN_NEUTRAL_PCT = 8.0
MAX_GAIN_DEV = 0.20


# --------------------------------------------------------------------------- color math
def srgb_to_linear(c: np.ndarray) -> np.ndarray:
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(c: np.ndarray) -> np.ndarray:
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(np.clip(c, 0, None), 1 / 2.4) - 0.055)


_M = np.array(
    [[0.4124564, 0.3575761, 0.1804375],
     [0.2126729, 0.7151522, 0.0721750],
     [0.0193339, 0.1191920, 0.9503041]], dtype=np.float32)
_WHITE = np.array([0.95047, 1.0, 1.08883], dtype=np.float32)


def linear_to_lab(lin: np.ndarray):
    xyz = lin @ _M.T / _WHITE
    eps, kappa = 216 / 24389, 24389 / 27
    f = np.where(xyz > eps, np.cbrt(xyz), (kappa * xyz + 16) / 116)
    L = 116 * f[..., 1] - 16
    a = 500 * (f[..., 0] - f[..., 1])
    b = 200 * (f[..., 1] - f[..., 2])
    return L, a, b


def neutral_mask(L, a, b):
    chroma = np.sqrt(a * a + b * b)
    m = (chroma < 14) & (L > 45)
    if m.mean() < 0.02:  # relax once for very colorful frames
        m = (chroma < 20) & (L > 35)
    return m


# --------------------------------------------------------------------------- measure
def measure(path: str, max_side: int = 768) -> dict:
    im = Image.open(path).convert("RGB")
    im.thumbnail((max_side, max_side))
    rgb = np.asarray(im).astype(np.float32) / 255.0
    lin = srgb_to_linear(rgb)
    L, a, b = linear_to_lab(lin)
    m = neutral_mask(L, a, b)
    pct = float(m.mean() * 100)
    nb = float(b[m].mean()) if m.any() else float("nan")
    na = float(a[m].mean()) if m.any() else float("nan")
    rb = float(rgb[..., 0].mean() / max(rgb[..., 2].mean(), 1e-6))

    flags = []
    if pct < MIN_NEUTRAL_PCT:
        flags.append("no_neutral_anchor")
    if rb > WARM_RB:
        flags.append("palette_warm_dominant")
    if np.isnan(nb):
        status = "unmeasurable"
    elif nb <= PASS_B:
        status = "pass"
    elif nb <= BORDER_B:
        status = "borderline"
    else:
        status = "reject"

    return {
        "file": os.path.basename(path),
        "neutral_b": None if np.isnan(nb) else round(nb, 1),
        "neutral_a": None if np.isnan(na) else round(na, 1),
        "frame_rb": round(rb, 2),
        "neutral_pct": round(pct, 1),
        "color_cast_status": status,
        "flags": flags,
    }


# --------------------------------------------------------------------------- fix
def fix(path: str, out_path: str) -> dict:
    im = Image.open(path).convert("RGB")
    full = np.asarray(im).astype(np.float32) / 255.0
    lin = srgb_to_linear(full)
    L, a, b = linear_to_lab(lin)
    m = neutral_mask(L, a, b)
    if m.mean() * 100 < MIN_NEUTRAL_PCT:
        return {"file": os.path.basename(path), "fixed": False, "reason": "no reliable neutral sample"}

    # Two von Kries passes: the neutral sample shifts slightly after the first
    # correction, a second pass converges. Total gain is still bounded.
    total = np.ones(3, dtype=np.float32)
    corrected = lin
    for _ in range(2):
        mean_rgb = corrected[m].mean(axis=0)
        g = mean_rgb[1] / mean_rgb  # anchor to green
        total = total * g
        corrected = np.clip(lin * total, 0, 1)
        if np.any(np.abs(total - 1.0) > MAX_GAIN_DEV):
            return {
                "file": os.path.basename(path), "fixed": False,
                "reason": f"required gain {[round(float(x), 3) for x in total]} exceeds "
                          f"+/-{int(MAX_GAIN_DEV * 100)}%; regenerate instead",
            }

    out = (linear_to_srgb(corrected) * 255 + 0.5).astype(np.uint8)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    Image.fromarray(out, "RGB").save(out_path, "PNG")
    after = measure(out_path)
    return {
        "file": os.path.basename(path),
        "fixed": True,
        "out": out_path,
        "gains_rgb": [round(float(x), 3) for x in total],
        "after": after,
    }


# --------------------------------------------------------------------------- cli
def collect(inputs):
    files = []
    for p in inputs:
        if os.path.isdir(p):
            files += sorted(glob.glob(os.path.join(p, "shot-*.png")))
        else:
            files.append(p)
    return files


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="directories (shot-*.png) or image files")
    ap.add_argument("--json", help="write per-shot report to this path")
    ap.add_argument("--fix", action="store_true", help="apply neutral-anchor white-balance correction")
    ap.add_argument("--out", help="output dir for --fix (default: <input dir>/wb-fixed)")
    args = ap.parse_args(argv)

    files = collect(args.inputs)
    if not files:
        print("no images found", file=sys.stderr)
        return 2

    rows = [measure(f) for f in files]
    print(f"{'file':<20}{'b*':>6}{'a*':>6}{'R/B':>6}{'neut%':>7}  status      flags")
    for r in rows:
        nb = "n/a" if r["neutral_b"] is None else f"{r['neutral_b']:.1f}"
        na = "n/a" if r["neutral_a"] is None else f"{r['neutral_a']:.1f}"
        print(f"{r['file']:<20}{nb:>6}{na:>6}{r['frame_rb']:>6.2f}{r['neutral_pct']:>6.0f}%  {r['color_cast_status']:<10}  {','.join(r['flags'])}")

    bs = np.array([r["neutral_b"] for r in rows if r["neutral_b"] is not None], dtype=float)
    summary = {
        "shots": len(rows),
        "median_neutral_b": round(float(np.median(bs)), 1) if bs.size else None,
        "borderline": int(sum(r["color_cast_status"] == "borderline" for r in rows)),
        "reject": int(sum(r["color_cast_status"] == "reject" for r in rows)),
        "palette_warm_dominant": int(sum("palette_warm_dominant" in r["flags"] for r in rows)),
        "no_neutral_anchor": int(sum("no_neutral_anchor" in r["flags"] for r in rows)),
    }
    print("-- set:", json.dumps(summary, ensure_ascii=False))

    fixes = []
    if args.fix:
        for f, r in zip(files, rows):
            if r["color_cast_status"] in ("borderline", "reject"):
                out_dir = args.out or os.path.join(os.path.dirname(f) or ".", "wb-fixed")
                res = fix(f, os.path.join(out_dir, os.path.basename(f)))
                fixes.append(res)
                if res["fixed"]:
                    print(f"fixed {res['file']}: gains={res['gains_rgb']} -> b*={res['after']['neutral_b']} ({res['after']['color_cast_status']})")
                else:
                    print(f"skip  {res['file']}: {res['reason']}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"thresholds": {"pass_b": PASS_B, "borderline_b": BORDER_B, "warm_rb": WARM_RB,
                                      "min_neutral_pct": MIN_NEUTRAL_PCT},
                       "summary": summary, "shots": rows, "fixes": fixes}, fh, ensure_ascii=False, indent=2)
        print(f"report -> {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
