#!/usr/bin/env python3
"""Clawlist Gemini JSON client used by the Etsy eRank pipeline."""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
import time
from pathlib import Path
from typing import Any, Callable
from urllib import error, request


BASE_URL = "https://clawlist.best/v1"
CHAT_URL = f"{BASE_URL}/chat/completions"
DEFAULT_MODEL = "gemini-3.1-pro-preview"
API_KEY_ENV = "CLAWLIST_API_KEY"
MODEL_ENV = "ETSY_LISTING_GEMINI_MODEL"
TRANSIENT_HTTP_CODES = {429, 500, 502, 503, 504}
MAX_IMAGES = 6
MAX_IMAGE_BYTES = 12 * 1024 * 1024


class GeminiError(RuntimeError):
    """Safe client error that never includes the API key."""


def resolve_setting(name: str) -> tuple[str | None, str]:
    value = os.environ.get(name)
    if value:
        return value.strip(), "process_environment"
    if os.name != "nt":
        return None, "missing"
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, name)
        resolved = str(value).strip() or None
        return resolved, "windows_user_environment" if resolved else "missing"
    except (FileNotFoundError, OSError):
        return None, "missing"


def image_part(value: str) -> dict[str, Any]:
    if value.startswith(("https://", "http://", "data:image/")):
        url = value
    else:
        path = Path(value).expanduser().resolve()
        if not path.is_file():
            raise GeminiError(f"Image not found: {path}")
        if path.stat().st_size > MAX_IMAGE_BYTES:
            raise GeminiError(f"Image exceeds {MAX_IMAGE_BYTES // (1024 * 1024)} MB: {path.name}")
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if not mime.startswith("image/"):
            raise GeminiError(f"Unsupported image type: {path.name}")
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        url = f"data:{mime};base64,{encoded}"
    return {"type": "image_url", "image_url": {"url": url}}


def user_content(payload: dict[str, Any], images: list[str]) -> str | list[dict[str, Any]]:
    safe = dict(payload)
    safe["images"] = [f"image_{index + 1}" for index in range(len(images))]
    text = json.dumps(safe, ensure_ascii=False, indent=2)
    if not images:
        return text
    if len(images) > MAX_IMAGES:
        raise GeminiError(f"At most {MAX_IMAGES} images are supported per request.")
    content: list[dict[str, Any]] = [{"type": "text", "text": text}]
    content.extend(image_part(str(value)) for value in images)
    return content


def parse_json_content(content: str) -> dict[str, Any]:
    clean = content.strip()
    clean = re.sub(r"^```(?:json)?\s*", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\s*```$", "", clean)
    try:
        parsed = json.loads(clean)
    except json.JSONDecodeError as exc:
        raise GeminiError(f"Gemini returned invalid or truncated JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise GeminiError("Gemini JSON must be an object.")
    return parsed


class GeminiClient:
    def __init__(self, model: str | None = None, timeout: int = 120) -> None:
        api_key, source = resolve_setting(API_KEY_ENV)
        if not api_key:
            raise GeminiError(f"{API_KEY_ENV} is not configured. The skill cannot use another provider.")
        configured_model, _ = resolve_setting(MODEL_ENV)
        selected_model = model or configured_model or DEFAULT_MODEL
        if "gemini" not in selected_model.casefold():
            raise GeminiError("Only Gemini models on the configured Clawlist endpoint are allowed.")
        if timeout < 10 or timeout > 600:
            raise GeminiError("timeout must be between 10 and 600 seconds.")
        self.api_key = api_key
        self.credential_source = source
        self.model = selected_model
        self.timeout = timeout

    def _request(self, messages: list[dict[str, Any]], temperature: float) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 12000,
            "response_format": {"type": "json_object"},
        }
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        last_error = "unknown API failure"
        for attempt in range(1, 3):
            req = request.Request(
                CHAT_URL,
                data=body,
                method="POST",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "etsy-tony-full-erank-listing/1.0",
                },
            )
            try:
                with request.urlopen(req, timeout=self.timeout) as response:
                    return json.loads(response.read().decode("utf-8"))
            except error.HTTPError as exc:
                detail = exc.read(1200).decode("utf-8", errors="replace").replace(self.api_key, "[REDACTED]")
                last_error = f"Clawlist HTTP {exc.code}: {detail}"
                if exc.code not in TRANSIENT_HTTP_CODES or attempt == 2:
                    break
            except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = f"Clawlist request failed: {exc}"
                if attempt == 2:
                    break
            time.sleep(2 ** (attempt - 1))
        raise GeminiError(last_error)

    @staticmethod
    def _extract(response: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        try:
            choice = response["choices"][0]
            content = choice["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise GeminiError("Clawlist returned an unexpected response shape.") from exc
        if not isinstance(content, str) or not content.strip():
            raise GeminiError("Clawlist returned empty model content.")
        return content, {
            "returned_model": response.get("model"),
            "finish_reason": choice.get("finish_reason"),
            "usage": response.get("usage"),
        }

    def generate_json(
        self,
        *,
        stage: str,
        system_prompt: str,
        payload: dict[str, Any],
        images: list[str] | None = None,
        validator: Callable[[dict[str, Any]], list[str]] | None = None,
        temperature: float = 0.15,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        images = images or []
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content(payload, images)},
        ]
        last_error = "validation failed"
        last_metadata: dict[str, Any] = {}
        for generation_attempt in range(1, 4):
            response = self._request(messages, temperature)
            content, last_metadata = self._extract(response)
            try:
                result = parse_json_content(content)
                problems = validator(result) if validator else []
                if problems:
                    raise GeminiError("; ".join(problems))
                metadata = {
                    "stage": stage,
                    "provider": "Clawlist",
                    "endpoint": CHAT_URL,
                    "requested_model": self.model,
                    "credential_source": self.credential_source,
                    "validated": True,
                    "generation_attempts": generation_attempt,
                    **last_metadata,
                }
                return result, metadata
            except GeminiError as exc:
                last_error = str(exc)
                if generation_attempt == 3:
                    break
                messages.extend(
                    [
                        {"role": "assistant", "content": content},
                        {
                            "role": "user",
                            "content": (
                                f"Validation failed: {last_error} Return a complete corrected JSON object only. "
                                "Preserve accurate content and fix every listed error."
                            ),
                        },
                    ]
                )
        finish = last_metadata.get("finish_reason")
        raise GeminiError(
            f"Gemini stage {stage} failed validation after 3 attempts: {last_error}; finish_reason={finish}"
        )

    def redact(self, message: str) -> str:
        return message.replace(self.api_key, "[REDACTED]")
