from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[3]


def run_cli(*args):
    result = subprocess.run(
        [sys.executable, "-m", "cli_anything.erank", "--json", *map(str, args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout)


def write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_all_extended_commands_are_discoverable():
    expected = {
        "live": ["member-ingest", "member-plan", "evidence-check", "shop-info", "shop-listings", "shop-tags"],
        "selection": ["breakout-shops", "opportunity", "cross-market", "daily", "sales-report", "furniture-report"],
        "competitor": ["clusters"],
        "listing": ["impact", "cro-audit", "fact-draft"],
        "keyword": ["portfolio"],
        "tools": ["true-profit"],
        "trends": ["seasonal-plan"],
        "shop": ["anomalies", "watchlist-alerts"],
    }
    for group, commands in expected.items():
        result = subprocess.run(
            [sys.executable, "-m", "cli_anything.erank", group, "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        for command in commands:
            assert command in result.stdout


def test_extended_workflows_end_to_end(tmp_path):
    now = datetime.now(timezone.utc).isoformat()
    listings_before = write_json(
        tmp_path / "before.json",
        {
            "listings": [
                {
                    "listing_id": "1",
                    "shop": "DemoShop",
                    "title": "Walnut Nightstand",
                    "description": "Confirmed walnut nightstand details " * 20,
                    "tags": ["wall art", "walnut table", "bedroom decor"],
                    "category": "Furniture > Nightstands",
                    "price": 120,
                    "sales": 10,
                    "views": 100,
                    "image_count": 5,
                },
                {
                    "listing_id": "2",
                    "shop": "DemoShop",
                    "title": "Oak Nightstand",
                    "description": "Confirmed oak nightstand details " * 20,
                    "tags": ["wall art", "oak table", "bedroom decor"],
                    "category": "Furniture > Nightstands",
                    "price": 100,
                    "sales": 5,
                    "views": 60,
                    "image_count": 5,
                },
            ]
        },
    )
    listings_after = write_json(
        tmp_path / "after.json",
        {
            "listings": [
                {
                    "listing_id": "1",
                    "shop": "DemoShop",
                    "title": "Floating Walnut Nightstand",
                    "description": "Confirmed walnut nightstand details " * 20,
                    "tags": ["floating table", "walnut table", "bedroom decor"],
                    "category": "Furniture > Nightstands",
                    "price": 130,
                    "sales": 15,
                    "views": 160,
                    "image_count": 6,
                },
                {
                    "listing_id": "2",
                    "shop": "DemoShop",
                    "title": "Oak Nightstand",
                    "description": "Confirmed oak nightstand details " * 20,
                    "tags": ["wall art", "oak table", "bedroom decor"],
                    "category": "Furniture > Nightstands",
                    "price": 100,
                    "sales": 6,
                    "views": 70,
                    "image_count": 5,
                },
            ]
        },
    )
    image_manifest = write_json(
        tmp_path / "images.json",
        {"rows": [{"listing_id": "1", "width": 2500, "height": 2500, "product_coverage": 70, "background_score": 85, "size_reference": True, "personalization_visible": True, "lifestyle": True}]},
    )
    product_image = tmp_path / "product.png"
    rendered = Image.new("RGB", (400, 400), "white")
    ImageDraw.Draw(rendered).rectangle((100, 100, 300, 300), fill="black")
    rendered.save(product_image)
    facts = write_json(tmp_path / "facts.json", {"product": "Cake Knife", "material": "stainless steel", "occasion": "wedding"})
    opportunities = write_json(
        tmp_path / "opportunities.json",
        {
            "rows": [
                {"product": "Nightstand", "demand": 1000, "competition": 100, "growth": 20, "competitor_momentum": 15, "required_equipment": "laser;printer", "available_equipment": "laser;printer", "ip_risk": 5},
                {"product": "Weak Product", "demand": "< 20", "competition": 5000, "growth": -20, "fit_score": 20, "ip_risk": 80},
            ]
        },
    )
    opportunity_costs = write_json(
        tmp_path / "costs.json",
        {"rows": [{"product": "Nightstand", "price": 120, "supplier_cost": 30, "shipping_cost": 20, "production_minutes": 30, "formula_multiplier": 2}]},
    )
    cross_market = write_json(
        tmp_path / "cross.json",
        {"rows": [{"product": "Nightstand", "source": source, "signal": signal, "confidence": 0.8} for source, signal in [("etsy", 80), ("google", 70), ("pinterest", 65)]]},
    )
    seasonal = write_json(
        tmp_path / "seasonal.json",
        {"rows": [{"product": "Halloween Sign", "month": month, "search_volume": volume} for month, volume in [(8, 20), (9, 80), (10, 100)]]},
    )
    previous = write_json(
        tmp_path / "previous.json",
        {"source": "erank-member-browser-api", "coverage": "complete", "fetched_at": now, "rows": [{"shop": "FastShop", "total_sales": 650, "created_at": "2026-04-03", "reviews": 10, "listings": 20, "category": "Furniture"}]},
    )
    current = write_json(
        tmp_path / "current.json",
        {"source": "erank-member-browser-api", "coverage": "complete", "fetched_at": now, "rows": [{"shop": "FastShop", "total_sales": 670, "created_at": "2026-04-03", "reviews": 15, "listings": 25, "category": "Furniture"}]},
    )
    top_sellers = write_json(
        tmp_path / "top.json",
        {
            "source": "erank-member-browser-api",
            "coverage": "complete",
            "fetched_at": now,
            "timeframe": "all-time",
            "rows": [{"rank": 1, "shop": "FastShop", "total_sales": 670, "category": "Furniture > Nightstands", "on_etsy_since": "2026-04-03"}],
        },
    )
    page1 = write_json(
        tmp_path / "page1.json",
        {"source": "erank-member-browser-api", "endpoint": "/api/top-sellers", "timeframe": "all-time", "fetched_at": now, "data": [{"shop_id": 1, "shop_name": "FastShop"}], "meta": {"current_page": 1, "last_page": 1, "total": 1}},
    )

    assert run_cli("live", "member-ingest", "--input", page1)["result_status"] == "VERIFIED_COMPLETE"
    assert run_cli("live", "member-plan", "--pages", 2)["request_count"] == 2
    assert run_cli("live", "evidence-check", "--input", current, "--require-complete")["accepted"] is True
    assert run_cli("live", "shop-info", "DemoShop", "--source", "export", "--input", listings_before)["listing_count"] == 2
    assert run_cli("live", "shop-listings", "DemoShop", "--source", "export", "--input", listings_before)["count"] == 2
    assert run_cli("live", "shop-tags", "DemoShop", "--source", "export", "--input", listings_before)["unique_tags"] >= 3
    assert run_cli("competitor", "clusters", "--listings", listings_before)["cluster_count"] == 1
    assert run_cli("listing", "impact", "--before", listings_before, "--after", listings_after)["matched_listings"] == 2
    assert run_cli("listing", "cro-audit", "--listing-file", listings_before, "--image", product_image, "--image-manifest", image_manifest)["checks"]["first_image_width"] == 400
    fact_args = ["listing", "fact-draft", "--facts", facts]
    for index in range(1, 14):
        fact_args.extend(["--keyword", f"buyer phrase {index}"])
    assert len(run_cli(*fact_args)["draft"]["tags"]) == 13
    assert run_cli("keyword", "portfolio", "--listings", listings_before)["cannibalization"]
    assert run_cli("tools", "true-profit", "--price", 80, "--supplier-cost", 20, "--shipping-cost", 10, "--formula-multiplier", 2)["constraints"]["formula_ok"] is True
    assert run_cli("trends", "seasonal-plan", "--input", seasonal, "--as-of", "2026-01-01")["products"][0]["peak_month"] == 10
    assert run_cli("shop", "anomalies", "--current", current, "--previous", previous)["rows_checked"] == 1
    alerts = run_cli("shop", "watchlist-alerts", "--current", current, "--previous", previous, "--state", tmp_path / "alerts.json")
    assert alerts["new_alert_count"] >= 1
    second_alerts = run_cli("shop", "watchlist-alerts", "--current", current, "--previous", previous, "--state", tmp_path / "alerts.json")
    assert second_alerts["new_alert_count"] == 0
    assert second_alerts["unresolved_count"] == alerts["unresolved_count"]
    resolved = run_cli(
        "shop", "watchlist-alerts", "--current", current, "--previous", previous,
        "--state", tmp_path / "alerts.json", "--resolve-alert", alerts["alerts"][0]["alert_id"],
    )
    assert resolved["unresolved_count"] == alerts["unresolved_count"] - 1
    breakout = run_cli(
        "selection", "breakout-shops", "--input", current, "--previous", previous,
        "--snapshot-dir", tmp_path / "snapshots", "--age-min-months", 4, "--age-max-months", 4,
        "--as-of", "2026-08-03",
    )
    assert breakout["matches"][0]["shop"] == "FastShop"
    assert Path(breakout["snapshot_output"]).exists()
    opportunity = run_cli("selection", "opportunity", "--input", opportunities, "--input", opportunity_costs)
    assert opportunity["opportunities"][0]["product"] == "Nightstand"
    assert len(opportunity["input_sources"]) == 2
    assert run_cli("selection", "cross-market", "--input", cross_market)["products"][0]["decision"] == "VALIDATED"
    daily = run_cli("selection", "daily", "--source", "exports", "--yesterday-input", top_sellers, "--member-all-time-input", top_sellers)
    assert daily["result_status"] == "VERIFIED_COMPLETE"
    assert run_cli("selection", "sales-report", "--source", "erank-export", "--input", top_sellers)["count"] == 1
    assert run_cli("selection", "furniture-report", "--input", top_sellers)["furniture_count"] == 1
