#!/usr/bin/env python3
"""
Measure what one run costs.

Sends 10 real requests to the running server (the 5 test questions, twice),
then reads the numbers back out of logs/requests.jsonl and averages them.

Start the server first, with the cache off, in another terminal:

    AI201_CACHE=0 PORT=5001 python serve.py

Then:

    python tools/measure_cost.py
    python tools/measure_cost.py --port 5001 --runs 10

Optional, if you want a dollar figure from the measured tokens:

    python tools/measure_cost.py --price-in 0.10 --price-out 0.40

Prices are dollars per million tokens. Look them up yourself and say where you
got them. The token counts are what was measured; the dollars are tokens times
whatever price you give it.
"""

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from questions import QUESTIONS  # noqa: E402

LOG = ROOT / "logs" / "requests.jsonl"


def ask(port, question, label):
    body = json.dumps({"question": question, "label": label}).encode()
    req = urllib.request.Request(
        f"http://localhost:{port}/ask",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        resp.read()


def mean(values):
    return sum(values) / len(values) if values else 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5001)
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--price-in", type=float, default=None,
                        help="dollars per million input tokens")
    parser.add_argument("--price-out", type=float, default=None,
                        help="dollars per million output tokens")
    args = parser.parse_args()

    questions = [q["question"] for q in QUESTIONS]
    prefix = f"cost-{int(time.time())}"

    print(f"Warm-up request (not counted) ...")
    try:
        ask(args.port, questions[0], f"{prefix}-warmup")
        print("  ok")
    except Exception as exc:  # noqa: BLE001
        print(f"  failed: {exc}")

    print(f"Sending {args.runs} measured requests to localhost:{args.port} ...")
    for i in range(args.runs):
        question = questions[i % len(questions)]
        label = f"{prefix}-{i + 1}"
        try:
            ask(args.port, question, label)
            print(f"  {i + 1}/{args.runs} ok")
        except Exception as exc:  # noqa: BLE001
            print(f"  {i + 1}/{args.runs} failed: {exc}")

    rows = []
    for line in LOG.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        label = row.get("label") or ""
        if label.startswith(prefix) and not label.endswith("-warmup"):
            rows.append(row)

    if not rows:
        print("\nNo log lines found for this run. Is the server running from this folder?")
        return

    cached = [r for r in rows if r.get("cached")]
    refused = [r for r in rows if r.get("status") == "refused_by_gate"]
    failed = [r for r in rows if r.get("status") in ("error", "bad_request")]
    real = [r for r in rows if not r.get("cached") and r.get("status") not in
            ("refused_by_gate", "error", "bad_request")]

    print(f"\nMeasured log lines (warm-up excluded): {len(rows)}")
    print(f"  real model calls: {len(real)}")
    print(f"  served from cache: {len(cached)}")
    print(f"  refused by gate:   {len(refused)}")
    print(f"  failed:            {len(failed)}")

    if cached:
        print("\nWARNING: some answers came from the cache, so they cost 0 tokens.")
        print("Restart the server with AI201_CACHE=0 and run this again.")

    if not real:
        print("\nNo real model calls to average.")
        return

    avg_in = mean([r["input_tokens"] for r in real])
    avg_out = mean([r["output_tokens"] for r in real])
    avg_total_ms = mean([r["latency_ms"] for r in real])
    avg_ret_ms = mean([r["retrieval_ms"] for r in real])
    avg_gen_ms = mean([r["generation_ms"] for r in real])

    print(f"\nAverage over {len(real)} warm model calls:")
    print(f"  input tokens:   {avg_in:.1f}")
    print(f"  output tokens:  {avg_out:.1f}")
    print(f"  total tokens:   {avg_in + avg_out:.1f}")
    print(f"  latency_ms:     {avg_total_ms:.0f}")
    print(f"  retrieval_ms:   {avg_ret_ms:.0f}")
    print(f"  generation_ms:  {avg_gen_ms:.0f}")

    if args.price_in is not None and args.price_out is not None:
        dollars = (avg_in * args.price_in + avg_out * args.price_out) / 1_000_000
        print(f"  dollars per run: ${dollars:.6f}  (at ${args.price_in}/M in, ${args.price_out}/M out)")


if __name__ == "__main__":
    main()
