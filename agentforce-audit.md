# Agentforce Specialist Question Bank — Verification vs. PDF Sources

Verifies `agentforce.json` against the three PDFs in `datasets/source-snapshots/agentforce/` (2026-09-11).

## Sources

| File | Pages | Questions | Created | Notes |
|---|---|---|---|---|
| `Agentforce-Specialist (1).pdf` | 440 | 379 | 2026-07-06 | "Spring 26 Update", v13.2 — **newest, used as primary** |
| `Salesforce Agentforce Specialist.pdf` | 269 | 364 | 2026-06-08 | Older; every question also appears in the newer PDF |
| `AGENT SPE.pdf` | 269 | 364 | 2026-06-08 | **Byte-identical** to the file above (same MD5) — ignored |

## Coverage

- **Every one of the 367 original bank questions was found in both PDFs** (355 exact / 12 fuzzy matches vs. the older PDF; 323 / 44 vs. the newer one — fuzz is OCR noise only).
- The newer PDF has 12 questions the bank lacked. 11 are reworded duplicates of questions already in the bank (same options, same key). One was a genuinely different variant and was **added as Q368**.
- The older PDF contributes nothing the newer one doesn't have.

Final bank: **368 questions**, all single-answer, all with explanations.

| Category | Questions |
|---|---|
| Agentforce Concepts | 113 |
| Prompt Engineering | 76 |
| Setup & Integration | 73 |
| Agentforce & Data | 71 |
| Trust Layer & Security | 35 |

## Answer-key verification

The two unique PDFs agree with each other on every shared question. The bank disagreed with them on 18 questions. Each was adjudicated against Salesforce documentation rather than taken on faith — the PDFs are braindumps and in 9 of the 18 cases the PDF's *own explanation argues for the bank's answer* while its key says otherwise.

**Bank corrected (3):**
- **Q60** A→C — related-list grounding in Prompt Builder exposes the fields from the object's page layout; there is no per-field picker for related lists. (The newer PDF's variant of this question also keys the layout answer.)
- **Q110** B→C — audit-data collection is enabled on the Einstein Feedback setup page; "request audit data from the Security section" doesn't exist.
- **Q202** A→B — Flow grounding of prompt templates uses a Template-Triggered Prompt Flow, not a Data Cloud-triggered flow.

**Bank kept, PDF key judged wrong (13):** Q40, Q49 (Agent/Copilot Builder tests utterances, not Model Playground), Q50, Q68, Q85 (Add Prompt Instructions), Q153, Q162 (Dynamic Forms), Q220, Q244, Q300, Q352, Q364, Q367.

**Bank kept but still a judgment call (flagged in `datasets/.../flagged-questions.json`):** Q89, Q91 (Digital Wallet vs. Testing Center), Q191 (Apex vs. External Object merge fields), Q207 (SDR channel), Q227 (Agent Insights vs. Optimization — neither source's name matches current product naming cleanly), Q282 (Agent Script `run` placement — the newer PDF contradicts itself across two variants).

## Other fixes

- **Q238** — options B and C had been fused into one option in every source (OCR defect). Split back into two options; key stays on "adheres to the permissions, FLS, and sharing configured in the flow".
- **25 empty explanations** written (Q27, 37, 44, 55, 59, 60, 81, 85, 89, 91, 113, 147, 162, 182, 185, 191, 198, 207, 227, 281, 288, 294, 295, 306, 323).
- **OCR typos** cleaned in 80 question/option fields: `user 's`→`user's` (37×), `Al`→`AI`, `Epstein`→`Einstein`, `Eternal Object`→`External Object`, `paae`→`page`, `apcMopnete`→`appropriate`, `held-level`→`field-level`, `Contest:`→`Context:`, truncated "An Agentforce …"→"An Agentforce Specialist …" (31×).
- `count` bumped 367→368 in `exams.json` and the embedded registry in `app.js`.

## Reproducing

Extraction/comparison was done with `pdftotext -layout` plus a small parser (Word PDF: `Multiple Choice … Correct Answer:` blocks; DX PDF: `Question: N … Answer:` blocks), matching on normalized question text and comparing keys by option *text* since letter order differs between sources.
