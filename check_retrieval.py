#!/usr/bin/env python3
"""
Run every question in questions.py through `python app.py retrieve` — no
model call, one subprocess per question.

    python check_retrieval.py

For each question in QUESTIONS, then each in OUT_OF_SCOPE, shells out to
`python app.py retrieve "<question>"` and reads its output: the top source it
retrieved (or NOT IN CORPUS if the gate would refuse it) and the best
distance. Prints one markdown table row per question.
"""

import re
import subprocess
import sys

import config
import questions as qs

TOP_RESULT = re.compile(r"^1\s+([\d.]+)\s+(\S+)", re.MULTILINE)


def check_one(question: str) -> tuple[str, str, float]:
    """One question through `app.py retrieve`. No answer, just distances."""
    result = subprocess.run(
        [sys.executable, "app.py", "retrieve", question],
        capture_output=True,
        text=True,
        check=True,
    )
    output = result.stdout

    match = TOP_RESULT.search(output)
    if not match:
        return question, "NOT IN CORPUS", 1.0

    distance, source = float(match.group(1)), match.group(2)
    location = "NOT IN CORPUS" if "refusing" in output else f"{config.CORPUS}/{source}"

    return question, location, distance


def main():
    questions = [item["question"] for item in qs.answered()] + list(qs.OUT_OF_SCOPE)

    print("| Question | Corpus / Document | Best Distance |")
    print("|---|---|---|")
    for question in questions:
        question_text, location, distance = check_one(question)
        cell = question_text.replace("|", "\\|")
        print(f"| {cell} | {location} | {distance:.4f} |")


if __name__ == "__main__":
    main()
