# PLAT-ADMN-301 Question Bank — Fixes Applied

This documents the corrections applied to `datasets/plat-admn-301-questions.json` (the source of truth that `tools/parse_datasets.py` compiles into `app.js`). The original scraped bank is preserved at `plat-admn-301-questions.orig.json`.

## Final bank

- **255 questions** (56 multi-select), all with clean explanations

| Domain | Questions |
|---|---|
| Security & Access | 61 |
| Automation & Logic | 52 |
| Data Management | 52 |
| Sales & Service Apps | 27 |
| UI & Analytics | 42 |
| Deployment & Sandboxes | 21 |
| **Total** | **255** |

## What was fixed

**Answer keys corrected (29 total):**
- 25 from the documentation audit (e.g. Q119 Partial→Developer sandbox, Q16 flow-dependency, Q163 roll-up AVG, Q54 FLS, Q87 daily-backup, Q215 junction delete).
- 2 corroborated by a second scraped bank (Q86 junction read-on-both-masters, Q219 summary report).
- 2 from adjudicating cross-bank conflicts against Salesforce Help (Q101 advanced currency management, Q28 pre-deployment backup).

**Structural repairs (4):** Q173 (answer text had leaked into the stem; option split across two entries), Q44 (missing Template1/Template2 numerals), Q17 (missing question sentence), Q214 (missing scenario).

**Typos:** ~200 spelling/garbling defects fixed across question text, options, and explanations (OCR artifacts like "Northen", "Soles reps", "Salesforce,id", "Organi2ation").

**Explanations:** 200 rewritten — every truncated, missing, or wrong-answer-defending explanation now justifies the verified key in 2–4 sentences. All 255 questions now have clean explanations with no "Reference:" fragments or dump marketing text.

**New questions (34):** unique questions from a second Spanish-language simulator snapshot were categorized, typo-cleaned, key-checked, and appended (ids 223–256).

## How to regenerate

Edit `datasets/plat-admn-301-questions.json`, then run `python3 tools/parse_datasets.py` to rewrite the QUESTIONS block in `app.js`. Raw source snapshots are archived in `datasets/source-snapshots/` (ignored by the parser).