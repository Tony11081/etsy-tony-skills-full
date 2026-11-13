#!/usr/bin/env python3
"""Gate a photo plan before any image is generated, and recount it after rendering.

    python plan_check.py <out-dir>/plan.codex-direct.json            # before generating
    python plan_check.py <out-dir>/plan.codex-direct.json --actual   # after rendering

The plan must pass before the first generation call. It checks the things that a
set can get wrong while every single image still looks acceptable:

- atmosphere: product type, the buyer's moment, occasion signals, glow, product state
- scene levels: enough L3 and L2 shots for the product type, L3 hero, strong first three
- warm occasions use warm_scene for hero and scene shots
- composition: enough different types, no type overused, no identical neighbours
- scale: scale_lock present; scene prompts carry a scale sentence
- prompts: no evaluative or enlarging words

With --actual it counts `scene_level_actual` (graded from the rendered images)
instead of the planned `scene_level`.

Exit code 0 pass, 1 fail, 64 unreadable plan. No third-party packages.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

LEVELS = {"L0": 0, "L1": 1, "L2": 2, "L3": 3}
TYPES = ("occasion_led", "lifestyle_led", "proof_led")
# per 15 shots: (hero minimum level, L3 minimum, L2+L3 minimum, L3 in first three)
FLOORS = {"occasion_led": (3, 5, 9, 2), "lifestyle_led": (2, 3, 7, 0), "proof_led": (0, 0, 0, 0)}
WARM_OCCASION = re.compile(
    r"christmas|xmas|holiday|winter|advent|hanukkah|autumn|fall\b|thanksgiving|halloween|candle|fireside|fireplace"
    r"|圣诞|冬|节日|秋|感恩|万圣|烛|壁炉", re.I)
BANNED = ["beautiful", "luxury", "luxurious", "stunning", "cozy", "8k", "masterpiece", "highly detailed",
          "oversized", "fills the frame", "hero-sized"]
SIZE = re.compile(r"\d+(\.\d+)?\s*(cm|centimet|inch|inches|in\b|\")", re.I)


def scaled(count, n):
    return count if n == 15 else math.ceil(count * n / 15)


def comp_code(value):
    if isinstance(value, dict):
        value = value.get("code") or value.get("type") or ""
    m = re.match(r"\s*`?([A-M])\b", str(value or ""))
    return m.group(1) if m else None


def prompt_text(shot, base):
    for key in ("prompt", "prompt_text"):
        if isinstance(shot.get(key), str) and shot[key].strip():
            return shot[key]
    name = shot.get("prompt_file")
    if isinstance(name, str):
        path = (base / name)
        if path.is_file():
            return path.read_text(encoding="utf-8", errors="replace")
    return None


def check(plan, base, actual=False):
    errors, warnings = [], []
    ad = plan.get("art_direction") or {}
    shots = plan.get("shots") or []
    n = len(shots)
    if not ad:
        errors.append("art_direction 缺失：先读懂产品、买家，定视觉世界")
    if n == 0:
        errors.append("shots 为空")
        return errors, warnings, {}

    # atmosphere
    atm = ad.get("atmosphere") or {}
    typ = atm.get("type")
    if typ not in TYPES:
        errors.append("art_direction.atmosphere.type 必须是 occasion_led / lifestyle_led / proof_led")
        typ = "proof_led"
    if typ != "proof_led":
        moment = str(atm.get("the_moment") or "")
        if len(moment) < 12:
            errors.append("atmosphere.the_moment 太短：要有时间、人、正在发生的事，不是「产品挂在墙上」")
        if len(atm.get("signals") or []) < 6:
            errors.append("atmosphere.signals 至少列 6 样具体的场合信号（现在 %d 样）" % len(atm.get("signals") or []))
        if not atm.get("product_state"):
            errors.append("atmosphere.product_state 缺失：产品在那一幕里是装满、戴着、点着还是成套")
        if not atm.get("life_trace"):
            errors.append("atmosphere.life_trace 缺失：人来过或正在场的痕迹")

    # scene levels
    key = "scene_level_actual" if actual else "scene_level"
    levels = []
    for i, s in enumerate(shots, 1):
        lv = str(s.get(key) or "").strip().upper()[:2]
        if lv not in LEVELS:
            errors.append("shot-%02d 缺 %s（L0 / L1 / L2 / L3）" % (i, key))
            lv = "L0"
        levels.append(LEVELS[lv])
    hero_min, l3_min, l23_min, first3_min = FLOORS[typ]
    l3_min, l23_min = scaled(l3_min, n), scaled(l23_min, n)
    l3, l23 = sum(1 for v in levels if v == 3), sum(1 for v in levels if v >= 2)
    if levels[0] < hero_min:
        errors.append("主图是 L%d，%s 产品的主图至少要 L%d：遮住产品也认得出场合和时刻" % (levels[0], typ, hero_min))
    if l3 < l3_min:
        errors.append("L3（完整一幕）只有 %d 张，至少要 %d 张" % (l3, l3_min))
    if l23 < l23_min:
        errors.append("L2 加 L3 只有 %d 张，至少要 %d 张；一面墙加一两件小道具是 L1，不算场景" % (l23, l23_min))
    if n >= 3 and sum(1 for v in levels[:3] if v == 3) < first3_min:
        errors.append("前三张里 L3 不足 %d 张：买家多数只看前三张" % first3_min)

    # warm occasions
    mood = str(ad.get("mood_profile") or "")
    context = " ".join(str(x) for x in (atm.get("the_moment"), ad.get("visual_world"), ad.get("library_entry"),
                                        (ad.get("product_reading") or {})))
    if typ == "occasion_led" and WARM_OCCASION.search(context) and mood != "warm_scene":
        if not ad.get("mood_profile_reason"):
            errors.append("暖场合（圣诞、秋冬、烛光、壁炉边）的主图和场景图默认 warm_scene；"
                          "坚持 true_color 要在 art_direction.mood_profile_reason 写理由")

    # composition
    codes = [comp_code(s.get("composition")) for s in shots]
    for i, c in enumerate(codes, 1):
        if not c:
            errors.append("shot-%02d 缺 composition 代号（A–M）" % i)
    known = [c for c in codes if c]
    if known:
        kinds_min, same_max = min(scaled(7, n), n), max(scaled(3, n), 1)
        if len(set(known)) < kinds_min:
            errors.append("构图只有 %d 种，至少要 %d 种" % (len(set(known)), kinds_min))
        for c in sorted(set(known)):
            if known.count(c) > same_max:
                errors.append("构图 %s 用了 %d 次，最多 %d 次" % (c, known.count(c), same_max))
        for i in range(1, len(codes)):
            if codes[i] and codes[i] == codes[i - 1]:
                errors.append("shot-%02d 和 shot-%02d 是同一种构图 %s，相邻两张要不同" % (i, i + 1, codes[i]))
    if len(ad.get("selling_points") or []) < 3:
        errors.append("art_direction.selling_points 至少 3 条，每条配证据和构图")

    # scale
    lock = ad.get("scale_lock")
    unverified = lock == "unverified" or (isinstance(lock, dict) and lock.get("real_size_cm") in (None, "unverified"))
    if not lock:
        errors.append("art_direction.scale_lock 缺失：真实尺寸、参照物、落点")
    elif unverified and l23 > 0:
        errors.append("没有可靠尺寸（scale_lock 为 unverified）时不能拍带参照物的场景；先拿到尺寸")

    # prompts
    for i, s in enumerate(shots, 1):
        text = prompt_text(s, base)
        if text is None:
            continue
        low = text.lower()
        hit = [w for w in BANNED if w in low]
        if hit:
            errors.append("shot-%02d 的 prompt 里有不该出现的词：%s" % (i, ", ".join(hit)))
        if levels[i - 1] >= 2 and not SIZE.search(text):
            errors.append("shot-%02d 是场景图，prompt 里没有尺度句（真实尺寸加相对关系）" % i)
        if levels[i - 1] >= 2 and "enlarge" not in low:
            warnings.append("shot-%02d 的 prompt 没有写 Do not enlarge the <product>" % i)

    summary = {"type": typ, "shots": n, "counted_field": key, "L3": l3, "L2_plus_L3": l23,
               "L0_L1": n - l23, "composition_types": len(set(known)), "mood_profile": mood}
    return errors, warnings, summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan", help="path to plan.codex-direct.json")
    ap.add_argument("--actual", action="store_true", help="count scene_level_actual from rendered images")
    ap.add_argument("--json", action="store_true", help="print JSON only")
    args = ap.parse_args(argv)
    path = Path(args.plan)
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(plan, dict):
            raise ValueError("plan must be a JSON object")
    except (OSError, ValueError) as exc:
        print("cannot read plan: %s" % exc, file=sys.stderr)
        return 64
    errors, warnings, summary = check(plan, path.parent, args.actual)
    status = "fail" if errors else "pass"
    if args.json:
        print(json.dumps({"status": status, "summary": summary, "errors": errors, "warnings": warnings},
                         ensure_ascii=False, indent=2))
    else:
        if summary:
            print("type=%(type)s shots=%(shots)d L3=%(L3)d L2+L3=%(L2_plus_L3)d L0/L1=%(L0_L1)d "
                  "composition_types=%(composition_types)d mood=%(mood_profile)s (%(counted_field)s)" % summary)
        for e in errors:
            print("FAIL  " + e)
        for w in warnings:
            print("warn  " + w)
        print("plan_check: " + status)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
