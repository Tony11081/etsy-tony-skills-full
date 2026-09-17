import importlib.util
import json
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "clawlist_optimize.py"
SPEC = importlib.util.spec_from_file_location("clawlist_optimize", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class HandbookKnowledgeBaseTests(unittest.TestCase):
    def test_database_count_and_english_context(self):
        request = {
            "task": "standard_diagnosis",
            "product": {
                "title": "Personalized Wedding Cake Topper",
                "description": "Custom name decoration for a wedding cake",
            },
            "confirmed_claims": ["personalized"],
            "images": [],
        }
        context, metadata = MODULE.load_handbook_context(request)
        self.assertTrue(metadata["loaded"])
        self.assertEqual(metadata["documents"], 945)
        self.assertGreater(len(metadata["hits"]), 0)
        self.assertIn("https://www.etsy.com/seller-handbook/article/", context)
        self.assertIn("ETSY SELLER HANDBOOK KNOWLEDGE BASE HITS", MODULE.system_prompt(
            request["task"], context
        ))

    def test_chinese_topic_alias_search(self):
        request = {
            "task": "full_description",
            "product": "需要优化物流、运费和发货说明",
            "confirmed_claims": [],
            "images": [],
        }
        _, metadata = MODULE.load_handbook_context(request)
        categories = {
            category
            for hit in metadata["hits"]
            for category in hit["categories"]
        }
        self.assertIn("Shipping", categories)

    def test_initialize_does_not_load_database(self):
        context, metadata = MODULE.load_handbook_context(
            {"task": "initialize", "product": {}, "confirmed_claims": [], "images": []}
        )
        self.assertEqual(context, "")
        self.assertFalse(metadata["loaded"])
        self.assertEqual(metadata["documents"], 0)

    def test_run_optimizer_reports_exact_handbook_hits_without_network(self):
        request = {
            "task": "standard_diagnosis",
            "product": {"title": "Blue Wedding Cake Topper"},
            "confirmed_claims": [],
            "images": [],
        }
        model_result = {
            "title_seo_diagnosis": {"score": 7, "findings": ["标题可读。"]},
            "optimized_titles": [
                "Blue Wedding Cake Topper for Reception Decor",
                "Wedding Cake Topper in Blue for Reception",
                "Blue Cake Decoration for Wedding Reception",
            ],
            "tags": [
                "cake topper",
                "wedding decor",
                "blue cake decor",
                "reception decor",
                "cake decoration",
                "wedding topper",
                "blue wedding",
                "party cake decor",
                "bridal decor",
                "cake accessory",
                "wedding cake",
                "table decor",
                "celebration decor",
            ],
            "visual_advice": ["展示正面比例。"],
            "description_cro_diagnosis": {"score": 7, "findings": ["开头需更清晰。"]},
            "description_opening": [
                "A blue silhouette gives this wedding cake a crisp focal point.",
                "Designed for a clean and memorable reception display.",
                "A simple accent for wedding and celebration cakes.",
            ],
            "full_description": None,
            "competitive_strategy": ["强调颜色与婚礼用途。"],
            "information_to_confirm": ["请确认尺寸。"],
            "assumptions": ["未假设材质。"],
        }
        fake_response = {
            "model": "gemini-test",
            "choices": [
                {
                    "message": {"content": json.dumps(model_result, ensure_ascii=False)},
                    "finish_reason": "stop",
                }
            ],
            "usage": {},
        }
        with mock.patch.object(MODULE, "call_api", return_value=fake_response):
            result = MODULE.run_optimizer(request, "not-a-real-key", "gemini-test", 10)
        handbook = result["_meta"]["seller_handbook_knowledge_base"]
        self.assertTrue(handbook["loaded"])
        self.assertEqual(handbook["documents"], 945)
        self.assertGreater(len(handbook["hits"]), 0)


if __name__ == "__main__":
    unittest.main()
