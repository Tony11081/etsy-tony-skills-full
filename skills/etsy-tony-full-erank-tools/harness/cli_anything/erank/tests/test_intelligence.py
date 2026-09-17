from datetime import date, datetime, timedelta, timezone
import json

import pytest
from PIL import Image, ImageDraw

from cli_anything.erank.core.intelligence import (
    analyze_image_file,
    breakout_radar,
    change_impact,
    cluster_listings,
    cro_audit,
    cross_market_validation,
    detect_anomalies,
    fact_gated_draft,
    keyword_portfolio,
    opportunity_engine,
    seasonal_plan,
    true_profit,
    watchlist_alerts,
)
from cli_anything.erank.core.models import Listing
from cli_anything.erank.utils.live_sources import fetch_erank_shop_info, fetch_erank_shop_listings
from cli_anything.erank.utils.member_data import evidence_report, member_request_plan, merge_member_pages


def listing(listing_id: str, title: str, *, category: str = "", tags=None, sales=0, views=0, price=20, image_count=5):
    return Listing(
        listing_id=listing_id,
        shop="DemoShop",
        title=title,
        description="Confirmed product description " * 20,
        category=category,
        tags=tags or [],
        sales=sales,
        views=views,
        price=price,
        image_count=image_count,
    )


def test_member_ingest_proves_complete_and_reports_missing_pages(tmp_path):
    page1 = tmp_path / "page-1.json"
    page2 = tmp_path / "page-2.json"
    base = {
        "source": "erank-member-browser-api",
        "endpoint": "/api/top-sellers",
        "timeframe": "all-time",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
    page1.write_text(json.dumps({**base, "data": [{"shop_id": 1, "shop_name": "One"}], "meta": {"current_page": 1, "last_page": 2, "total": 2}}), encoding="utf-8")
    page2.write_text(json.dumps({**base, "data": [{"shop_id": 2, "shop_name": "Two"}], "meta": {"current_page": 2, "last_page": 2, "total": 2}}), encoding="utf-8")
    partial = merge_member_pages([page1])
    assert partial["result_status"] == "PARTIAL"
    assert partial["meta"]["missing_pages"] == [2]
    complete = merge_member_pages([page1, page2])
    assert complete["result_status"] == "VERIFIED_COMPLETE"
    assert complete["meta"]["row_count"] == 2


def test_member_ingest_rejects_credentials(tmp_path):
    unsafe = tmp_path / "unsafe.json"
    unsafe.write_text(json.dumps({"cookie": "secret", "data": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="Sensitive credential"):
        merge_member_pages([unsafe])


def test_member_request_plan_builds_only_requested_resume_pages():
    result = member_request_plan(timeframe="all-time", page_count=4, missing_pages=[2, 4])
    assert [row["page"] for row in result["requests"]] == [2, 4]
    assert all(row["path"].startswith("/api/top-sellers?") for row in result["requests"])
    assert "cookies" in result["never_save"]


def test_evidence_gate_requires_fresh_complete_rows(tmp_path):
    source = tmp_path / "snapshot.json"
    source.write_text(
        json.dumps({"source": "erank-member-browser-api", "coverage": "complete", "fetched_at": datetime.now(timezone.utc).isoformat(), "rows": [{"shop": "One"}]}),
        encoding="utf-8",
    )
    report = evidence_report(source, require_complete=True)
    assert report["accepted"] is True
    assert report["source_kind"] == "member_session"
    source.write_text(
        json.dumps({"source": "erank-member-browser-api", "coverage": "complete", "fetched_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(), "rows": [{"shop": "One"}]}),
        encoding="utf-8",
    )
    assert evidence_report(source, max_age_hours=24, require_complete=True)["accepted"] is False


def test_true_profit_enforces_margin_capacity_and_formula():
    result = true_profit(
        price=60,
        supplier_cost=15,
        shipping_cost=10,
        packaging_cost=2,
        production_minutes=30,
        labor_rate_hourly=20,
        return_rate=2,
        breakage_rate=1,
        weekly_orders=5,
        weekly_capacity_minutes=300,
        target_margin=20,
        formula_multiplier=2,
    )
    assert result["constraints"]["formula_recommended_price"] == 50
    assert result["constraints"]["capacity_ok"] is True
    assert result["decision"] == "VIABLE"
    with pytest.raises(ValueError, match="cannot exceed"):
        true_profit(price=20, return_rate=101)


def test_opportunity_engine_ranks_evidence_without_converting_unknown():
    result = opportunity_engine(
        [
            {"product": "Strong", "demand": 1000, "competition": 100, "growth": 20, "required_equipment": "laser;printer", "available_equipment": "laser;printer;embroidery", "ip_risk": 5, "price": 60, "supplier_cost": 10, "shipping_cost": 5},
            {"product": "Weak", "demand": "< 20", "competition": 5000, "growth": -20, "fit_score": 20, "ip_risk": 80},
        ]
    )
    assert result["opportunities"][0]["product"] == "Strong"
    assert result["opportunities"][0]["equipment"]["missing"] == []
    weak = next(row for row in result["opportunities"] if row["product"] == "Weak")
    assert weak["raw_metrics"]["demand"] == "< 20"
    assert "demand" in weak["missing_fields"]


def test_breakout_radar_adds_growth_and_keeps_uncertain_age_separate():
    current = [
        {"shop": "FastShop", "total_sales": 670, "created_at": "2026-04-03", "reviews": 20, "listings": 30},
        {"shop": "YearOnly", "total_sales": 665, "year_started": "2026"},
    ]
    previous = [{"shop": "FastShop", "total_sales": 650, "created_at": "2026-04-03", "reviews": 15, "listings": 25}]
    result = breakout_radar(
        current,
        as_of=date(2026, 8, 3),
        age_min_months=4,
        age_max_months=4,
        sales_min=660,
        sales_max=680,
        previous_rows=previous,
        snapshot_days=7,
    )
    assert result["matches"][0]["growth"]["weekly_sales_velocity"] == 20
    assert result["needs_verification"][0]["shop"] == "YearOnly"


def test_competitor_clusters_price_bands_and_hero_listing():
    current = [
        listing("1", "Walnut Nightstand", category="Furniture > Nightstands", sales=20, price=200),
        listing("2", "Oak Nightstand", category="Furniture > Nightstands", sales=10, price=100),
        listing("3", "Wood Desk", category="Furniture > Desks", sales=5, price=300),
    ]
    previous = [
        listing("1", "Walnut Nightstand", category="Furniture > Nightstands", sales=10, price=200),
        listing("3", "Wood Desk", category="Furniture > Desks", sales=4, price=300),
    ]
    result = cluster_listings(current, previous)
    assert result["cluster_count"] == 2
    assert result["clusters"][0]["family"] == "nightstands"
    assert result["clusters"][0]["price_band"]["average"] == 150
    assert result["clusters"][0]["sales_growth_signal"] == 10
    assert result["clusters"][0]["new_listing_count"] == 1


def test_change_impact_is_observational_and_flags_simultaneous_edits():
    old = listing("1", "Old Title", tags=["old tag"], sales=10, views=100, price=20)
    new = listing("1", "New Title", tags=["new tag"], sales=15, views=150, price=25)
    old.rank, new.rank = 20, 10
    old.visits, new.visits = 80, 130
    old.orders, new.orders = 8, 12
    old.revenue, new.revenue = 160, 300
    result = change_impact([old], [new], datetime(2026, 1, 1), datetime(2026, 1, 11))
    row = result["listings"][0]
    assert row["deltas"]["sales"] == 5
    assert row["deltas"]["visits"] == 50
    assert row["rank_improvement"] == 10
    assert "multiple_simultaneous_changes" in row["confounders"]
    assert result["causal_claim_allowed"] is False


def test_keyword_portfolio_detects_cannibalization_and_limits_slots():
    items = [
        listing("1", "Custom Wall Art Print", tags=["wall art", "custom print"]),
        listing("2", "Printable Wall Art Gift", tags=["wall art", "printable gift"]),
    ]
    result = keyword_portfolio(items, [{"keyword": "wall art", "search_volume": "< 20", "competition": 100}])
    assert result["cannibalization"][0]["keyword"] == "wall art"
    assert result["cannibalization"][0]["search_stage"] == "discovery"
    assert all(plan["slot_count"] <= 13 for plan in result["plans"])


def test_cro_audit_uses_manifest_and_requires_human_review():
    item = listing("1", "Custom Sign", image_count=6)
    result = cro_audit(item, [{"width": 1200, "height": 1200, "product_coverage": 40, "size_reference": False, "lifestyle": False}])
    codes = {issue["code"] for issue in result["issues"]}
    assert "low_resolution" in codes
    assert "product_too_small" in codes
    assert result["human_review_required"] is True


def test_image_file_analysis_extracts_real_technical_signals(tmp_path):
    path = tmp_path / "product.png"
    image = Image.new("RGB", (400, 400), "white")
    ImageDraw.Draw(image).rectangle((100, 100, 300, 300), fill="black")
    image.save(path)
    result = analyze_image_file(str(path))
    assert result["width"] == 400
    assert 20 < result["product_coverage"] < 40
    assert result["background_score"] > 90


def test_cross_market_requires_multiple_positive_sources():
    rows = [
        {"product": "Wall Sign", "source": "etsy", "signal": 80, "confidence": 0.9},
        {"product": "Wall Sign", "source": "pinterest", "signal": 70, "confidence": 0.8},
        {"product": "Wall Sign", "source": "google", "signal": 60, "confidence": 0.7},
    ]
    assert cross_market_validation(rows, min_sources=3)["products"][0]["decision"] == "VALIDATED"


def test_seasonal_plan_backtests_and_calculates_launch_date():
    rows = [
        {"product": "Halloween Sign", "month": 8, "search_volume": 20},
        {"product": "Halloween Sign", "month": 9, "search_volume": 80},
        {"product": "Halloween Sign", "month": 10, "search_volume": 100},
    ]
    result = seasonal_plan(rows, lead_days=45, as_of=date(2026, 1, 1))["products"][0]
    assert result["peak_month"] == 10
    assert result["recommended_launch_date"] == "2026-08-17"
    assert result["backtest_status"] == "SUFFICIENT"


def test_fact_gated_draft_requires_and_emits_exactly_13_tags():
    facts = {"product": "Cake Knife", "material": "stainless steel", "occasion": "wedding"}
    blocked = fact_gated_draft(facts, ["cake knife"])
    assert blocked["status"] == "NEEDS_CONFIRMATION"
    keywords = [f"buyer phrase {index}" for index in range(1, 14)]
    ready = fact_gated_draft(facts, keywords)
    assert ready["status"] == "DRAFT_READY_REVIEW_ONLY"
    assert len(ready["draft"]["tags"]) == 13
    assert ready["draft"]["tags_csv"].count(",") == 12


def test_anomaly_and_alert_deduplication():
    previous = [{"shop": "Fast", "total_sales": 10, "reviews": 1, "listings": 2}]
    current = [
        {"shop": "Fast", "total_sales": 100, "reviews": 5, "listings": 10},
        {"shop": "Fast", "total_sales": 100, "reviews": 5, "listings": 10},
    ]
    anomalies = detect_anomalies(current, previous, spike_multiplier=5)
    assert {row["code"] for row in anomalies["anomalies"]} >= {"sales_spike", "duplicate_identity"}
    first = watchlist_alerts(current[:1], previous)
    assert first["new_alert_count"] == 3
    second = watchlist_alerts(
        current[:1],
        previous,
        seen_alert_ids=first["state"]["seen_alert_ids"],
        prior_unresolved=first["state"]["unresolved"],
    )
    assert second["new_alert_count"] == 0
    assert second["suppressed_duplicate_count"] == 3
    assert second["unresolved_count"] == 3
    assert watchlist_alerts(current, previous, evidence_ok=False)["result_status"] == "BLOCKED_BY_EVIDENCE"


def test_live_shop_connectors_use_current_official_route_contract():
    calls = []

    class Response:
        status_code = 200

        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self.payload

    class Http:
        @staticmethod
        def get(url, **kwargs):
            calls.append((url, kwargs.get("params")))
            if url.endswith("/badge"):
                return Response({"shop_details": {"review_count": 10}})
            if url.endswith("/listings"):
                return Response({"recent_listings": [{"listing_id": 1, "title": "Desk", "tags": ["wood desk"]}]})
            return Response({"name": "DemoShop", "sales": {"total": 100}})

    info = fetch_erank_shop_info("DemoShop", http=Http)
    listings = fetch_erank_shop_listings("DemoShop", http=Http)
    assert info["schema_version"] == listings["schema_version"] == 1
    assert info["overview"]["name"] == "DemoShop"
    assert listings["count"] == 1
    assert calls[0][0].endswith("/api/shop-info/DemoShop")
    assert calls[1][0].endswith("/api/shop-info/DemoShop/badge")
    assert calls[2][0].endswith("/api/shop-info/DemoShop/listings")
