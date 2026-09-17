from pathlib import Path
import json
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
FIXTURES = Path(__file__).parent / "fixtures"


def run_cli(*args):
    result = subprocess.run(
        [sys.executable, "-m", "cli_anything.erank", "--json", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_api_check_e2e():
    payload = run_cli("api-check")
    assert payload["erank_public_api"]["found"] is False
    assert payload["recommended_backend"]["name"] == "Etsy Open API v3"
    assert "/api/shop-info/{shop_name}" in payload["undocumented_read_only_routes"]["routes"]


def test_keyword_tool_e2e():
    payload = run_cli("keyword", "tool", "crochet pattern", "--listings", str(FIXTURES / "listings.csv"))
    assert payload["keyword"] == "crochet pattern"
    assert payload["top_listings"][0]["shop"] == "CozyCraftSupply"


def test_competitor_shop_info_e2e():
    payload = run_cli("competitor", "shop-info", "BrightMockupStudio", "--listings", str(FIXTURES / "listings.csv"))
    assert payload["listing_count"] == 2
    assert payload["total_sales"] == 67


def test_shop_health_check_e2e():
    payload = run_cli("shop", "health-check", "--listings", str(FIXTURES / "listings.csv"), "--shop", "CozyCraftSupply")
    assert payload["listing_count"] == 2
    assert payload["issue_counts"]


def test_tools_and_trends_e2e():
    profit = run_cli("tools", "profit", "--price", "30", "--item-cost", "9", "--shipping-cost", "5")
    assert profit["profit"] > 10
    trends = run_cli("trends", "buzz", "--trends-csv", str(FIXTURES / "trends.csv"), "--marketplace", "etsy")
    assert trends["trends"][0]["keyword"] == "crochet pattern"


def test_live_sources_e2e():
    payload = run_cli("live", "sources")
    assert payload["erank_member_browser"]["available"] is True
    assert payload["erank_live_api"]["available"] is None
    assert payload["erank_live_api"]["probe_command"] == "live source-probe"
    assert "live top-sellers --source erank-export --input path.csv" in payload["erank_export"]["commands"]


def test_live_top_sellers_export_e2e():
    payload = run_cli(
        "live",
        "top-sellers",
        "--source",
        "erank-export",
        "--input",
        str(FIXTURES / "top_sellers_export.csv"),
        "--limit",
        "2",
    )
    assert payload["realtime"] is False
    assert payload["snapshot"] is True
    assert payload["count"] == 2
    assert payload["rows"][0]["shop"] == "CaitlynMinimalist"
    assert payload["rows"][0]["monthly_sales"] == 20204


def test_live_shop_search_e2e():
    payload = run_cli(
        "live",
        "shop-search",
        "--input",
        str(FIXTURES / "shop_search_export.csv"),
        "--sales-min",
        "660",
        "--sales-max",
        "680",
        "--age-months",
        "4",
        "--as-of",
        "2026-08-03",
    )
    assert payload["match_count"] == 1
    assert payload["matches"][0]["shop"] == "ExactFourMonthShop"
    assert payload["needs_verification_count"] == 1


def test_live_shop_search_invalid_range_e2e():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "cli_anything.erank",
            "live",
            "shop-search",
            "--input",
            str(FIXTURES / "shop_search_export.csv"),
            "--sales-min",
            "680",
            "--sales-max",
            "660",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode != 0
    assert "cannot exceed" in result.stderr
