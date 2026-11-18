#!/usr/bin/env python3
"""
Run the five capstone criteria three times and write the run log to results/.

    .venv/bin/python tools/run_capstone_eval.py

What it does, per run (3 runs, each with fresh servers):
  - starts a good server (cache off) and a bad-key server, on their own ports
  - sends the requests each criterion needs (see criteria.md)
  - reads the numbers back out of the server's own request log

The servers write to results/capstone_logs/, NOT to logs/requests.jsonl, so the
committed log stays clean. serve.py is not modified: this script only swaps its
LOG_PATH before starting it.

Output: results/capstone_run_<timestamp>.md  (table + the real log lines)
"""

import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import config  # noqa: E402  (loads .env into the environment)
from questions import OUT_OF_SCOPE, QUESTIONS  # noqa: E402

RUNS = 3
GOOD_KEY = os.environ.get("GEMINI_API_KEY", "")
BAD_KEY = "this-is-not-a-real-key"
LATENCY_LIMIT_MS = 3000
TOKEN_LIMIT = 600

FULL_FIELDS = {
    "timestamp", "label", "corpus", "model", "question", "status", "error",
    "answer", "sources", "best_distance", "num_chunks", "retrieval_ms",
    "generation_ms", "cached", "input_tokens", "output_tokens", "latency_ms",
}
SHORT_FIELDS = {
    "timestamp", "label", "corpus", "model", "question", "status", "error",
    "answer", "latency_ms",
}

OUT_DIR = ROOT / "results" / "capstone_logs"
LAUNCHER = (
    "import os, signal, sys\n"
    "from pathlib import Path\n"
    "sys.path.insert(0, sys.argv[1])\n"
    "import serve\n"
    "serve.LOG_PATH = Path(sys.argv[2])\n"
    # SIGUSR1 = "someone put the real key back into the environment"
    "signal.signal(signal.SIGUSR1, lambda *a: os.environ.__setitem__("
    "'GEMINI_API_KEY', os.environ['REAL_KEY_FOR_TEST']))\n"
    "serve.main()\n"
)


# ─── small helpers ───────────────────────────────────────────────────────────


def post(port, payload, timeout=90):
    """POST to /ask. Returns (http_code, body_text)."""
    data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
    req = urllib.request.Request(
        f"http://localhost:{port}/ask",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()


def get_health(port):
    try:
        with urllib.request.urlopen(f"http://localhost:{port}/health", timeout=5) as r:
            return r.status
    except Exception:  # noqa: BLE001
        return None


def start_server(port, log_path, key, cache_off=True):
    env = dict(os.environ)
    env["PORT"] = str(port)
    env["GEMINI_API_KEY"] = key
    env["REAL_KEY_FOR_TEST"] = GOOD_KEY
    if cache_off:
        env["AI201_CACHE"] = "0"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("")
    proc = subprocess.Popen(
        [sys.executable, "-c", LAUNCHER, str(ROOT), str(log_path)],
        env=env,
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    for _ in range(120):
        if proc.poll() is not None:
            raise RuntimeError(f"server on port {port} died while starting")
        if get_health(port) == 200:
            return proc
        time.sleep(1)
    proc.kill()
    raise RuntimeError(f"server on port {port} never became healthy")


def stop_server(proc):
    try:
        os.killpg(proc.pid, signal.SIGTERM)
        proc.wait(timeout=10)
    except Exception:  # noqa: BLE001
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except Exception:  # noqa: BLE001
            pass


def read_log(path):
    """Return (list of raw lines, list of parsed-or-None)."""
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    parsed = []
    for l in lines:
        try:
            parsed.append(json.loads(l))
        except json.JSONDecodeError:
            parsed.append(None)
    return lines, parsed


def by_label(path, prefix):
    lines, parsed = read_log(path)
    return [(raw, row) for raw, row in zip(lines, parsed)
            if row and str(row.get("label") or "").startswith(prefix)]


# ─── the five criteria ───────────────────────────────────────────────────────


def crit1(port, log_path, n):
    """20 mixed requests -> exactly 20 new, complete, valid log lines."""
    questions = [q["question"] for q in QUESTIONS]
    plan = []  # (payload, expected statuses)
    a = o = e = 0
    for i in range(20):
        kind = ("ans", "oos", "empty")[i % 3] if i < 18 else ("oos", "empty")[i % 2]
        label = f"c1-r{n}-{i + 1}"
        if kind == "ans":
            plan.append(({"question": questions[a % 5], "label": label},
                         {"answered", "refused_by_model"}))
            a += 1
        elif kind == "oos":
            plan.append(({"question": OUT_OF_SCOPE[o % 5], "label": label},
                         {"refused_by_gate"}))
            o += 1
        else:
            plan.append(({"question": "", "label": label}, {"bad_request"}))
            e += 1

    before = len(read_log(log_path)[0])
    for payload, _ in plan:
        post(port, payload)
    lines, parsed = read_log(log_path)
    new_lines, new_parsed = lines[before:], parsed[before:]

    problems = []
    if len(new_lines) != 20:
        problems.append(f"expected 20 new lines, got {len(new_lines)}")
    good = 0
    for (payload, expected), row in zip(plan, new_parsed):
        if row is None:
            problems.append(f"{payload['label']}: not valid JSON")
            continue
        status = row.get("status")
        need = SHORT_FIELDS if status in ("error", "bad_request") else FULL_FIELDS
        missing = need - set(row)
        if missing:
            problems.append(f"{payload['label']}: missing {sorted(missing)}")
        elif status not in expected:
            problems.append(f"{payload['label']}: status {status}, wanted {sorted(expected)}")
        else:
            good += 1
    if len(new_lines) != 20:
        good = min(good, len(new_lines))
    return {
        "score": good, "of": 20, "passed": good == 20 and len(new_lines) == 20,
        "cell": f"{good}/20", "problems": problems,
        "raw": new_lines,
        "summary": f"{len(new_lines)} new lines; {good}/20 valid, complete, right status",
    }


def crit2_and_3(port, log_path, n):
    """20 uncached real requests -> latency distribution, and token mean (first 10)."""
    questions = [q["question"] for q in QUESTIONS]
    prefix = f"c23-r{n}-"
    for i in range(20):
        post(port, {"question": questions[i % 5], "label": f"{prefix}{i + 1:02d}"})
    rows = by_label(log_path, prefix)
    usable = [(raw, r) for raw, r in rows
              if r.get("status") in ("answered", "refused_by_model") and not r.get("cached")]
    lat = [r["latency_ms"] for _, r in usable]
    over = [x for x in lat if x > LATENCY_LIMIT_MS]
    ok2 = len(usable) == 20 and len(over) <= 1
    first10 = usable[:10]
    tokens = [r["input_tokens"] + r["output_tokens"] for _, r in first10]
    mean_tok = sum(tokens) / len(tokens) if tokens else float("nan")
    ok3 = len(first10) == 10 and mean_tok <= TOKEN_LIMIT
    lat_sorted = sorted(lat)
    c2 = {
        "score": 20 - len(over), "of": 20, "passed": ok2,
        "cell": f"{len(over)}/20 over" if len(usable) == 20 else f"only {len(usable)} usable",
        "problems": [],
        "raw": [raw for raw, _ in usable],
        "summary": (f"{len(usable)} usable requests; latency_ms min {lat_sorted[0]}, "
                    f"median {lat_sorted[len(lat_sorted)//2]}, max {lat_sorted[-1]}; "
                    f"{len(over)} over {LATENCY_LIMIT_MS}") if lat else "no usable requests",
    }
    c3 = {
        "score": mean_tok, "of": TOKEN_LIMIT, "passed": ok3,
        "cell": f"{mean_tok:.0f} tok",
        "problems": [],
        "raw": [raw for raw, _ in first10],
        "summary": f"mean input+output over first {len(first10)} requests = {mean_tok:.1f}",
    }
    return c2, c3


def crit4(port, log_path, n):
    """3 bad inputs -> 400, bad_request logged, 0 tokens, then a normal question works."""
    cases = [
        ("empty string", {"question": "", "label": f"c4-r{n}-empty"}),
        ("missing key", {"label": f"c4-r{n}-missing"}),
        ("whitespace only", {"question": "   ", "label": f"c4-r{n}-space"}),
    ]
    good, problems, raw = 0, [], []
    for name, payload in cases:
        code, body = post(port, payload)
        rows = by_label(log_path, payload["label"])
        row = rows[-1][1] if rows else None
        if rows:
            raw.append(rows[-1][0])
        why = []
        if code != 400:
            why.append(f"HTTP {code}, wanted 400")
        if not row:
            why.append("no log line")
        else:
            if row.get("status") != "bad_request":
                why.append(f"status {row.get('status')}")
            if not row.get("error"):
                why.append("error is empty")
            if row.get("answer") is not None:
                why.append("answer not null")
            if row.get("input_tokens") or row.get("output_tokens"):
                why.append("tokens used")
        if why:
            problems.append(f"{name}: " + "; ".join(why))
        else:
            good += 1

    code, body = post(port, {"question": QUESTIONS[0]["question"], "label": f"c4-r{n}-after"})
    after = by_label(log_path, f"c4-r{n}-after")
    after_ok = code == 200 and bool(after) and after[-1][1].get("status") == "answered"
    if after:
        raw.append(after[-1][0])
    if not after_ok:
        problems.append(f"follow-up question: HTTP {code}")
    passed = good == 3 and after_ok
    return {
        "score": good, "of": 3, "passed": passed,
        "cell": f"{good}/3" + ("" if after_ok else " (follow-up failed)"),
        "problems": problems, "raw": raw,
        "summary": f"{good}/3 bad inputs handled; follow-up question {'ok' if after_ok else 'FAILED'}",
    }


def crit5(port, log_path, pid, n):
    """Bad key: 3 requests -> 500, logged, no stack trace. Then put key back, no restart."""
    good, problems, raw = 0, [], []
    for i in range(3):
        label = f"c5-r{n}-{i + 1}"
        code, body = post(port, {"question": QUESTIONS[i]["question"], "label": label})
        rows = by_label(log_path, label)
        row = rows[-1][1] if rows else None
        if rows:
            raw.append(rows[-1][0])
        why = []
        if code != 500:
            why.append(f"HTTP {code}, wanted 500")
        if "Traceback" in body or 'File "' in body:
            why.append("stack trace in response")
        if BAD_KEY in body or (GOOD_KEY and GOOD_KEY in body):
            why.append("key text in response")
        if not row:
            why.append("no log line")
        else:
            if row.get("status") != "error":
                why.append(f"status {row.get('status')}")
            if not row.get("error"):
                why.append("error message empty")
            if "latency_ms" not in row:
                why.append("no latency_ms")
        if why:
            problems.append(f"request {i + 1}: " + "; ".join(why))
        else:
            good += 1

    alive = get_health(port) == 200
    os.kill(pid, signal.SIGUSR1)  # put the real key back in the environment
    time.sleep(0.5)
    label = f"c5-r{n}-recover"
    code, body = post(port, {"question": QUESTIONS[0]["question"], "label": label})
    rows = by_label(log_path, label)
    if rows:
        raw.append(rows[-1][0])
    recovered = code == 200 and bool(rows) and rows[-1][1].get("status") == "answered"
    if not alive:
        problems.append("server stopped responding after errors")
    if not recovered:
        problems.append(
            f"after key restored (no restart): HTTP {code}, "
            f"status {rows[-1][1].get('status') if rows else 'no log line'}"
        )
    return {
        "score": good, "of": 3, "passed": good == 3 and alive and recovered,
        "cell": f"{good}/3" + ("" if recovered else " (no recovery)"),
        "problems": problems, "raw": raw,
        "summary": (f"{good}/3 errors handled; server alive: {alive}; "
                    f"answered after key restored without restart: {recovered}"),
    }


# ─── main ────────────────────────────────────────────────────────────────────


def run_once(n):
    print(f"\n=== Run {n} ===", flush=True)
    good_log = OUT_DIR / f"run{n}_good_server.jsonl"
    bad_log = OUT_DIR / f"run{n}_badkey_server.jsonl"
    good = start_server(5200 + n, good_log, GOOD_KEY)
    bad = start_server(5210 + n, bad_log, BAD_KEY)
    results = {}
    try:
        print("  warm-up request (not counted) ...", flush=True)
        t = time.perf_counter()
        post(5200 + n, {"question": QUESTIONS[0]["question"], "label": f"warmup-r{n}"})
        print(f"    took {round((time.perf_counter() - t) * 1000)} ms", flush=True)

        print("  criteria 2 + 3 (20 requests) ...", flush=True)
        results[2], results[3] = crit2_and_3(5200 + n, good_log, n)
        print("  criterion 1 (20 mixed requests) ...", flush=True)
        results[1] = crit1(5200 + n, good_log, n)
        print("  criterion 4 (bad input) ...", flush=True)
        results[4] = crit4(5200 + n, good_log, n)
        print("  criterion 5 (bad key) ...", flush=True)
        results[5] = crit5(5210 + n, bad_log, bad.pid, n)
    finally:
        stop_server(good)
        stop_server(bad)
    for k in sorted(results):
        r = results[k]
        print(f"    {k}: {'PASS' if r['passed'] else 'FAIL'}  {r['summary']}", flush=True)
        for p in r["problems"]:
            print(f"       - {p}", flush=True)
    return results


def main():
    if not GOOD_KEY:
        sys.exit("No GEMINI_API_KEY in .env")
    all_runs = [run_once(n) for n in range(1, RUNS + 1)]

    names = {
        1: ("1. Every request leaves one complete log line", "20 of 20"),
        2: ("2. Answered requests are fast", f"at most 1 of 20 over {LATENCY_LIMIT_MS} ms"),
        3: ("3. Answers stay cheap", f"mean tokens at most {TOKEN_LIMIT}"),
        4: ("4. Bad input gets a clean rejection", "3 of 3 (+ follow-up works)"),
        5: ("5. A broken pipeline fails loudly and recovers", "3 of 3 (+ recovers, no restart)"),
    }
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    out = ROOT / "results" / f"capstone_run_{stamp}.md"
    md = [f"# Capstone run log — {stamp}", "",
          f"- Produced by: `tools/run_capstone_eval.py::main` (3 runs, fresh servers each run)",
          f"- Server: `serve.py` with `LOG_PATH` redirected to `results/capstone_logs/`, cache off (`AI201_CACHE=0`)",
          f"- Model: `{config.MODEL}` · top-k {config.TOP_K} · cutoff {config.THRESHOLD}",
          "- One warm-up request per run is sent first and not counted.",
          "- Criteria 2 and 3 share the same 20 requests (3 uses the first 10).", "",
          "| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |", "|---|---|---|---|---|---|"]
    for k in range(1, 6):
        cells = [all_runs[r][k]["cell"] for r in range(RUNS)]
        verdict = "MET" if all(all_runs[r][k]["passed"] for r in range(RUNS)) else "MISSED"
        md.append(f"| {names[k][0]} | {names[k][1]} | " + " | ".join(cells) + f" | {verdict} |")

    md += ["", "## What happened in each run", ""]
    for k in range(1, 6):
        md.append(f"### {names[k][0]}")
        for r in range(RUNS):
            res = all_runs[r][k]
            md.append(f"- Run {r + 1}: {'pass' if res['passed'] else 'FAIL'} — {res['summary']}")
            for p in res["problems"]:
                md.append(f"  - problem: {p}")
        md.append("")

    fn = {1: "crit1", 2: "crit2_and_3", 3: "crit2_and_3", 4: "crit4", 5: "crit5"}
    md += ["## Real log lines from run 1", "",
           "Each block is the raw `logs`-style JSON the server wrote.", ""]
    for k in range(1, 6):
        md.append(f"### {names[k][0]} — produced by `tools/run_capstone_eval.py::{fn[k]}`")
        md.append("```json")
        md += all_runs[0][k]["raw"]
        md.append("```")
        md.append("")
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\nWrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
