# Competitor Scene Learning Schema

Use this schema to convert public competitor observations into original scene direction without using competitor images as generation inputs.

## Combined Plan Shape

The validator expects one JSON object with these top-level fields:

```json
{
  "schema_version": "1.0",
  "mandatory_user_prompt": "<exact prompt required by etsy-tony-full-photo-15>",
  "scene_capacity_tier": "experience_led",
  "product": {
    "product_id": "seller-stable-id",
    "source_classification": "real_product_supported",
    "product_reference_paths": ["./product-input/product-front.png"],
    "confirmed_facts": [],
    "unknowns": []
  },
  "competitor_evidence": [],
  "shots": []
}
```

The plan is a pre-generation contract. Keep final audit results in the output artifacts required by the parent photo skill.

## Competitor Evidence Record

Retain 3–5 core listings. Each record should contain:

```json
{
  "listing_id": "c01",
  "shop_id": "public-shop-name-or-stable-label",
  "url": "https://www.etsy.com/listing/...",
  "accessed_at": "2026-09-01T12:00:00+08:00",
  "visible_title": "Visible public title",
  "score": 86,
  "tier": "core",
  "same_core_product": true,
  "same_primary_buyer_need": true,
  "matches": [],
  "mismatches": [],
  "scene_observations": [
    {
      "image_index": 2,
      "scene_class": "contextual lifestyle",
      "buyer_question": "How large does it look in a furnished room?",
      "environment_anchor": "reading corner",
      "depth_layers": ["chair edge", "product", "wall and window"],
      "product_contact": "supported by the visible floor",
      "camera": "eye-level medium-wide",
      "lighting": "neutral side daylight",
      "human_mode": "none",
      "prop_jobs": ["chair establishes scale"],
      "overlay_function": "none",
      "strength": "clear room-scale proof",
      "risks": []
    }
  ]
}
```

Use URLs and written observations as evidence. Do not add a local competitor image path, screenshot path, thumbnail path, or image-generation reference.

## Pattern Aggregation

Create `competitor-scene-patterns.json` with:

- `recurrent_patterns`: pattern, listings observed, shops observed, buyer question, confidence, and risk;
- `single_listing_ideas`: source and why it is not a category pattern;
- `market_gaps`: missing buyer question, evidence, and original opportunity;
- `risk_patterns`: misleading or low-quality conventions to avoid.

Mark a pattern `recurrent` only when at least two independent shops support it. Popularity is not permission to reproduce a specific execution.

## Shot Record

The combined plan must contain exactly 15 shot records:

```json
{
  "shot_id": "shot-04",
  "role": "room-scale proof",
  "buyer_question": "Will this fit visually beside a reading chair?",
  "scene_bearing": true,
  "deterministic_overlay": false,
  "generation_references": [
    {
      "path": "./product-input/product-front.png",
      "source_type": "seller_product"
    }
  ],
  "scene_translation": {
    "evidence_sources": ["c01#image-2", "c03#image-4"],
    "abstract_principle": "Use a familiar seat to establish human scale",
    "product_truth_source": "seller reference front view and confirmed dimensions",
    "creative_delta_axes": ["environment", "camera", "prop_family"],
    "competitor_elements_to_avoid": ["the observed chair model", "the observed wall layout"]
  }
}
```

Every shot needs a distinct buyer question. Every scene-bearing shot needs a translation record. A dimension-proof shot must set `deterministic_overlay` to `true` and use confirmed values.

Allowed `source_type` values are:

- `seller_product`;
- `supplier_product_permitted`;
- `seller_measurement`;
- `seller_logo`;
- `seller_packaging`.

Any competitor image, screenshot, crop, thumbnail, or derivative is forbidden as a generation reference.
Every shot must include at least one `seller_product` or `supplier_product_permitted` reference so the product itself remains visually locked.

## Originality Axes

For each scene-bearing shot, change at least three of these axes while preserving product truth:

- `environment`;
- `prop_family`;
- `camera`;
- `lighting`;
- `palette`;
- `product_placement`;
- `product_state` when source-supported;
- `human_action`.

Changing only colors or swapping one prop is insufficient. Reject a direction that keeps the same environment, prop family, camera family, lighting logic, and product placement as a competitor observation.

## Acceptance Checklist

- 3–5 independently opened core competitors; fewer than three keeps the competitor-informed scene plan blocked after one bounded expansion;
- no competitor image files or implicit recent-image inputs in generation;
- exactly 15 distinct shot roles and buyer questions;
- scene coverage satisfies the parent skill's tier floor and sequencing rules;
- every scene-bearing shot has evidence, an abstract principle, product-truth support, three or more creative deltas, and explicit avoidances;
- at least one deterministic dimension-proof shot;
- no brand, trademark, distinctive artwork, exact room layout, exact prop cluster, or copied overlay language;
- all parent photo-skill fidelity, contact-sheet, and publication-readiness audits remain required.
