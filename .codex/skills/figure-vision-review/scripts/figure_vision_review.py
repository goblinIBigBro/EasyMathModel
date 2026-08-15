#!/usr/bin/env python3
"""External vision-model figure review for the EasyMathModel workflow.

Two complementary modes:
  open      - free-form 10-criterion review with a score
  checklist - 10 verifiable PASS/FAIL/UNCERTAIN checks (mandatory signal)

Exit codes:
  0  all reviewed figures passed, or the run was skipped by policy (NOT_RUN)
  1  at least one figure has a checklist FAIL (NEEDS_FIX)
  2  configuration error (missing file, bad schema, missing key when enabled)
  3  API unavailable after model fallback/retries (figures recorded NOT_RUN)

The API key is read only from the environment variable named by
external_api.key_env (default VISION_API_KEY). It is never written to disk,
to the report, or to stdout.

Usage (from the workspace root):
  VISION_API_KEY=xxx python scripts/figure_vision_review.py \
    --config planning/vision_config.json \
    --figures paper/figures/fig1.png paper/figures/fig2.png \
    --mode both \
    --context "Q3 timeline; conclusion: union 7.74 s"
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

from PIL import Image

PROMPTS = Path(__file__).resolve().parent.parent / "references" / "prompts.md"
DEFAULT_KEY_ENV = "VISION_API_KEY"


def redact(text: str, key: str) -> str:
    return text.replace(key, "[REDACTED]") if key else text


def load_prompt(name: str) -> str:
    text = PROMPTS.read_text(encoding="utf-8")
    m = re.search(
        rf"<!-- PROMPT:{name.upper()}_BEGIN -->\n(.*?)\n"
        rf"<!-- PROMPT:{name.upper()}_END -->",
        text,
        flags=re.S,
    )
    if not m:
        raise RuntimeError(f"prompt marker {name} missing in {PROMPTS}")
    return m.group(1).strip()


def load_config(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"config not found: {path} (exit 2)")
    cfg = json.loads(path.read_text(encoding="utf-8"))
    if cfg.get("schema_version") != 1:
        raise SystemExit(f"unsupported schema_version in {path} (exit 2)")
    api = cfg.get("external_api") or {}
    for field in ("enabled", "provider", "endpoint", "models", "key_env"):
        if field not in api:
            raise SystemExit(f"config missing external_api.{field} (exit 2)")
    return cfg


def compress_image(path: Path, max_edge: int) -> str:
    img = Image.open(path).convert("RGB")
    img.thumbnail((max_edge, max_edge), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def call_model(
    endpoint: str,
    key: str,
    model: str,
    b64: str,
    prompt: str,
    max_tokens: int,
    temperature: float,
) -> str:
    payload = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64}"},
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
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    content = data["choices"][0]["message"]["content"]
    if isinstance(content, list):
        content = "".join(
            part.get("text", "") for part in content if isinstance(part, dict)
        )
    return content


def parse_checklist(text: str) -> list[dict]:
    results = []
    for line in text.splitlines():
        m = re.match(
            r"^\s*(\d{1,2})[.、)\s]+(PASS|FAIL|UNCERTAIN)\s*[:：]?\s*(.*)$",
            line.strip(),
            flags=re.IGNORECASE,
        )
        if m:
            evidence = re.sub(
                r"^证据[是]?[“\"「]?|^；?\s*证据[：:]?", "", m.group(3).strip()
            ).strip(" “\"「」」”")
            results.append(
                {
                    "num": int(m.group(1)),
                    "verdict": m.group(2).upper(),
                    "evidence": evidence,
                }
            )
    results.sort(key=lambda r: r["num"])
    for i in range(1, 11):
        if not any(r["num"] == i for r in results):
            results.append(
                {"num": i, "verdict": "UNCERTAIN", "evidence": "模型未输出该项"}
            )
    return sorted(results, key=lambda r: r["num"])


def parse_score(text: str) -> float | None:
    m = re.search(r"总分[^0-9]{0,15}(\d+(?:\.\d+)?)", text)
    if not m:
        m = re.search(r"(\d+(?:\.\d+)?)\s*/\s*10", text)
    return float(m.group(1)) if m else None


def review_figure(
    cfg: dict,
    key: str,
    path: Path,
    context: str,
    mode: str,
    dry_run: bool,
) -> dict:
    api = cfg["external_api"]
    policy = cfg["policy"]
    result = {
        "figure": path.name,
        "path": str(path),
        "context": context,
        "verdict": "NOT_RUN",
        "reason": None,
        "score": None,
        "checks": [],
        "raw": {},
        "model": None,
        "errors": [],
    }
    if dry_run:
        result["verdict"] = "VALIDATED_ONLY"
        result["raw"]["dry_run"] = "paths and prompts validated"
        return result
    if not api.get("enabled") or api.get("status") == "skipped":
        result["reason"] = "external vision API disabled/skipped by policy"
        return result

    max_edge = int(policy.get("max_image_edge", 1280))
    b64 = compress_image(path, max_edge)
    prompts = {
        "open": load_prompt("open"),
        "checklist": load_prompt("checklist"),
    }
    tasks = []
    if mode in ("open", "both"):
        tasks.append(("open", prompts["open"], 1500, 0.3))
    if mode in ("checklist", "both"):
        tasks.append(("checklist", prompts["checklist"], 1200, 0.1))

    for task_name, prompt, max_tokens, temperature in tasks:
        text = f"图名：{path.name}\n背景与待核对结论：{context}\n\n{prompt}"
        succeeded = False
        for model in api["models"]:
            for attempt in range(2):
                try:
                    raw = call_model(
                        api["endpoint"],
                        key,
                        model,
                        b64,
                        text,
                        max_tokens,
                        temperature,
                    )
                    result["raw"][task_name] = raw
                    result["model"] = model
                    succeeded = True
                    break
                except urllib.error.HTTPError as e:
                    body = redact(e.read().decode("utf-8", "replace")[:200], key)
                    msg = f"{model}: HTTP {e.code} {body}"
                    result["errors"].append(msg)
                    if e.code == 413 and max_edge > 1024:
                        max_edge = 1024
                        b64 = compress_image(path, max_edge)
                        continue
                    if e.code == 429 and attempt == 0:
                        time.sleep(3)
                        continue
                    break
                except Exception as e:  # noqa: BLE001
                    result["errors"].append(
                        f"{model}: {type(e).__name__}: {redact(str(e), key)}"
                    )
                    break
            if succeeded:
                break
        if not succeeded:
            return result

    if "checklist" in result["raw"]:
        result["checks"] = parse_checklist(result["raw"]["checklist"])
    if "open" in result["raw"]:
        result["score"] = parse_score(result["raw"]["open"])

    fails = [c for c in result["checks"] if c["verdict"] == "FAIL"]
    result["verdict"] = "NEEDS_FIX" if fails else "PASSED"
    return result


def write_report(results: list[dict], out: Path, cfg: dict, mode: str) -> None:
    api = cfg["external_api"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# 视觉模型图审报告",
        "",
        f"> 生成时间：{now}",
        f"> 模式：{mode}",
        f"> 模型列表：{' → '.join(api['models'])}",
        f"> API 状态：{api.get('status', 'unknown')}（Key 仅存于环境变量）",
        "",
        "## 汇总表",
        "",
        "| 图 | 判定 | 开放分(10) | 清单 PASS/FAIL/UNC | 模型 |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        checks = r["checks"]
        n_pass = sum(1 for c in checks if c["verdict"] == "PASS")
        n_fail = sum(1 for c in checks if c["verdict"] == "FAIL")
        n_unc = sum(1 for c in checks if c["verdict"] == "UNCERTAIN")
        lines.append(
            f"| {r['figure']} | {r['verdict']} | {r['score'] or '—'} | "
            f"{n_pass}/{n_fail}/{n_unc} | {r['model'] or '—'} |"
        )
    lines.append("")
    lines.append("## 逐图明细")
    for r in results:
        lines.append(f"\n### {r['figure']} — {r['verdict']}")
        lines.append(f"\n**背景**：{r['context']}")
        if r.get("reason"):
            lines.append(f"\n**原因**：{r['reason']}")
        if r["errors"]:
            lines.append("\n**错误/跳过原因**：")
            lines.extend(f"- {e}" for e in r["errors"])
        if "checklist" in r["raw"]:
            lines.append("\n| 检查项 | 结论 | 证据 |")
            lines.append("|---|---|---|")
            for c in r["checks"]:
                lines.append(f"| {c['num']}. | {c['verdict']} | {c['evidence']} |")
        if "open" in r["raw"]:
            lines.append(f"\n**开放评审（分数 {r['score']}）**\n")
            lines.append("```text")
            lines.append(r["raw"]["open"])
            lines.append("```")
        if "checklist" in r["raw"]:
            lines.append("\n**清单原始输出**\n")
            lines.append("```text")
            lines.append(r["raw"]["checklist"])
            lines.append("```")
    lines.append("")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review rendered figures with an external vision model."
    )
    parser.add_argument(
        "--config",
        default="planning/vision_config.json",
        help="path to vision_config.json (default: planning/vision_config.json)",
    )
    parser.add_argument(
        "--figures", nargs="+", required=True, help="rendered figure paths"
    )
    parser.add_argument(
        "--mode",
        choices=["open", "checklist", "both"],
        default="both",
        help="review modes (default: both)",
    )
    parser.add_argument("--context", default="", help="claim/context for figures")
    parser.add_argument(
        "--out",
        default="paper/audits/vision_figure_review.md",
        help="output report path",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate config, figures, and prompts without network calls",
    )
    args = parser.parse_args()

    try:
        cfg = load_config(Path(args.config))
    except SystemExit as e:
        print(e, file=sys.stderr)
        return 2

    api = cfg["external_api"]
    key_env = api.get("key_env") or DEFAULT_KEY_ENV
    key = os.environ.get(key_env, "")

    figures = [Path(p) for p in args.figures]
    missing = [str(p) for p in figures if not p.exists()]
    if missing:
        print(f"missing figures: {', '.join(missing)}", file=sys.stderr)
        return 2

    if args.dry_run:
        print("dry-run: config OK")
        print(f"dry-run: {len(figures)} figure(s) exist")
        for name in ("open", "checklist"):
            try:
                load_prompt(name)
                print(f"dry-run: prompt [{name}] OK")
            except RuntimeError as e:
                print(e, file=sys.stderr)
                return 2
        if api.get("enabled") and not key:
            print(f"dry-run: warning — {key_env} is not set")
        else:
            print(f"dry-run: {key_env} present or API disabled")
        return 0

    if api.get("enabled") and not key:
        print(f"error: {key_env} is not set (exit 2)", file=sys.stderr)
        return 2

    results = [
        review_figure(cfg, key, p, args.context, args.mode, False)
        for p in figures
    ]
    write_report(results, Path(args.out), cfg, args.mode)
    print(f"report written: {args.out}")

    any_api_error = any(
        r["verdict"] == "NOT_RUN" and r["errors"] and not r.get("reason")
        for r in results
    )
    any_fail = any(r["verdict"] == "NEEDS_FIX" for r in results)
    for r in results:
        print(f"{r['figure']}: {r['verdict']}")
    if any_api_error:
        return 3
    if any_fail:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
