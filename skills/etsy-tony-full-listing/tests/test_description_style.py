import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "clawlist_optimize.py"
SPEC = importlib.util.spec_from_file_location("clawlist_optimize_description", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def valid_result():
    opening = [
        "Two gold mirror initials frame a slim center divider on the cake.",
        "Laser-cut acrylic reflects the surrounding reception light.",
        "Three separate pieces allow front or side cake placement.",
    ]
    return {
        "title_seo_diagnosis": {"score": 8, "findings": ["标题具体。"]},
        "optimized_titles": [
            "Gold Mirror Initials Wedding Cake Topper",
            "Custom Monogram Acrylic Cake Charm",
            "Laser Cut Wedding Initials Cake Decor",
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
        "visual_advice": ["展示三个独立部件。"],
        "description_cro_diagnosis": {"score": 8, "findings": ["事实完整。"]},
        "description_opening": opening,
        "full_description": "\n".join(
            opening
            + [
                "",
                "📝 Product Details",
                "• Material: Acrylic",
                "",
                "📐 Dimensions",
                "• Overall size: 10 cm x 10 cm x 3 mm",
                "",
                "🎂 Confirmed Uses",
                "• Wedding cakes",
                "",
                "🚚 Shipping & Processing",
                "• Processing time: 1-3 days",
            ]
        ),
        "competitive_strategy": ["强调镜面字母。"],
        "information_to_confirm": ["无。"],
        "assumptions": ["无。"],
    }


REQUEST = {
    "task": "full_description",
    "product": {
        "supplied_title": "Gold Mirror Wedding Cake Topper",
        "seller_facts": {
            "material": "acrylic",
            "confirmed_uses": "wedding cakes and wedding receptions",
        },
    },
    "confirmed_claims": [],
    "images": [],
}


class DescriptionStyleTests(unittest.TestCase):
    def test_rejects_boilerplate_opening(self):
        result = valid_result()
        boilerplate = "Add a personalized touch to your wedding cake."
        result["description_opening"][0] = boilerplate
        result["full_description"] = result["full_description"].replace(
            "Two gold mirror initials frame a slim center divider on the cake.", boilerplate, 1
        )
        with self.assertRaisesRegex(MODULE.OptimizerError, "boilerplate"):
            MODULE.validate_listing(result, REQUEST)

    def test_rejects_missing_icon_sections(self):
        result = valid_result()
        for icon in ("📐", "🎂", "🚚"):
            result["full_description"] = result["full_description"].replace(icon, "")
        with self.assertRaisesRegex(MODULE.OptimizerError, "at least 4"):
            MODULE.validate_listing(result, REQUEST)

    def test_rejects_placeholder_text(self):
        result = valid_result()
        result["full_description"] += "\n[Packaged weight to be confirmed]"
        with self.assertRaisesRegex(MODULE.OptimizerError, "placeholder"):
            MODULE.validate_listing(result, REQUEST)

    def test_rejects_unconfirmed_care_instructions(self):
        result = valid_result()
        result["full_description"] += "\n\n🧼 Care Instructions\nWipe with a soft damp cloth."
        with self.assertRaisesRegex(MODULE.OptimizerError, "care instructions"):
            MODULE.validate_listing(result, REQUEST)

    def test_rejects_unconfirmed_occasion(self):
        result = valid_result()
        result["full_description"] += "\n• Also suitable for anniversary cakes."
        with self.assertRaisesRegex(MODULE.OptimizerError, "unconfirmed occasion"):
            MODULE.validate_listing(result, REQUEST)

    def test_rejects_unconfirmed_mounting_effect(self):
        result = valid_result()
        result["full_description"] += "\n• Invisible stakes create a floating effect."
        with self.assertRaisesRegex(MODULE.OptimizerError, "mounting or readiness"):
            MODULE.validate_listing(result, REQUEST)

    def test_accepts_product_specific_icon_description(self):
        MODULE.validate_listing(valid_result(), REQUEST)


if __name__ == "__main__":
    unittest.main()
