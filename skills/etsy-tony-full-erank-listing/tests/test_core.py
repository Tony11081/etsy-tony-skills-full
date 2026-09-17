from __future__ import annotations

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from normalize_erank_export import normalize_rows  # noqa: E402
from run_pipeline import determine_status, run_listing, validate_intent_result  # noqa: E402
from select_keyword_portfolio import rank_evidence  # noqa: E402
from validate_listing import validate_package  # noqa: E402


def valid_tags() -> list[str]:
    return [
        "rocking chair",
        "nursery rocker",
        "wood frame chair",
        "reading nook chair",
        "upholstered seat",
        "mid century chair",
        "accent rocker",
        "bedroom chair",
        "living room chair",
        "cozy reading chair",
        "modern nursery",
        "statement chair",
        "gentle rocking",
    ]


def valid_package() -> dict:
    tags = valid_tags()
    opening = [
        "Bring a grounded rust tone and gentle motion to your reading corner with this corduroy rocking chair.",
        "The upholstered seat and visible wood frame create a warm, tailored silhouette without looking bulky.",
        "Style it in a nursery, bedroom, or quiet reading nook where comfort and compact character both matter.",
    ]
    description = """Bring a grounded rust tone and gentle motion to your reading corner with this corduroy rocking chair.
The upholstered seat and visible wood frame create a warm, tailored silhouette without looking bulky.
Style it in a nursery, bedroom, or quiet reading nook where comfort and compact character both matter.

✨ Why You'll Love It
The rust corduroy texture adds depth and warmth, while the simple frame keeps the chair easy to coordinate with modern interiors.

🪑 Product Details
Wood frame, upholstered seat, and rust corduroy texture. Dimensions: [add dimensions].

🏡 Perfect For
Nurseries, reading nooks, bedrooms, and warm modern interiors.

🧽 Care Instructions
Use a soft dry cloth and follow the supplied fabric care guidance.

📦 Shipping & Processing
Processing time: 1-3 days
Shipping method: 3-7 days

ℹ️ Important Notes
Colors may vary slightly by screen. Confirm dimensions before ordering.
"""
    return {
        "listing": {
            "recommended_title": "Rust Corduroy Rocking Chair, Wood Frame Nursery Seat",
            "alternate_titles": [
                "Wood Frame Rocking Chair in Rust Corduroy",
                "Rust Upholstered Rocker, Modern Wood Frame Chair",
            ],
            "tags": tags,
            "tag_evidence": [
                {
                    "tag": tag,
                    "evidence_status": "ERANK_MEMBER_VERIFIED",
                    "matched_keyword": tag,
                    "intent": "product",
                    "rationale": "测试证据映射。",
                }
                for tag in tags
            ],
            "description_opening": opening,
            "full_description": description,
            "category_attribute_advice": ["选择最具体的 rocking chair 类目。"],
            "visual_advice": ["首图保持产品主体清晰。"],
        },
        "provenance": {"erank": {"authoritative_member_data": True}},
    }


class NormalizeTests(unittest.TestCase):
    def test_normalizes_member_rows_without_inventing_missing_metrics(self) -> None:
        result = normalize_rows(
            [
                {
                    "Keyword": "wood frame rocker",
                    "Average Searches": "1.2k",
                    "Average Clicks": "800",
                    "CTR": "66.7%",
                    "Etsy Competition": "24,000",
                },
                {"Keyword": "nursery rocker", "Average Searches": "N/A"},
            ],
            source="erank-member-export",
            market="US",
            fetched_at="2026-07-28T00:00:00Z",
            input_file="test.csv",
        )
        self.assertTrue(result["source"]["authoritative_member_data"])
        self.assertEqual(result["keywords"][0]["average_searches"], 1200.0)
        self.assertEqual(result["keywords"][0]["ctr"], 66.7)
        self.assertIsNone(result["keywords"][1]["average_searches"])

    def test_non_member_source_is_unverified(self) -> None:
        result = normalize_rows(
            [{"keyword": "rocking chair", "search volume": 100}],
            source="synthetic",
            market="US",
            fetched_at="2026-07-28T00:00:00Z",
        )
        self.assertFalse(result["source"]["authoritative_member_data"])
        self.assertEqual(result["keywords"][0]["evidence_status"], "UNVERIFIED")


class PortfolioTests(unittest.TestCase):
    def test_rejects_unsupported_high_volume_phrase(self) -> None:
        rows = []
        phrases = valid_tags() + ["leather glider"]
        for index, phrase in enumerate(phrases):
            rows.append(
                {
                    "phrase": phrase,
                    "average_searches": 10_000 if phrase == "leather glider" else 100 + index * 10,
                    "average_clicks": 5_000 if phrase == "leather glider" else 80 + index * 5,
                    "ctr": 70,
                    "competition": 20_000 - index * 100,
                    "trend": 1,
                    "intent": "product" if index < 3 else "room_use",
                    "search_stage": "consideration",
                    "product_relevance": "low" if phrase == "leather glider" else "high",
                    "fact_supported": phrase != "leather glider",
                    "evidence_status": "ERANK_MEMBER_VERIFIED",
                }
            )
        result = rank_evidence(
            {
                "source": {
                    "kind": "erank-member-export",
                    "market": "US",
                    "fetched_at": "2026-07-28T00:00:00Z",
                    "authoritative_member_data": True,
                },
                "keywords": rows,
            }
        )
        selected = {item["phrase"] for item in result["selected_tag_candidates"]}
        self.assertNotIn("leather glider", selected)
        rejected = {item["phrase"]: item["reason"] for item in result["rejected_keywords"]}
        self.assertEqual(rejected["leather glider"], "fact_or_relevance_not_confirmed")
        self.assertEqual(result["coverage"]["selected_tag_count"], 13)

    def test_missing_metrics_cannot_be_selected(self) -> None:
        result = rank_evidence(
            {
                "source": {
                    "kind": "erank-member-export",
                    "market": "US",
                    "fetched_at": "2026-07-28T00:00:00Z",
                    "authoritative_member_data": True,
                },
                "keywords": [
                    {
                        "phrase": "nursery rocker",
                        "average_searches": None,
                        "average_clicks": None,
                        "ctr": None,
                        "competition": None,
                        "product_relevance": "high",
                        "fact_supported": True,
                    }
                ],
            }
        )
        self.assertEqual(result["coverage"]["eligible_keyword_count"], 0)
        self.assertEqual(result["rejected_keywords"][0]["reason"], "missing_member_metrics")


class ListingValidationTests(unittest.TestCase):
    def test_valid_package(self) -> None:
        result = validate_package(valid_package(), {"category": "Rocking Chairs", "attributes": {}})
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["checks"]["tag_count"], 13)

    def test_unconfirmed_glider_is_rejected(self) -> None:
        package = valid_package()
        package["listing"]["recommended_title"] = "Rust Corduroy Glider Chair, Wood Frame Nursery Seat"
        result = validate_package(package, {})
        self.assertFalse(result["valid"])
        self.assertTrue(any("glider" in error for error in result["errors"]))

    def test_member_hypothesis_cannot_be_final_tag_evidence(self) -> None:
        package = valid_package()
        package["listing"]["tag_evidence"][0]["evidence_status"] = "GEMINI_HYPOTHESIS"
        result = validate_package(package, {})
        self.assertFalse(result["valid"])
        self.assertTrue(any("Invalid evidence status" in error for error in result["errors"]))

    def test_description_requires_icon_led_sections(self) -> None:
        package = valid_package()
        package["listing"]["full_description"] = package["listing"]["full_description"].replace(
            "✨ Why You'll Love It", "Why You'll Love It"
        )
        result = validate_package(package, {})
        self.assertFalse(result["valid"])
        self.assertTrue(any("leading icon" in error for error in result["errors"]))

    def test_generic_cake_topper_boilerplate_is_rejected(self) -> None:
        package = valid_package()
        forbidden = "Add an elegant finishing touch to your celebratory cake with a custom laser-cut acrylic cake topper."
        package["listing"]["description_opening"][0] = forbidden
        package["listing"]["full_description"] = package["listing"]["full_description"].replace(
            package["listing"]["full_description"].splitlines()[0], forbidden, 1
        )
        result = validate_package(package, {})
        self.assertFalse(result["valid"])
        self.assertTrue(any("prohibited generic cake-topper boilerplate" in error for error in result["errors"]))


class PipelineHelperTests(unittest.TestCase):
    def test_intent_schema(self) -> None:
        candidates = [
            {
                "phrase": f"rocker phrase {index}",
                "intent": "product",
                "search_stage": "consideration",
                "product_relevance": "high",
                "fact_supported": True,
                "rationale": "测试。",
                "evidence_status": "GEMINI_HYPOTHESIS",
            }
            for index in range(5)
        ]
        value = {
            "product_truth": {},
            "information_to_confirm": [],
            "assumptions": [],
            "search_intent_candidates": candidates,
        }
        self.assertEqual(validate_intent_result(value), [])

    def test_success_requires_fresh_member_evidence_and_audit(self) -> None:
        now = datetime.now(timezone.utc).isoformat()
        request = {"member_listing_audit": {"complete": True, "verified": True}, "current_listing": {}}
        source = {"authoritative_member_data": True, "fetched_at": now}
        status = determine_status(request, source, {"valid": True}, [], False)
        self.assertEqual(status, "VERIFIED_SUCCESS")

    def test_offline_full_pipeline_with_mocked_gemini(self) -> None:
        tags = valid_tags()
        package = valid_package()

        class FakeClient:
            def generate_json(self, *, stage, payload, **kwargs):
                meta = {"stage": stage, "provider": "mock", "validated": True}
                if stage == "intent":
                    return (
                        {
                            "product_truth": {
                                "product_type": "rocking chair",
                                "confirmed_objective_traits": ["rust orange", "corduroy", "wood frame"],
                                "visible_observations": [],
                                "supported_use_cases": ["nursery", "reading nook"],
                                "supported_customization": [],
                                "unsupported_or_unknown_claims": [],
                            },
                            "information_to_confirm": [],
                            "assumptions": [],
                            "search_intent_candidates": [
                                {
                                    "phrase": phrase,
                                    "intent": "product",
                                    "search_stage": "consideration",
                                    "product_relevance": "high",
                                    "fact_supported": True,
                                    "rationale": "测试。",
                                    "evidence_status": "GEMINI_HYPOTHESIS",
                                }
                                for phrase in tags[:5]
                            ],
                        },
                        meta,
                    )
                if stage.startswith("evidence_annotation_"):
                    return (
                        {
                            "keyword_annotations": [
                                {
                                    "phrase": item["phrase"],
                                    "intent": "product",
                                    "search_stage": "consideration",
                                    "product_relevance": "high",
                                    "fact_supported": True,
                                    "rationale": "测试。",
                                    "rejection_reason": "",
                                }
                                for item in payload["keywords"]
                            ],
                            "portfolio_reasoning": ["测试排序。"],
                        },
                        meta,
                    )
                if stage == "listing_copy":
                    return (
                        {
                            "listing": package["listing"],
                            "rejected_keywords": [],
                            "information_to_confirm": [],
                            "assumptions": [],
                            "measurement_plan": ["保存上线前基线并在获得足够曝光后复核。"],
                        },
                        meta,
                    )
                if stage == "quality_review":
                    return (
                        {
                            "approved": True,
                            "issues": [],
                            "corrected_listing": package["listing"],
                        },
                        meta,
                    )
                raise AssertionError(stage)

        now = datetime.now(timezone.utc).isoformat()
        evidence = {
            "source": {
                "kind": "erank-member-export",
                "market": "US",
                "fetched_at": now,
                "authoritative_member_data": True,
            },
            "keywords": [
                {
                    "phrase": tag,
                    "average_searches": 2000 - index * 80,
                    "average_clicks": 1600 - index * 60,
                    "ctr": 80 - index,
                    "competition": 25000 + index * 500,
                    "trend": 1,
                    "evidence_status": "ERANK_MEMBER_VERIFIED",
                }
                for index, tag in enumerate(tags)
            ],
            "integrity": {},
        }
        request = {
            "market": "US",
            "shop_language": "en-US",
            "product": {"product_type": "rocking chair"},
            "category": "Rocking Chairs",
            "attributes": {},
            "confirmed_claims": [],
            "images": [],
            "current_listing": {},
            "shop_stats": {},
            "prohibited_terms": [],
            "member_listing_audit": {"complete": True, "verified": True},
        }
        result = run_listing(FakeClient(), request, evidence, batch_size=40, max_keywords=200)
        self.assertEqual(result["status"], "VERIFIED_SUCCESS")
        self.assertTrue(result["quality_review"]["validator"]["valid"])
        self.assertEqual(len(result["listing"]["tags"]), 13)


if __name__ == "__main__":
    unittest.main()
