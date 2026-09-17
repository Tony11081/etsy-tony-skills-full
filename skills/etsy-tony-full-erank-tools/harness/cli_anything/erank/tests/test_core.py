from pathlib import Path

from cli_anything.erank.core.analyzers import (
    audit_listing,
    keyword_analysis,
    profit_calculator,
    rank_check,
    tag_report,
)
from cli_anything.erank.core.session import SessionStore
from cli_anything.erank.utils.data_io import load_listings


FIXTURES = Path(__file__).parent / "fixtures"


def test_keyword_analysis_finds_best_listing():
    listings = load_listings(FIXTURES / "listings.csv")
    result = keyword_analysis("crochet pattern", listings)
    assert result["metrics"]["competition"] >= 2
    assert result["top_listings"][0]["shop"] == "CozyCraftSupply"


def test_listing_audit_flags_draft_hygiene():
    listings = load_listings(FIXTURES / "listings.csv")
    draft = [item for item in listings if item.status == "draft"][0]
    result = audit_listing(draft)
    codes = {issue["code"] for issue in result["issues"]}
    assert "unused_tags" in codes
    assert "thin_description" in codes
    assert result["score"] < 80


def test_tag_report_aggregates_by_shop():
    listings = load_listings(FIXTURES / "listings.csv")
    result = tag_report(listings, shop="BrightMockupStudio")
    assert result["listing_count"] == 2
    assert any(row["tag"] == "wall art" for row in result["tags"])


def test_rank_check_returns_best_rank():
    listings = load_listings(FIXTURES / "listings.csv")
    result = rank_check("wall art", listings, shop="BrightMockupStudio")
    assert result["found"] is True
    assert result["best_rank"] == 1


def test_profit_calculator_basic_math():
    result = profit_calculator(price=25, item_cost=8, shipping_cost=4)
    assert result["profit"] > 10
    assert result["fees"]["transaction_fee"] == 1.62


def test_session_undo_redo(tmp_path):
    store = SessionStore(tmp_path / "session.json")
    store.begin("set config")
    store.config()["etsy_api_key"] = "abc123"
    store.save()
    assert store.config()["etsy_api_key"] == "abc123"
    undo = store.undo()
    assert undo["ok"] is True
    assert "etsy_api_key" not in store.config()
    redo = store.redo()
    assert redo["ok"] is True
    assert store.config()["etsy_api_key"] == "abc123"
