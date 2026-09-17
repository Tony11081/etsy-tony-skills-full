from datetime import date
import json
from pathlib import Path

import pytest

from cli_anything.erank.core.shop_search import completed_months, find_shops, load_shop_rows
from cli_anything.erank.utils.live_sources import probe_erank_live_api


FIXTURES = Path(__file__).parent / "fixtures"


def test_completed_months_respects_opening_day():
    assert completed_months(date(2026, 4, 3), date(2026, 8, 3)) == 4
    assert completed_months(date(2026, 4, 4), date(2026, 8, 3)) == 3


def test_shop_search_requires_exact_age_and_lifetime_sales():
    rows, metadata = load_shop_rows(FIXTURES / "shop_search_export.csv")
    result = find_shops(
        rows,
        sales_min=660,
        sales_max=680,
        age_months=4,
        age_tolerance=0,
        as_of=date(2026, 8, 3),
        default_period=metadata.get("period"),
    )
    assert [row["shop"] for row in result["matches"]] == ["ExactFourMonthShop"]
    assert [row["shop"] for row in result["needs_verification"]] == ["YearOnlyCandidate"]
    assert result["excluded_summary"]["total_sales_unavailable"] == 1


def test_shop_search_rejects_reversed_sales_range():
    with pytest.raises(ValueError, match="cannot exceed"):
        find_shops([], sales_min=680, sales_max=660, age_months=4, age_tolerance=0, as_of=date(2026, 8, 3))


def test_shop_search_reads_saved_member_json(tmp_path):
    source = tmp_path / "member.json"
    source.write_text(
        json.dumps(
            {
                "source": {"kind": "erank-member-browser", "fetched_at": "2026-08-03T00:00:00Z"},
                "timeframe": "all-time",
                "rows": [{"shop": "JsonShop", "sales": 666, "created_at": "2026-04-03"}],
            }
        ),
        encoding="utf-8",
    )
    rows, metadata = load_shop_rows(source)
    result = find_shops(
        rows,
        sales_min=660,
        sales_max=680,
        age_months=4,
        age_tolerance=0,
        as_of=date(2026, 8, 3),
        default_period=metadata["period"],
    )
    assert result["matches"][0]["shop"] == "JsonShop"
    assert metadata["source"] == "erank-member-browser"


def test_source_probe_reports_member_requirement_without_retry():
    class Response:
        status_code = 403
        ok = False

    class Http:
        calls = 0

        @classmethod
        def get(cls, *args, **kwargs):
            cls.calls += 1
            return Response()

    result = probe_erank_live_api(http=Http)
    assert Http.calls == 3
    assert result["access"] == "blocked"
    assert all(check["auth_required"] is True for check in result["checks"].values())
