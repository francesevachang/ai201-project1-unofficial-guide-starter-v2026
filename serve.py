#!/usr/bin/env python3
"""
The Unofficial Guide — the same pipeline, over HTTP.

    python serve.py                          run it locally on port 5000
    gunicorn serve:app                       run it the way a host runs it

Nothing new happens in this file. It is a wrapper: a request comes in, it
hands the question to `app.py::ask_pipeline` — the exact function the command
line uses — and hands the answer back as JSON. Retrieval, the relevance gate
and the grounded prompt all still live where they lived. If you change how
your system answers, you change it in those files and this one follows.

Two routes:

    POST /ask       {"question": "..."} in, the answer and its sources out
    GET  /health    is the service up, and is there an index to search

Why this exists: `app.py` runs once and exits, which is fine on your laptop
and impossible to deploy. A hosted service has to stay up and wait for
requests. This is the smallest thing that does that.

Every /ask request writes one JSON line to logs/requests.jsonl. The fields
are listed in the README under Capstone.
"""

import json
import os
import time
from datetime import datetime, timezone

from flask import Flask, jsonify, request

import config

app = Flask(__name__)

LOG_PATH = config.ROOT / "logs" / "requests.jsonl"


def write_log(record):
    """Append one request to the log. A logging problem never fails a request."""
    try:
        LOG_PATH.parent.mkdir(exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception as exc:  # noqa: BLE001
        print(f"[log] could not write: {exc}", flush=True)


@app.get("/health")
def health():
    """Is the service up, and is there an index to search?

    Two different questions, and the second one is the one that bites. A
    freshly deployed service answers this route happily while every /ask
    returns "no index" — hosts give you no disk that survives a restart, so
    the index has to be built as part of getting the service up. Checking
    here means you find that out in one request instead of five.
    """
    from store import index_exists

    ready = index_exists(config.CORPUS)
    return jsonify(
        {
            "status": "ok",
            "corpus": config.CORPUS,
            "index_ready": ready,
            "detail": (
                "ready"
                if ready
                else "no index for this corpus — run `python app.py index`"
            ),
        }
    )


@app.post("/ask")
def ask():
    """One question in, one grounded answer out.

    A refused question is a 200, not an error. The gate refusing is your
    system working — it is an answer, and the JSON says so with
    `"refused": true` so whatever calls this can tell the two apart.
    """
    from app import ask_pipeline

    started = time.perf_counter()
    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "label": payload.get("label"),
        "corpus": config.CORPUS,
        "model": config.MODEL,
        "question": question,
    }

    def finish(body, code, **fields):
        record.update(fields)
        record["latency_ms"] = round((time.perf_counter() - started) * 1000)
        write_log(record)
        return jsonify(body), code

    if not question:
        msg = (
            "Send JSON with a question in it, like "
            '{"question": "is the housing lottery random?"}'
        )
        return finish({"error": msg}, 400, status="bad_request", error=msg, answer=None)

    import generate

    tokens_before = generate.token_counts()
    hits_before = generate.cache_hit_count()

    try:
        outcome = ask_pipeline(question, corpus=config.CORPUS)
    except Exception as exc:  # noqa: BLE001 — a reader gets this, not a traceback
        msg = f"{type(exc).__name__}: {exc}"
        return finish({"error": msg}, 500, status="error", error=msg, answer=None)

    tokens_after = generate.token_counts()
    usage = {
        "cached": generate.cache_hit_count() > hits_before,
        "input_tokens": tokens_after["prompt"] - tokens_before["prompt"],
        "output_tokens": tokens_after["output"] - tokens_before["output"],
    }

    if outcome["refused"]:
        status = "refused_by_gate"
    elif "enough information" in outcome["answer"].lower():
        status = "refused_by_model"
    else:
        status = "answered"
    return finish(
        {
            "question": question,
            "answer": outcome["answer"],
            "refused": outcome["refused"],
            "sources": outcome["sources"],
            "best_distance": round(outcome["best_distance"], 4),
            "threshold": outcome["threshold"],
            "corpus": config.CORPUS,
        },
        200,
        status=status,
        error=None,
        answer=outcome["answer"],
        sources=outcome["sources"],
        best_distance=round(outcome["best_distance"], 4),
        **usage,
    )


def main():
    # Hosts tell you which port to listen on through PORT, and they expect you
    # on 0.0.0.0. Binding 127.0.0.1 instead works perfectly on your laptop and
    # then answers nothing at all once deployed, because the host's router
    # can't reach a socket that only accepts connections from inside the
    # container. It is the single most common way a first deploy "succeeds"
    # and is unreachable.
    port = int(os.getenv("PORT", "5000"))

    # Debug mode reloads on save, which is handy, and prints a console that
    # runs arbitrary code, which is not something to leave switched on where
    # strangers can reach it. Off unless you ask for it.
    debug = os.getenv("AI201_DEBUG", "0") == "1"

    print(f"Serving The Unofficial Guide on http://localhost:{port}")
    print(f"Corpus: {config.CORPUS}    (Ctrl-C to stop)\n")
    print("Try it from another terminal:\n")
    print(f"  curl http://localhost:{port}/health")
    print(
        f"  curl -X POST http://localhost:{port}/ask \\\n"
        f"    -H 'Content-Type: application/json' \\\n"
        f"    -d '{{\"question\": \"is the housing lottery random?\"}}'\n"
    )

    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":
    main()
