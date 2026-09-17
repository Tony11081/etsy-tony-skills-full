from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from typing import Any


def parse_tags(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    if text.startswith("["):
        try:
            decoded = json.loads(text)
            if isinstance(decoded, list):
                return [str(item).strip() for item in decoded if str(item).strip()]
        except json.JSONDecodeError:
            pass
    delimiter = "|"
    for candidate in (";", "|", ","):
        if candidate in text:
            delimiter = candidate
            break
    return [part.strip() for part in text.split(delimiter) if part.strip()]


def parse_number(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace("$", "").replace(",", "").strip()
    try:
        return float(text)
    except ValueError:
        return default


def parse_int(value: Any, default: int = 0) -> int:
    return int(round(parse_number(value, float(default))))


def parse_datetime(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        if value <= 0:
            return None
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(text, fmt)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def first_value(mapping: dict[str, Any], *keys: str, default: Any = None) -> Any:
    lowered = {str(key).lower(): value for key, value in mapping.items()}
    for key in keys:
        if key in mapping and mapping[key] not in (None, ""):
            return mapping[key]
        lower = key.lower()
        if lower in lowered and lowered[lower] not in (None, ""):
            return lowered[lower]
    return default


@dataclass
class Listing:
    listing_id: str = ""
    shop: str = ""
    title: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    price: float = 0.0
    currency: str = "USD"
    views: int = 0
    visits: int = 0
    favorites: int = 0
    sales: int = 0
    orders: int = 0
    revenue: float = 0.0
    rank: int = 0
    quantity: int = 0
    category: str = ""
    country: str = ""
    status: str = "active"
    url: str = ""
    created: str = ""
    updated: str = ""
    image_count: int = 0
    materials: list[str] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, row: dict[str, Any]) -> "Listing":
        price_value = first_value(row, "price", "amount", "listing_price", default=0)
        if isinstance(price_value, dict):
            amount = parse_number(price_value.get("amount"), 0)
            divisor = parse_number(price_value.get("divisor"), 100) or 100
            price = amount / divisor
            currency = str(price_value.get("currency_code") or price_value.get("currency") or "USD")
        else:
            price = parse_number(price_value, 0)
            currency = str(first_value(row, "currency", "currency_code", default="USD"))

        created = first_value(row, "created", "creation_tsz", "created_timestamp", "creation_timestamp", default="")
        updated = first_value(row, "updated", "last_modified_tsz", "updated_timestamp", default="")
        created_dt = parse_datetime(created)
        updated_dt = parse_datetime(updated)

        materials = parse_tags(first_value(row, "materials", "material", default=""))
        tags = parse_tags(first_value(row, "tags", "tag", "taxonomy_path", default=""))

        images = first_value(row, "images", "image_count", "photos", default="")
        if isinstance(images, list):
            image_count = len(images)
        else:
            image_count = parse_int(images, 0)

        return cls(
            listing_id=str(first_value(row, "listing_id", "id", "listingId", default="")),
            shop=str(first_value(row, "shop", "shop_name", "shopName", "shop_id", default="")),
            title=str(first_value(row, "title", "name", default="")).strip(),
            description=str(first_value(row, "description", "body", default="")).strip(),
            tags=tags,
            price=price,
            currency=currency,
            views=parse_int(first_value(row, "views", "view_count", "num_views", default=0), 0),
            visits=parse_int(first_value(row, "visits", "traffic", "sessions", default=0), 0),
            favorites=parse_int(first_value(row, "favorites", "num_favorers", "likes", default=0), 0),
            sales=parse_int(first_value(row, "sales", "num_sold", "sold", "orders", default=0), 0),
            orders=parse_int(first_value(row, "orders", "order_count", "conversions", default=0), 0),
            revenue=parse_number(first_value(row, "revenue", "gross_revenue", default=0), 0),
            rank=parse_int(first_value(row, "rank", "position", "search_rank", default=0), 0),
            quantity=parse_int(first_value(row, "quantity", "stock", default=0), 0),
            category=str(first_value(row, "category", "category_path", "taxonomy", default="")).strip(),
            country=str(first_value(row, "country", "shop_location", "location", default="")).strip(),
            status=str(first_value(row, "status", "state", default="active")).strip() or "active",
            url=str(first_value(row, "url", "listing_url", default="")).strip(),
            created=created_dt.isoformat() if created_dt else str(created or ""),
            updated=updated_dt.isoformat() if updated_dt else str(updated or ""),
            image_count=image_count,
            materials=materials,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def age_days(self, now: datetime | None = None) -> float:
        created_dt = parse_datetime(self.created)
        if not created_dt:
            return 30.0
        ref = now or datetime.now(timezone.utc)
        return max((ref - created_dt).total_seconds() / 86400, 1.0)


@dataclass
class Order:
    order_id: str = ""
    country: str = ""
    total: float = 0.0
    status: str = ""
    carrier: str = ""
    tracking_number: str = ""
    created: str = ""

    @classmethod
    def from_mapping(cls, row: dict[str, Any]) -> "Order":
        created = first_value(row, "created", "date", "order_date", default="")
        created_dt = parse_datetime(created)
        return cls(
            order_id=str(first_value(row, "order_id", "receipt_id", "id", default="")),
            country=str(first_value(row, "country", "ship_country", "destination_country", default="")),
            total=parse_number(first_value(row, "total", "grand_total", "revenue", default=0), 0),
            status=str(first_value(row, "status", "delivery_status", "shipment_status", default="")),
            carrier=str(first_value(row, "carrier", "shipping_carrier", default="")),
            tracking_number=str(first_value(row, "tracking_number", "tracking", default="")),
            created=created_dt.isoformat() if created_dt else str(created or ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
