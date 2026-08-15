#!/usr/bin/env python3
"""Validate an external vision API and update planning/vision_config.json.

Sends a tiny 64x64 test image and requires a non-empty model response.
On success sets external_api.status = "validated"; on failure keeps "failed"
with last_error. The key is read from the environment variable named by
external_api.key_env and is never written to disk.

Usage (from the workspace root):
  VISION_API_KEY=xxx python scripts/vision_probe.py \
    --config planning/vision_config.json

Exit codes: 0 validated, 1 failed, 2 configuration error.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


def build_test_image() -> str:
    img = Image.new("RGB", (64, 64), "#DC2626")
    for x in range(32, 64):
        for y in range(64):
            img.putpixel((x, y), (37, 99, 235))
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def probe(endpoint: str, key: str, model: str) -> str:
    payload = {
        "model": model,
        "temperature": 0.0,
        "max_tokens": 50,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "测试图。只回答左半和右半的颜色名称。"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{build_test_image()}"
                        },
                    },
                ],
            }
        ],
    }
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    content = data["choices"][0]["message"]["content"]
    return content if isinstance(content, str) else " ".join(
        part.get("text", "") for part in content if isinstance(part, dict)
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the configured external vision API."
    )
    parser.add_argument(
        "--config",
        default="planning/vision_config.json",
        help="path to vision_config.json",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate config only, without network calls",
    )
    args = parser.parse_args()

    path = Path(args.config)
    if not path.exists():
        print(f"config not found: {path}", file=sys.stderr)
        return 2
    cfg = json.loads(path.read_text(encoding="utf-8"))
    api = cfg.get("external_api") or {}
    key_env = api.get("key_env") or "VISION_API_KEY"
    key = os.environ.get(key_env, "")

    if args.dry_run:
        required = ("enabled", "provider", "endpoint", "models", "key_env")
        missing = [f for f in required if f not in api]
        print(
            f"dry-run: config {'OK' if not missing else 'missing ' + ', '.join(missing)}"
        )
        return 0 if not missing else 2
    if not key:
        print(f"error: {key_env} is not set", file=sys.stderr)
        return 2

    last_error = None
    for model in api.get("models", []):
        for attempt in range(2):
            try:
                content = probe(api["endpoint"], key, model)
                if content and content.strip():
                    api["enabled"] = True
                    api["status"] = "validated"
                    api["validated_at"] = datetime.now(timezone.utc).isoformat()
                    api["last_error"] = None
                    api["models"] = [model] + [
                        m for m in api.get("models", []) if m != model
                    ]
                    cfg["updated_at"] = datetime.now(timezone.utc).isoformat()
                    path.write_text(
                        json.dumps(cfg, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8",
                    )
                    print(f"validated: {model}")
                    return 0
            except urllib.error.HTTPError as e:
                last_error = f"{model}: HTTP {e.code}"
                if e.code == 429 and attempt == 0:
                    time.sleep(3)
                    continue
                break
            except Exception as e:  # noqa: BLE001
                last_error = f"{model}: {type(e).__name__}: {e}"
                break
        if last_error and "HTTP 429" not in last_error:
            continue

    api["status"] = "failed"
    api["last_error"] = last_error or "no models configured"
    cfg["updated_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"probe failed: {api['last_error']}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
