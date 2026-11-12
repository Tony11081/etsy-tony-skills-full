#!/usr/bin/env python3
"""Generate one product photo through the OpenRouter Image API.

One call = one image. Reads a prompt and up to 16 reference images, writes the
image file, and appends one line to <out dir>/generation-log.jsonl with the
model that produced it and the billed cost.

  python openrouter_image.py --prompt-file prompts/shot-01.txt \\
      --ref refs/front.jpg --ref refs/detail.jpg --out etsy-output/shot-01.png

  python openrouter_image.py --prompt-file prompts/shot-01.txt --ref refs/front.jpg \\
      --out etsy-output/shot-01.png --dry-run        # show the request, send nothing

Environment
-----------
  OPENROUTER_API_KEY     required. Read from the environment only. It is never
                         accepted on the command line, printed, or written to disk.
  OPENROUTER_BASE_URL    optional, default https://openrouter.ai/api/v1
  ETSY_TONY_IMAGE_MODEL  optional default for --model

Exit codes
----------
  0  image written
  2  bad arguments or unreadable input
  3  insufficient credits (HTTP 402): stop the run, do not retry
  4  key missing, invalid, disabled or over its spend limit (HTTP 401 / 403)
  5  request rejected, timed out, or upstream failed after the one fallback attempt
  6  output file already exists (pass --overwrite to replace it)

Only the Python standard library is required. When Pillow is installed, large
reference images are downscaled before upload and a mismatched output format
is converted to the requested extension.
"""
from __future__ import annotations

import argparse
import base64
import datetime as _dt
import io
import json
import mimetypes
import os
import socket
import sys
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openai/gpt-image-2"
DEFAULT_FALLBACK = "google/gemini-3.1-flash-image"
MAX_REFS = 16
MAX_REF_SIDE = 2048            # px, applied only when Pillow is available
MAX_REF_BYTES = 12 * 1024 * 1024
EXT_BY_MEDIA = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}
FORMAT_BY_EXT = {".png": "png", ".jpg": "jpeg", ".jpeg": "jpeg", ".webp": "webp"}


class Fail(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code


# --------------------------------------------------------------------------- inputs
def read_prompt(args) -> str:
    if bool(args.prompt) == bool(args.prompt_file):
        raise Fail(2, "pass exactly one of --prompt or --prompt-file")
    if args.prompt_file:
        try:
            with open(args.prompt_file, encoding="utf-8") as fh:
                text = fh.read()
        except OSError as exc:
            raise Fail(2, f"cannot read prompt file: {exc}") from None
    else:
        text = args.prompt
    text = text.strip()
    if not text:
        raise Fail(2, "prompt is empty")
    return text


def _downscale(raw: bytes, mime: str):
    """Shrink very large references. Returns (bytes, mime); unchanged without Pillow."""
    try:
        from PIL import Image
    except ImportError:
        return raw, mime
    try:
        im = Image.open(io.BytesIO(raw))
        im.load()
    except Exception:
        return raw, mime
    if max(im.size) <= MAX_REF_SIDE and len(raw) <= MAX_REF_BYTES:
        return raw, mime
    im.thumbnail((MAX_REF_SIDE, MAX_REF_SIDE))
    buf = io.BytesIO()
    if im.mode in ("RGBA", "LA", "P"):
        im.convert("RGBA").save(buf, "PNG")
        return buf.getvalue(), "image/png"
    im.convert("RGB").save(buf, "JPEG", quality=92)
    return buf.getvalue(), "image/jpeg"


def load_reference(ref: str) -> dict:
    """A reference is an http(s) URL or a local image file (sent as a base64 data URL)."""
    if ref.startswith(("http://", "https://")):
        return {"url": ref, "bytes": 0, "source": ref}
    try:
        with open(ref, "rb") as fh:
            raw = fh.read()
    except OSError as exc:
        raise Fail(2, f"cannot read reference image: {exc}") from None
    mime = mimetypes.guess_type(ref)[0] or ""
    if mime not in EXT_BY_MEDIA:
        raise Fail(2, f"unsupported reference type for {ref!r}: use PNG, JPEG or WebP")
    raw, mime = _downscale(raw, mime)
    if len(raw) > MAX_REF_BYTES:
        raise Fail(2, f"reference {ref!r} is {len(raw) // 1024 // 1024} MB; "
                      f"downscale it below {MAX_REF_BYTES // 1024 // 1024} MB (or install Pillow)")
    data_url = f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"
    return {"url": data_url, "bytes": len(raw), "source": ref}


# --------------------------------------------------------------------------- transport
def post_images(base_url: str, key: str, body: dict, timeout: int):
    """Returns (status, payload). status 0 = no HTTP response (network error or timeout)."""
    req = urllib.request.Request(
        base_url.rstrip("/") + "/images",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "X-Title": "etsy-tony-skills"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, _parse(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, _parse(exc.read())
    except (socket.timeout, TimeoutError):
        return 0, {"error": {"message": "timed out"}, "_timeout": True}
    except urllib.error.URLError as exc:
        timed_out = isinstance(exc.reason, (socket.timeout, TimeoutError))
        return 0, {"error": {"message": "timed out" if timed_out else f"network error: {exc.reason}"},
                   "_timeout": timed_out}


def _parse(raw: bytes) -> dict:
    try:
        data = json.loads(raw.decode("utf-8", "replace"))
        return data if isinstance(data, dict) else {"error": {"message": "unexpected response"}}
    except ValueError:
        return {"error": {"message": raw[:300].decode("utf-8", "replace")}}


def error_message(payload: dict) -> str:
    err = payload.get("error")
    if isinstance(err, dict):
        return str(err.get("message") or err)[:400]
    return str(err or "no error message")[:400]


def first_image(payload: dict):
    data = payload.get("data")
    if not isinstance(data, list) or not data or not isinstance(data[0], dict):
        return None
    b64 = data[0].get("b64_json")
    if not isinstance(b64, str) or len(b64) < 100:
        return None
    try:
        raw = base64.b64decode(b64, validate=False)
    except ValueError:
        return None
    return raw, data[0].get("media_type") or sniff_media_type(raw)


def sniff_media_type(raw: bytes) -> str:
    if raw[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if raw[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "image/webp"
    return "application/octet-stream"


# --------------------------------------------------------------------------- output
def write_image(raw: bytes, media_type: str, out_path: str) -> str:
    """Writes the image at out_path. If the returned format differs from the
    requested extension, converts with Pillow when possible; otherwise keeps the
    bytes and corrects the extension. Returns the path actually written."""
    want_ext = os.path.splitext(out_path)[1].lower()
    got_ext = EXT_BY_MEDIA.get(media_type)
    if got_ext is None:
        raise Fail(5, f"provider returned an unsupported image type: {media_type}")
    same = FORMAT_BY_EXT.get(want_ext) == FORMAT_BY_EXT.get(got_ext)
    final_path = out_path
    if not same:
        converted = None
        if want_ext in FORMAT_BY_EXT:
            try:
                from PIL import Image
                im = Image.open(io.BytesIO(raw))
                buf = io.BytesIO()
                fmt = FORMAT_BY_EXT[want_ext].upper()
                (im.convert("RGB") if fmt == "JPEG" else im).save(buf, fmt)
                converted = buf.getvalue()
            except Exception:
                converted = None
        if converted is not None:
            raw = converted
        else:
            final_path = os.path.splitext(out_path)[0] + got_ext
    os.makedirs(os.path.dirname(final_path) or ".", exist_ok=True)
    tmp = final_path + ".part"
    with open(tmp, "wb") as fh:
        fh.write(raw)
    os.replace(tmp, final_path)
    return final_path


def append_log(out_path: str, entry: dict) -> None:
    log_path = os.path.join(os.path.dirname(out_path) or ".", "generation-log.jsonl")
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


# --------------------------------------------------------------------------- main
def run(args) -> dict:
    prompt = read_prompt(args)
    if len(args.ref) > MAX_REFS:
        raise Fail(2, f"at most {MAX_REFS} reference images per call")
    if os.path.exists(args.out) and not args.overwrite:
        raise Fail(6, f"{args.out} already exists; pass --overwrite to replace it")
    refs = [load_reference(r) for r in args.ref]

    base_url = os.environ.get("OPENROUTER_BASE_URL", DEFAULT_BASE_URL)
    model = args.model or os.environ.get("ETSY_TONY_IMAGE_MODEL") or DEFAULT_MODEL
    fallback = None if args.fallback_model.lower() == "none" else args.fallback_model
    out_format = FORMAT_BY_EXT.get(os.path.splitext(args.out)[1].lower(), "png")

    def body_for(name: str, primary: bool) -> dict:
        body = {"model": name, "prompt": prompt, "n": 1, "aspect_ratio": args.aspect}
        if primary:  # quality and output_format are not accepted by every model
            if args.quality != "auto":
                body["quality"] = args.quality
            body["output_format"] = out_format
        if refs:
            body["input_references"] = [{"type": "image_url", "image_url": {"url": r["url"]}} for r in refs]
        return body

    if args.dry_run:
        return {"ok": True, "dry_run": True, "endpoint": base_url.rstrip("/") + "/images", "model": model,
                "fallback_model": fallback, "aspect_ratio": args.aspect, "quality": args.quality,
                "prompt_chars": len(prompt), "refs": [{"source": r["source"], "bytes": r["bytes"]} for r in refs],
                "out": args.out}

    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        raise Fail(4, "OPENROUTER_API_KEY is not set in the environment")

    used, fallback_used = model, False
    status, payload = post_images(base_url, key, body_for(model, True), args.timeout)
    if (status == 429 or status >= 500) and fallback and fallback != model:
        print(f"{model} failed with HTTP {status}: {error_message(payload)}; trying {fallback}", file=sys.stderr)
        used, fallback_used = fallback, True
        status, payload = post_images(base_url, key, body_for(fallback, False), args.timeout)

    if status == 0:
        hint = (" The request may still have completed and been billed: check the OpenRouter activity page "
                "before retrying.") if payload.get("_timeout") else ""
        raise Fail(5, f"{used}: {error_message(payload)}.{hint}")
    if status == 402:
        raise Fail(3, f"insufficient OpenRouter credits: {error_message(payload)}")
    if status in (401, 403):
        raise Fail(4, f"OpenRouter rejected the key (HTTP {status}): {error_message(payload)}")
    if status != 200:
        raise Fail(5, f"{used} failed with HTTP {status}: {error_message(payload)}")

    image = first_image(payload)
    if image is None:
        raise Fail(5, f"{used} returned no image data")
    raw, media_type = image
    written = write_image(raw, media_type, args.out)
    usage = payload.get("usage") if isinstance(payload.get("usage"), dict) else {}
    entry = {
        "time": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "ok": True, "out": written, "model": used, "fallback_used": fallback_used,
        "aspect_ratio": args.aspect, "quality": args.quality if not fallback_used else None,
        "refs": len(refs), "bytes": os.path.getsize(written), "media_type": media_type,
        "cost_usd": usage.get("cost"),
    }
    append_log(written, entry)
    return entry


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompt", help="prompt text")
    ap.add_argument("--prompt-file", help="UTF-8 text file holding the prompt")
    ap.add_argument("--ref", action="append", default=[], metavar="PATH_OR_URL",
                    help="reference product image; repeat for several (max 16)")
    ap.add_argument("--out", required=True, help="output image path, e.g. etsy-output/shot-01.png")
    ap.add_argument("--aspect", default="1:1", help="aspect ratio, e.g. 1:1, 4:3, 3:4, 16:9 (default 1:1)")
    ap.add_argument("--quality", default="medium", choices=["auto", "low", "medium", "high"],
                    help="primary model quality (default medium)")
    ap.add_argument("--model", help=f"image model (default {DEFAULT_MODEL})")
    ap.add_argument("--fallback-model", default=DEFAULT_FALLBACK,
                    help=f"used once when the primary returns HTTP 429/5xx (default {DEFAULT_FALLBACK}; 'none' disables)")
    ap.add_argument("--timeout", type=int, default=300, help="seconds to wait per request (default 300)")
    ap.add_argument("--overwrite", action="store_true", help="replace --out if it exists")
    ap.add_argument("--dry-run", action="store_true", help="validate inputs and print the request summary; send nothing")
    args = ap.parse_args(argv)
    try:
        result = run(args)
    except Fail as exc:
        print(json.dumps({"ok": False, "exit_code": exc.code, "error": str(exc)}, ensure_ascii=False))
        return exc.code
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
