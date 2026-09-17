#!/usr/bin/env python3
"""Validate a competitor-informed Etsy 15-photo campaign plan."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


MANDATORY_PROMPT = """我是etsy卖家，根据我提供的产品图，帮我生成15张符合etsy顾客喜欢的产品图，镜头需要有近有远，有大有小，整体要有生活气息，图片需包含产品展示，产品细节展示，产品尺寸效果图，尺寸图不的随意修改和线条叠加错乱，人物使用效果展示，生成时注意产品摆放角度和场景图需多样化，不的集中在某一角度和某一场景展示，你是资深的
etsy产品设计师，发挥你的设计才能开始设计吧"""

ALLOWED_REFERENCE_TYPES = {
    "seller_product",
    "supplier_product_permitted",
    "seller_measurement",
    "seller_logo",
    "seller_packaging",
}
PRODUCT_REFERENCE_TYPES = {"seller_product", "supplier_product_permitted"}
ALLOWED_DELTA_AXES = {
    "environment",
    "prop_family",
    "camera",
    "lighting",
    "palette",
    "product_placement",
    "product_state",
    "human_action",
}
SCENE_FLOORS = {"experience_led": 8, "balanced": 5, "proof_led": 3}


def nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def normalized(value: str) -> str:
    return " ".join(value.casefold().split())


def validate(plan: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(plan, dict):
        return ["plan must be a JSON object"]

    if plan.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")
    if plan.get("mandatory_user_prompt") != MANDATORY_PROMPT:
        errors.append("mandatory_user_prompt must exactly match etsy-tony-full-photo-15")

    tier = plan.get("scene_capacity_tier")
    if tier not in SCENE_FLOORS:
        errors.append("scene_capacity_tier must be experience_led, balanced, or proof_led")

    product = plan.get("product")
    if not isinstance(product, dict):
        errors.append("product must be an object")
    else:
        if not nonempty_text(product.get("product_id")):
            errors.append("product.product_id is required")
        if product.get("source_classification") not in {
            "real_product_supported",
            "permitted_pod_mockup_supported",
            "concept_only",
        }:
            errors.append("product.source_classification is missing or unsupported")
        paths = product.get("product_reference_paths")
        if not isinstance(paths, list) or not paths or not all(nonempty_text(p) for p in paths):
            errors.append("product.product_reference_paths must contain permitted product references")

    competitors = plan.get("competitor_evidence")
    if not isinstance(competitors, list):
        errors.append("competitor_evidence must be a list")
        competitors = []
    if not 3 <= len(competitors) <= 5:
        errors.append("competitor_evidence must contain 3 to 5 core listings")

    listing_ids: set[str] = set()
    urls: set[str] = set()
    shops: set[str] = set()
    for index, item in enumerate(competitors, start=1):
        prefix = f"competitor_evidence[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        listing_id = item.get("listing_id")
        if not nonempty_text(listing_id):
            errors.append(f"{prefix}.listing_id is required")
        elif normalized(listing_id) in listing_ids:
            errors.append(f"{prefix}.listing_id is duplicated")
        else:
            listing_ids.add(normalized(listing_id))
        url = item.get("url")
        if not nonempty_text(url) or not url.startswith(("https://", "http://")):
            errors.append(f"{prefix}.url must be a public URL")
        elif normalized(url) in urls:
            errors.append(f"{prefix}.url is duplicated")
        else:
            urls.add(normalized(url))
        shop_id = item.get("shop_id")
        if not nonempty_text(shop_id):
            errors.append(f"{prefix}.shop_id is required")
        else:
            shops.add(normalized(shop_id))
        if not nonempty_text(item.get("accessed_at")):
            errors.append(f"{prefix}.accessed_at is required")
        if item.get("tier") != "core" or not isinstance(item.get("score"), (int, float)) or item["score"] < 80:
            errors.append(f"{prefix} must be a core competitor scoring at least 80")
        if item.get("same_core_product") is not True:
            errors.append(f"{prefix}.same_core_product must be true")
        if item.get("same_primary_buyer_need") is not True:
            errors.append(f"{prefix}.same_primary_buyer_need must be true")
        observations = item.get("scene_observations")
        if not isinstance(observations, list) or not observations:
            errors.append(f"{prefix}.scene_observations must not be empty")

    if len(competitors) >= 3 and len(shops) < 2:
        errors.append("core competitor evidence must cover at least two shops")

    shots = plan.get("shots")
    if not isinstance(shots, list):
        errors.append("shots must be a list")
        shots = []
    if len(shots) != 15:
        errors.append("shots must contain exactly 15 records")

    shot_ids: set[str] = set()
    buyer_questions: set[str] = set()
    scene_flags: list[bool] = []
    has_dimension_proof = False
    for index, shot in enumerate(shots, start=1):
        prefix = f"shots[{index}]"
        if not isinstance(shot, dict):
            errors.append(f"{prefix} must be an object")
            scene_flags.append(False)
            continue
        shot_id = shot.get("shot_id")
        if not nonempty_text(shot_id):
            errors.append(f"{prefix}.shot_id is required")
        elif normalized(shot_id) in shot_ids:
            errors.append(f"{prefix}.shot_id is duplicated")
        else:
            shot_ids.add(normalized(shot_id))
        role = shot.get("role")
        if not nonempty_text(role):
            errors.append(f"{prefix}.role is required")
        question = shot.get("buyer_question")
        if not nonempty_text(question):
            errors.append(f"{prefix}.buyer_question is required")
        elif normalized(question) in buyer_questions:
            errors.append(f"{prefix}.buyer_question must be distinct")
        else:
            buyer_questions.add(normalized(question))

        scene_bearing = shot.get("scene_bearing")
        if not isinstance(scene_bearing, bool):
            errors.append(f"{prefix}.scene_bearing must be true or false")
            scene_bearing = False
        scene_flags.append(scene_bearing)

        refs = shot.get("generation_references")
        if not isinstance(refs, list) or not refs:
            errors.append(f"{prefix}.generation_references must not be empty")
        else:
            shot_reference_types: set[str] = set()
            for ref_index, ref in enumerate(refs, start=1):
                ref_prefix = f"{prefix}.generation_references[{ref_index}]"
                if not isinstance(ref, dict):
                    errors.append(f"{ref_prefix} must be an object")
                    continue
                if ref.get("source_type") not in ALLOWED_REFERENCE_TYPES:
                    errors.append(f"{ref_prefix}.source_type is forbidden or unknown")
                else:
                    shot_reference_types.add(ref["source_type"])
                if not nonempty_text(ref.get("path")):
                    errors.append(f"{ref_prefix}.path is required")
            if not shot_reference_types.intersection(PRODUCT_REFERENCE_TYPES):
                errors.append(f"{prefix}.generation_references needs a permitted product-image reference")

        forbidden_keys = {
            key
            for key in shot
            if "competitor" in key.casefold()
            and any(token in key.casefold() for token in ("path", "image", "reference", "input"))
        }
        for key in forbidden_keys:
            if shot.get(key):
                errors.append(f"{prefix}.{key} must be empty; competitor images are never generation inputs")

        if nonempty_text(role) and "dimension" in role.casefold():
            if shot.get("deterministic_overlay") is True:
                has_dimension_proof = True
            else:
                errors.append(f"{prefix} dimension role must set deterministic_overlay=true")

        if scene_bearing:
            translation = shot.get("scene_translation")
            if not isinstance(translation, dict):
                errors.append(f"{prefix}.scene_translation is required for a scene-bearing shot")
                continue
            if not isinstance(translation.get("evidence_sources"), list) or not translation["evidence_sources"]:
                errors.append(f"{prefix}.scene_translation.evidence_sources must not be empty")
            for field in ("abstract_principle", "product_truth_source"):
                if not nonempty_text(translation.get(field)):
                    errors.append(f"{prefix}.scene_translation.{field} is required")
            axes = translation.get("creative_delta_axes")
            if not isinstance(axes, list):
                errors.append(f"{prefix}.scene_translation.creative_delta_axes must be a list")
            else:
                unique_axes = {axis for axis in axes if isinstance(axis, str) and axis in ALLOWED_DELTA_AXES}
                if len(unique_axes) < 3:
                    errors.append(f"{prefix}.scene_translation needs at least three valid creative delta axes")
                unknown_axes = {
                    str(axis)
                    for axis in axes
                    if not isinstance(axis, str) or axis not in ALLOWED_DELTA_AXES
                }
                if unknown_axes:
                    errors.append(f"{prefix}.scene_translation has unknown axes: {sorted(unknown_axes)}")
            avoid = translation.get("competitor_elements_to_avoid")
            if not isinstance(avoid, list) or not avoid:
                errors.append(f"{prefix}.scene_translation.competitor_elements_to_avoid must not be empty")

    if tier in SCENE_FLOORS:
        scene_count = sum(scene_flags)
        if scene_count < SCENE_FLOORS[tier]:
            errors.append(f"{tier} requires at least {SCENE_FLOORS[tier]} scene-bearing shots")
        if tier == "experience_led":
            if sum(scene_flags[:5]) < 2:
                errors.append("experience_led requires at least two scene-bearing shots among the first five")
            if any(not any(scene_flags[i : i + 3]) for i in range(max(0, len(scene_flags) - 2))):
                errors.append("experience_led may not contain more than two consecutive non-scene shots")

    if not has_dimension_proof:
        errors.append("at least one deterministic dimension-proof shot is required")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_scene_plan.py <plan.json>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: cannot read plan: {exc}", file=sys.stderr)
        return 2
    errors = validate(plan)
    if errors:
        print(f"INVALID: {len(errors)} error(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALID: competitor evidence, originality translation, 15-shot structure, and reference isolation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
