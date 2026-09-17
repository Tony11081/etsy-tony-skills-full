from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable

from cli_anything.erank.core.models import Listing, Order


def read_table(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Data file not found: {source}")
    suffix = source.suffix.lower()
    if suffix == ".json":
        data = json.loads(source.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [dict(row) for row in data]
        if isinstance(data, dict):
            for key in ("listings", "orders", "rows", "data", "items", "trends"):
                if isinstance(data.get(key), list):
                    return [dict(row) for row in data[key]]
            return [data]
        raise ValueError(f"Unsupported JSON payload in {source}")
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def load_listings(path: str | Path | None) -> list[Listing]:
    if not path:
        return []
    return [Listing.from_mapping(row) for row in read_table(path)]


def load_orders(path: str | Path | None) -> list[Order]:
    if not path:
        return []
    return [Order.from_mapping(row) for row in read_table(path)]


def load_rows(path: str | Path | None) -> list[dict[str, Any]]:
    if not path:
        return []
    return read_table(path)


def write_csv(path: str | Path, rows: Iterable[dict[str, Any]]) -> int:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    materialized = list(rows)
    if not materialized:
        target.write_text("", encoding="utf-8-sig")
        return 0
    fieldnames: list[str] = []
    for row in materialized:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with target.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(materialized)
    return len(materialized)


def write_json(path: str | Path, payload: Any) -> str:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return str(target.resolve())
