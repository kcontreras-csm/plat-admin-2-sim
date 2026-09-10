#!/usr/bin/env python3
"""Regenerate the QUESTIONS block in app.js from the files in datasets/.

Two source formats are supported:

  *.json — the simulator's question bank (questions.json from
           https://kvidals21.github.io/plat-admin2-simulator/), where each
           entry has id, category (1-6), text, options (list of strings),
           correct (+ optional correct2/correct3 indices), explanation.

  *.html — saved snapshots of the rendered simulator (one per domain tab,
           with all questions submitted so the correct answers carry the
           `correct-answer` CSS class).

Run:

    python3 tools/parse_datasets.py

Questions are deduplicated by id across all files; JSON entries win over
HTML-snapshot entries for the same id.
"""

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASETS_DIR = ROOT / "datasets"
APP_JS = ROOT / "app.js"

START_MARKER = "// >>> QUESTIONS START"
END_MARKER = "// <<< QUESTIONS END"

# Maps the snapshot's quiz-tab title to the CATEGORIES constant in app.js
CATEGORY_CONSTANTS = {
    "Security & Access": "SECURITY",
    "Automation & Logic": "AUTOMATION",
    "Data Management": "DATA",
    "Sales & Service Apps": "APPS",
    "UI & Analytics": "UI",
    "Deployment & Sandboxes": "DEPLOY",
}

# Maps the JSON bank's numeric category to the CATEGORIES constant in app.js
CATEGORY_NUMBERS = {
    1: "SECURITY",
    2: "AUTOMATION",
    3: "DATA",
    4: "APPS",
    5: "UI",
    6: "DEPLOY",
}


def clean_text(fragment: str) -> str:
    """Strip tags/labels from an HTML fragment and normalize whitespace."""
    fragment = re.sub(
        r'<span class="multi-select-label">.*?</span>', "", fragment, flags=re.S
    )
    fragment = re.sub(r"<[^>]+>", "", fragment)
    return re.sub(r"\s+", " ", html.unescape(fragment)).strip()


def parse_snapshot(path: Path):
    text = path.read_text(encoding="utf-8")

    title_match = re.search(r'id="quiz-tab-title"[^>]*>(.*?)</h2>', text, re.S)
    title = clean_text(title_match.group(1)) if title_match else None
    category = CATEGORY_CONSTANTS.get(title)
    if title and category is None:
        print(f"  ! Unknown tab title {title!r} in {path.name}; "
              f"its questions will only appear in the Full Exam tab")

    chunks = re.split(r'<div class="question-card[^"]*" id="qcard-(\d+)">', text)
    questions = []
    for qid, chunk in zip(chunks[1::2], chunks[2::2]):
        text_match = re.search(r'<div class="question-text">(.*?)</div>', chunk, re.S)
        if not text_match:
            print(f"  ! qcard-{qid} in {path.name}: no question text, skipped")
            continue

        options, answers = [], []
        for opt in re.finditer(
            r'<div class="option-item([^"]*)"[^>]*>\s*'
            r'<div class="option-radio[^"]*"></div>\s*'
            r'<div class="option-letter">([A-Z])</div>\s*'
            r'<div class="option-text">(.*?)</div>',
            chunk,
            re.S,
        ):
            classes, letter, opt_text = opt.groups()
            options.append({"letter": letter, "text": clean_text(opt_text)})
            if "correct-answer" in classes:
                answers.append(letter)

        if not options or not answers:
            print(f"  ! qcard-{qid} in {path.name}: options or correct answers "
                  f"missing (was the question submitted before saving?), skipped")
            continue

        exp_match = re.search(
            r'<div class="explanation-panel"[^>]*>\s*<h4>.*?</h4>\s*<p>(.*?)</p>',
            chunk,
            re.S,
        )

        questions.append({
            "id": int(qid),
            "category": category,
            "text": clean_text(text_match.group(1)),
            "options": options,
            "answer": sorted(answers),
            "multi": len(answers) > 1,
            "explanation": clean_text(exp_match.group(1)) if exp_match else "",
        })
    return questions


def parse_json_bank(path: Path):
    entries = json.loads(path.read_text(encoding="utf-8"))
    questions = []
    for entry in entries:
        category = CATEGORY_NUMBERS.get(entry.get("category"))
        if category is None:
            print(f"  ! id {entry.get('id')} in {path.name}: unknown category "
                  f"{entry.get('category')!r}; it will only appear in the Full Exam tab")

        indices = sorted({
            i for i in (entry.get("correct"), entry.get("correct2"), entry.get("correct3"))
            if i is not None
        })
        if not entry.get("options") or not indices:
            print(f"  ! id {entry.get('id')} in {path.name}: options or correct "
                  f"answers missing, skipped")
            continue

        questions.append({
            "id": int(entry["id"]),
            "category": category,
            "text": re.sub(r"\s+", " ", entry["text"]).strip(),
            "options": [
                {"letter": chr(65 + i), "text": re.sub(r"\s+", " ", opt).strip()}
                for i, opt in enumerate(entry["options"])
            ],
            "answer": [chr(65 + i) for i in indices],
            "multi": len(indices) > 1,
            "explanation": re.sub(r"\s+", " ", entry.get("explanation", "")).strip(),
            "hook": re.sub(r"\s+", " ", entry.get("hook", "")).strip(),
        })
    return questions


def render_question(q) -> str:
    category = f"CATEGORIES.{q['category']}" if q["category"] else "null"
    options = ",\n".join(
        f"      {{letter:{json.dumps(o['letter'])}, text:{json.dumps(o['text'], ensure_ascii=False)}}}"
        for o in q["options"]
    )
    return (
        "  {\n"
        f"    id:{q['id']}, category: {category},\n"
        f"    text:{json.dumps(q['text'], ensure_ascii=False)},\n"
        "    options:[\n"
        f"{options}\n"
        "    ],\n"
        f"    answer:{json.dumps(q['answer'])}, multi:{json.dumps(q['multi'])},\n"
        f"    explanation:{json.dumps(q['explanation'], ensure_ascii=False)},\n"
        f"    hook:{json.dumps(q.get('hook', ''), ensure_ascii=False)}\n"
        "  }"
    )


def main():
    html_files = sorted(DATASETS_DIR.glob("*.html"))
    json_files = sorted(DATASETS_DIR.glob("*.json"))
    if not html_files and not json_files:
        sys.exit(f"No .html or .json files found in {DATASETS_DIR}")

    by_id = {}

    def add(q, authoritative):
        existing = by_id.get(q["id"])
        # JSON bank entries are authoritative; among snapshots, prefer the
        # copy that knows its domain (a domain tab beats a Full Exam tab)
        if (existing is None or authoritative
                or (existing["category"] is None and q["category"])):
            by_id[q["id"]] = q

    for path in html_files:
        print(f"Parsing {path.name} …")
        parsed = parse_snapshot(path)
        print(f"  {len(parsed)} questions extracted")
        for q in parsed:
            add(q, authoritative=False)

    for path in json_files:
        print(f"Parsing {path.name} …")
        parsed = parse_json_bank(path)
        print(f"  {len(parsed)} questions extracted")
        for q in parsed:
            add(q, authoritative=True)

    questions = sorted(by_id.values(), key=lambda q: q["id"])
    block = (
        f"{START_MARKER} (auto-generated by tools/parse_datasets.py — do not edit by hand)\n"
        "const QUESTIONS = [\n"
        + ",\n".join(render_question(q) for q in questions)
        + "\n];\n"
        f"{END_MARKER}"
    )

    app_source = APP_JS.read_text(encoding="utf-8")
    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.S
    )
    if not pattern.search(app_source):
        sys.exit(f"Markers {START_MARKER!r} / {END_MARKER!r} not found in {APP_JS}")
    APP_JS.write_text(pattern.sub(lambda _: block, app_source), encoding="utf-8")

    counts = {}
    for q in questions:
        counts[q["category"] or "(no domain)"] = counts.get(q["category"] or "(no domain)", 0) + 1
    print(f"\nWrote {len(questions)} questions to {APP_JS.name}:")
    for cat, n in sorted(counts.items()):
        print(f"  {cat}: {n}")


if __name__ == "__main__":
    main()
