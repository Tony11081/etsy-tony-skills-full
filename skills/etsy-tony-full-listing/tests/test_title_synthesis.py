import copy
import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "clawlist_optimize.py"
SPEC = importlib.util.spec_from_file_location("clawlist_optimize_titles", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


COMPETITOR_TITLES = [
    "Gold Mirror Acrylic Wedding Cake Topper, Custom Initials",
    "Wedding Monogram Cake Charm, Gold Acrylic Side Decor",
    "Personalized Initials Wedding Cake Topper",
]


def competitor_record(index, title, tier="core"):
    if tier == "core":
        breakdown = {
            "core_product": 30,
            "buyer_need": 20,
            "structure_or_mounting": 15,
            "personalization_or_variant": 15,
            "material_or_process": 5,
            "style_or_use_case": 5,
        }
    else:
        breakdown = {
            "core_product": 30,
            "buyer_need": 20,
            "structure_or_mounting": 5,
            "personalization_or_variant": 5,
            "material_or_process": 5,
            "style_or_use_case": 5,
        }
    return {
        "url": f"https://www.etsy.com/listing/{index}",
        "title": title,
        "accessed_at": "2026-08-02T12:00:00+08:00",
        "tier": tier,
        "match_score": sum(breakdown.values()),
        "score_breakdown": breakdown,
        "hard_gate": {
            "same_core_product": True,
            "same_primary_buyer_need": True,
        },
        "match_reasons": ["Same physical product and wedding buyer need."],
        "mismatches": [],
    }


REQUEST = {
    "task": "standard_diagnosis",
    "product": {
        "supplied_title": "Custom Monogram Wedding Cake Topper",
        "seller_facts": {"material": "acrylic", "finish": "gold mirror"},
        "competitor_evidence": [
            competitor_record(index, title) for index, title in enumerate(COMPETITOR_TITLES, 1)
        ],
    },
    "confirmed_claims": [],
    "images": [],
}


def valid_result():
    return {
        "title_seo_diagnosis": {"score": 8, "findings": ["组合了竞品语言。"]},
        "optimized_titles": [
            "Gold Mirror Wedding Cake Topper with Custom Acrylic Initials",
            "Custom Wedding Monogram Cake Charm with Gold Acrylic Initials",
            "Personalized Gold Initials Side Cake Decor for Wedding",
        ],
        "tags": [
            "wedding cake topper",
            "acrylic cake topper",
            "mirror acrylic",
            "laser cut charm",
            "wedding monogram",
            "gold cake topper",
            "wedding initials",
            "cake initials",
            "cake letters",
            "initials topper",
            "monogram topper",
            "custom initials",
            "side cake topper",
        ],
        "visual_advice": ["展示正面效果。"],
        "description_cro_diagnosis": {"score": 8, "findings": ["开场具体。"]},
        "description_opening": [
            "Two gold initials frame a center divider on the wedding cake.",
            "Mirror acrylic reflects the surrounding reception light.",
            "Three separate pieces create a clean monogram arrangement.",
        ],
        "full_description": None,
        "competitive_strategy": ["强调镜面字母。"],
        "information_to_confirm": ["请确认尺寸。"],
        "assumptions": ["未假设尺寸。"],
    }


class TitleSynthesisTests(unittest.TestCase):
    def test_accepts_titles_combined_from_multiple_competitors(self):
        MODULE.validate_listing(valid_result(), REQUEST)

    def test_rejects_complete_competitor_title_copy(self):
        result = valid_result()
        result["optimized_titles"][0] = COMPETITOR_TITLES[0]
        with self.assertRaisesRegex(MODULE.OptimizerError, "must not copy"):
            MODULE.validate_listing(result, REQUEST)

    def test_rejects_title_without_multiple_competitor_sources(self):
        result = valid_result()
        result["optimized_titles"][0] = "Botanical Table Number Sign for Dinner"
        with self.assertRaisesRegex(MODULE.OptimizerError, "at least two competitor titles"):
            MODULE.validate_listing(result, REQUEST)

    def test_rejects_adjacent_title_as_core_title_source(self):
        request = copy.deepcopy(REQUEST)
        request["product"]["competitor_evidence"].append(
            competitor_record(4, "Botanical Acrylic Table Number Sign for Dinner", "adjacent")
        )
        result = valid_result()
        result["optimized_titles"][0] = "Botanical Acrylic Table Number Sign for Dinner Reception"
        with self.assertRaisesRegex(MODULE.OptimizerError, "at least two competitor titles"):
            MODULE.validate_listing(result, request)

    def test_rejects_score_tier_mismatch(self):
        request = copy.deepcopy(REQUEST)
        request["product"]["competitor_evidence"][0]["tier"] = "adjacent"
        with self.assertRaisesRegex(MODULE.OptimizerError, "tier must be core"):
            MODULE.validate_listing(valid_result(), request)

    def test_rejects_fewer_than_three_core_competitors(self):
        request = copy.deepcopy(REQUEST)
        request["product"]["competitor_evidence"] = request["product"]["competitor_evidence"][:2]
        with self.assertRaisesRegex(MODULE.OptimizerError, "3-5 core competitors"):
            MODULE.validate_listing(valid_result(), request)

    def test_rejects_hard_gate_failure(self):
        request = copy.deepcopy(REQUEST)
        request["product"]["competitor_evidence"][0]["hard_gate"]["same_core_product"] = False
        with self.assertRaisesRegex(MODULE.OptimizerError, "failed the mandatory competitor hard gate"):
            MODULE.validate_listing(valid_result(), request)


if __name__ == "__main__":
    unittest.main()
