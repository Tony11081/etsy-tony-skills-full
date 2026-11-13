#!/usr/bin/env python3
"""Check whether a product is drawn at its real size relative to scene anchors.

Measure two pixel lengths in the rendered image: the product's long side and one
edge of known real size on an anchor at the same depth (mantel height, door width,
chair back, a hand). The script converts the product's pixel length into the size
the scene implies and compares it with the real size.

    python scale_check.py --product-cm 48 --product-px 482 \
        --anchor "mantel height:130-140:698" --anchor "firebox width:80-100:470"

    python scale_check.py --product-cm 48 --scene-cm 150     # planning: frame share

Anchor format: NAME:CM:PX or NAME:CM_LOW-CM_HIGH:PX. A range is treated as "any
real size in this range is plausible", so the product only deviates when its real
size falls outside the whole implied range.

Verdict per anchor: deviation <= 15% pass, <= 30% borderline, otherwise reject.
The overall verdict is the worst one. Exit code 0 pass, 1 borderline, 2 reject,
64 bad arguments. No third-party packages.
"""
import argparse
import json
import sys

PASS_DEV = 0.15
BORDER_DEV = 0.30
ORDER = {"pass": 0, "borderline": 1, "reject": 2}


def parse_anchor(text):
    parts = text.rsplit(":", 2)
    if len(parts) != 3:
        raise ValueError(f"anchor must be NAME:CM:PX or NAME:LOW-HIGH:PX, got {text!r}")
    name, cm, px = parts
    if "-" in cm:
        lo, hi = (float(v) for v in cm.split("-", 1))
    else:
        lo = hi = float(cm)
    px = float(px)
    if not name.strip() or lo <= 0 or hi < lo or px <= 0:
        raise ValueError(f"anchor values must be positive and LOW <= HIGH, got {text!r}")
    return name.strip(), lo, hi, px


def check_anchor(product_cm, product_px, name, lo, hi, px):
    implied_lo = product_px * lo / px
    implied_hi = product_px * hi / px
    if implied_lo <= product_cm <= implied_hi:
        deviation, direction = 0.0, "ok"
    elif product_cm < implied_lo:
        deviation, direction = (implied_lo - product_cm) / product_cm, "too_large"
    else:
        deviation, direction = (product_cm - implied_hi) / product_cm, "too_small"
    if deviation <= PASS_DEV:
        status = "pass"
    elif deviation <= BORDER_DEV:
        status = "borderline"
    else:
        status = "reject"
    return {
        "anchor": name,
        "anchor_real_cm": [lo, hi],
        "anchor_px": px,
        "implied_product_cm": [round(implied_lo, 1), round(implied_hi, 1)],
        "deviation_pct": round(deviation * 100, 1),
        "direction": direction,
        "status": status,
        "expected_product_px": [round(product_cm * px / hi), round(product_cm * px / lo)],
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--product-cm", type=float, required=True, help="real length of the measured product side")
    ap.add_argument("--product-px", type=float, help="that side's length in the image, in pixels")
    ap.add_argument("--anchor", action="append", default=[], help="NAME:CM:PX or NAME:LOW-HIGH:PX (repeatable)")
    ap.add_argument("--scene-cm", type=float, help="planning only: real height or width the frame covers")
    ap.add_argument("--json", action="store_true", help="print JSON only")
    args = ap.parse_args(argv)

    if args.product_cm <= 0:
        print("--product-cm must be positive", file=sys.stderr)
        return 64

    result = {"product_real_cm": args.product_cm}

    if args.scene_cm:
        if args.scene_cm <= 0:
            print("--scene-cm must be positive", file=sys.stderr)
            return 64
        share = args.product_cm / args.scene_cm
        result["frame_share_pct"] = round(share * 100, 1)
        result["frame_share_note"] = (
            "product larger than the framed area" if share > 1
            else "too small to read in a thumbnail; move the camera closer" if share < 0.2
            else "ok"
        )

    if args.anchor:
        if not args.product_px or args.product_px <= 0:
            print("--product-px is required with --anchor", file=sys.stderr)
            return 64
        try:
            anchors = [parse_anchor(a) for a in args.anchor]
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 64
        checks = [check_anchor(args.product_cm, args.product_px, *a) for a in anchors]
        result["product_px"] = args.product_px
        result["checks"] = checks
        result["scale_status"] = max((c["status"] for c in checks), key=ORDER.get)
    elif not args.scene_cm:
        print("give --anchor (with --product-px) or --scene-cm", file=sys.stderr)
        return 64

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if "frame_share_pct" in result:
            print(f"frame share: product {args.product_cm:g} cm / scene {args.scene_cm:g} cm "
                  f"= {result['frame_share_pct']}% ({result['frame_share_note']})")
        for c in result.get("checks", []):
            lo, hi = c["implied_product_cm"]
            size = f"{lo:g} cm" if lo == hi else f"{lo:g}-{hi:g} cm"
            word = {"ok": "matches", "too_large": "too large by", "too_small": "too small by"}[c["direction"]]
            dev = "" if c["direction"] == "ok" else f" {c['deviation_pct']}%"
            elo, ehi = c["expected_product_px"]
            print(f"[{c['status']}] vs {c['anchor']}: drawn as {size}, real {args.product_cm:g} cm, "
                  f"{word}{dev}; should measure about {elo}-{ehi} px")
        if "scale_status" in result:
            print(f"scale_status: {result['scale_status']}")

    return ORDER.get(result.get("scale_status", "pass"), 0)


if __name__ == "__main__":
    sys.exit(main())
