#!/usr/bin/env python3
"""Parse the Sales Cloud Consultant dump PDF into a raw question list.

Usage:  python3 tools/parse_sales_consultant_pdf.py
Reads   datasets/source-snapshots/sales-consultant/Sales-Cloud-Consultant.pdf  (via pdftotext -layout)
Writes  datasets/source-snapshots/sales-consultant/sales-consultant-raw.json

Same DXperience "Question: N / A. / Answer: X" layout as the App Builder dump, but this
PDF carries no explanations. Output items: {num, text, options:[str], answer:[letters], multi}.
Category + explanation are added in a later step; the final bank is sales-consultant.json.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "datasets/source-snapshots/sales-consultant/Sales-Cloud-Consultant.pdf"
OUT = ROOT / "datasets/source-snapshots/sales-consultant/sales-consultant-raw.json"

NOISE = re.compile(
    r"(Questions & Answers PDF|dumpsschool\.com|Product Questions:|^Version:|"
    r"Salesforce Certified Agentforce Sales Consultant|SALES-CLOUD-CONSULTANT|^P-\d+$|"
    r"Thank You for Purchasing|Test Your Preparation|Practice Exam Software|Coupon|Download Free)",
    re.I,
)


def clean_lines(block):
    out = []
    for ln in block.splitlines():
        s = re.sub(r"\s*P-\d+\s*$", "", ln.strip())
        if s and NOISE.search(s):
            continue
        if s in ("Salesforce", "PDF"):
            continue
        out.append(s)
    return out


def parse_block(num, lines):
    qlines, opts = [], []
    ans = None
    state = "q"
    cur_letter, cur_opt = None, []

    def flush():
        nonlocal cur_letter, cur_opt
        if cur_letter is not None:
            opts.append((cur_letter, " ".join(cur_opt).strip()))
        cur_letter, cur_opt = None, []

    for ln in lines:
        m_ans = re.match(r"Answer:\s*([A-E][A-E,\s]*)", ln)
        m_opt = re.match(r"^([A-E])\.\s+(.*)$", ln)
        if state in ("q", "opt"):
            if m_ans:
                flush(); ans = re.findall(r"[A-E]", m_ans.group(1)); state = "ans"; continue
            if m_opt:
                flush(); cur_letter, cur_opt = m_opt.group(1), [m_opt.group(2)]; state = "opt"; continue
            if ln:
                (qlines if state == "q" else cur_opt).append(ln)
        # anything after the answer line is page furniture; ignore

    text = re.sub(r"\s+", " ", " ".join(qlines)).strip()
    text = re.sub(r"\s*Choose\s+\w+\s+answers?\.?\s*$", "", text, flags=re.I).strip()
    options = [re.sub(r"\s+", " ", t) for _, t in sorted(opts, key=lambda x: x[0])]
    return {
        "num": num,
        "text": text,
        "options": options,
        "answer": sorted(ans) if ans else [],
        "multi": bool(ans and len(ans) > 1),
    }


def main():
    if not PDF.exists():
        sys.exit(f"PDF not found: {PDF}")
    txt = subprocess.run(["pdftotext", "-layout", str(PDF), "-"],
                         capture_output=True, text=True).stdout
    parts = re.split(r"\nQuestion:\s*(\d+)\s*\n", "\n" + txt)
    questions = [parse_block(int(parts[i]), clean_lines(parts[i + 1]))
                 for i in range(1, len(parts), 2)]

    bad = [q["num"] for q in questions
           if len(q["options"]) < 2 or not q["answer"]
           or any(ord(l) - 65 >= len(q["options"]) for l in q["answer"])]
    OUT.write_text(json.dumps(questions, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"Parsed {len(questions)} questions -> {OUT.name}")
    print(f"Multi-answer: {sum(1 for q in questions if q['multi'])}")
    print("Option-count distribution:",
          {n: sum(1 for q in questions if len(q['options']) == n)
           for n in sorted({len(q['options']) for q in questions})})
    print(f"⚠ parse problems: {bad}" if bad else "All questions have >=2 options and an in-range answer ✓")


if __name__ == "__main__":
    main()
