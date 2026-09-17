from __future__ import annotations

import os
from typing import Any

import requests

from cli_anything.erank.core.models import Listing


class EtsyBackend:
    """Small Etsy Open API v3 adapter.

    It intentionally exposes read-only calls used by this harness. Etsy requires
    an x-api-key header for most endpoints and OAuth for seller-private data.
    """

    base_url = "https://openapi.etsy.com/v3/application"

    def __init__(self, config: dict[str, Any] | None = None, timeout: int = 30):
        config = config or {}
        self.api_key = config.get("etsy_api_key") or os.environ.get("ETSY_API_KEY")
        self.oauth_token = config.get("etsy_oauth_token") or os.environ.get("ETSY_OAUTH_TOKEN")
        self.timeout = timeout

    def configured(self, require_oauth: bool = False) -> bool:
        if require_oauth:
            return bool(self.api_key and self.oauth_token)
        return bool(self.api_key)

    def headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["x-api-key"] = str(self.api_key)
        if self.oauth_token:
            headers["Authorization"] = f"Bearer {self.oauth_token}"
        return headers

    def request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("Missing Etsy API key. Run: config set etsy_api_key <key>")
        url = f"{self.base_url}{path}"
        response = requests.request(method, url, headers=self.headers(), timeout=self.timeout, **kwargs)
        if response.status_code >= 400:
            raise RuntimeError(f"Etsy API {response.status_code}: {response.text[:500]}")
        return response.json()

    def active_listings(self, keywords: str, limit: int = 25, offset: int = 0) -> list[Listing]:
        payload = self.request(
            "GET",
            "/listings/active",
            params={"keywords": keywords, "limit": limit, "offset": offset},
        )
        results = payload.get("results", payload if isinstance(payload, list) else [])
        return [Listing.from_mapping(row) for row in results]

    def shop_by_id(self, shop_id: str) -> dict[str, Any]:
        return self.request("GET", f"/shops/{shop_id}")

    def find_shops(self, shop_name: str, limit: int = 10) -> list[dict[str, Any]]:
        payload = self.request("GET", "/shops", params={"shop_name": shop_name, "limit": limit})
        return payload.get("results", payload if isinstance(payload, list) else [])

    def shop_listings(self, shop_id: str, limit: int = 100, offset: int = 0) -> list[Listing]:
        payload = self.request(
            "GET",
            f"/shops/{shop_id}/listings/active",
            params={"limit": limit, "offset": offset},
        )
        results = payload.get("results", payload if isinstance(payload, list) else [])
        listings = [Listing.from_mapping(row) for row in results]
        for listing in listings:
            if not listing.shop:
                listing.shop = str(shop_id)
        return listings
