#!/usr/bin/env python3
"""Parse the Agentforce Specialist simulator HTML snapshot into a raw question list.

The saved HTML has rendered (unsubmitted) question cards — options are NOT marked
correct, and the answer-key lived in an external app.js that wasn't saved. But each
card's explanation prose states the correct option(s), so the answer is recovered
in a later agent step. This parser just extracts id/text/options/explanation.

Usage:  python3 tools/parse_agentforce_html.py
Writes  datasets/source-snapshots/agentforce/agentforce-raw.json
"""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "datasets/source-snapshots/agentforce/Agentforce Specialist Exam Simulator — 370 Practice Questions.html"
OUT = ROOT / "datasets/source-snapshots/agentforce/agentforce-raw.json"


def clean(fragment):
    fragment = re.sub(r'<span class="multi-select-label">.*?</span>', "", fragment, flags=re.S)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    return re.sub(r"\s+", " ", html.unescape(fragment)).strip()


def main():
    text = SRC.read_text(encoding="utf-8")
    cards = re.split(r'<div class="question-card[^"]*" id="qcard-(\d+)" data-qid="\d+">', text)
    by_id = {}
    for qid, chunk in zip(cards[1::2], cards[2::2]):
        qid = int(qid)
        if qid in by_id:
            continue  # each card is rendered twice; keep the first

        m_text = re.search(r'<div class="question-text">(.*?)</div>', chunk, re.S)
        if not m_text:
            continue
        options = [clean(m.group(1)) for m in
                   re.finditer(r'<div class="option-text">(.*?)</div>', chunk, re.S)]
        m_exp = re.search(r'<div class="explanation-panel"[^>]*>\s*<h4>.*?</h4>\s*<p>(.*?)</p>',
                          chunk, re.S)
        if len(options) < 2:
            continue
        by_id[qid] = {
            "num": qid,
            "text": clean(m_text.group(1)),
            "options": options,
            "explanation": clean(m_exp.group(1)) if m_exp else "",
            "multi_hint": bool(re.search(r"Choose\s+\w+\s+answers?", chunk, re.I)),
        }

    questions = [by_id[k] for k in sorted(by_id)]
    OUT.write_text(json.dumps(questions, indent=1, ensure_ascii=False), encoding="utf-8")
    from collections import Counter
    print(f"Parsed {len(questions)} unique questions -> {OUT.name}")
    print("option-count distribution:",
          dict(sorted(Counter(len(q["options"]) for q in questions).items())))
    print("with explanation:", sum(1 for q in questions if len(q["explanation"]) > 30))
    print("flagged 'Choose N answers':", sum(1 for q in questions if q["multi_hint"]))


if __name__ == "__main__":
    main()
