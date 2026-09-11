# Sales Cloud Consultant Question Bank — Build Notes

`sales-consultant.json` was built from `datasets/source-snapshots/sales-consultant/Sales-Cloud-Consultant.pdf` (DXperience dump, v33.3, 2026-08-31, 64 pages, "Salesforce Certified Agentforce Sales Consultant" header) on 2026-09-11.

## Source → bank

- `tools/parse_sales_consultant_pdf.py` extracts the 190 `Question: N / A. B. C. / Answer: X` blocks into `sales-consultant-raw.json`.
- The PDF has **no explanations** — all 190 were written from Salesforce documentation and consulting best practice.
- All questions are single-answer with 3 options (one 4-option question, Q117, was a parse artifact — see below).
- No duplicate questions within the PDF.

Final bank: **190 questions**.

| Category | Questions |
|---|---|
| Product Knowledge & Integration | 35 |
| Data, Reports & Dashboards | 28 |
| Implementation Strategies | 26 |
| Lead & Campaign Management | 25 |
| Account & Contact Management | 22 |
| Consulting Practices | 22 |
| Sales Life Cycle & Forecasting | 20 |
| Opportunity Management | 12 |

Categories map to the official exam outline with two merges: *Implementation Strategies* and *Consulting Practices* stay separate; *Sales Life Cycle* absorbs forecasting/territories/quotas; *Application of Product Knowledge* absorbs *Sales Productivity & Integration*; *Sales Metrics, Reports & Dashboards* absorbs *Data Management*.

## Answer keys

The dump key was reviewed question by question. **20 keys were changed** where the dump is contradicted by Salesforce documentation:

| Q | Dump | Bank | Reason |
|---|---|---|---|
| 14 | B | A | Lead Settings has *Enable Conversions for Salesforce Mobile* — no Global Action needed |
| 16 | A | B | Account Hierarchy is display-only; it never grants record access |
| 50 | A | C | Only Overlay splits may total less than 100% |
| 64 | B | C | "Activities that drive sales" → meetings held, not opportunities created |
| 72 | C | B | Contacts to Multiple Accounts preserves history as a contractor changes companies |
| 75 | C | A | Under Public Read-Only, a rep edits only opportunities they own |
| 76 | B | C | Report subscriptions let managers control email frequency |
| 78 | C | B | Private OWD + public group → sharing rule; no "object default visibility for a group" exists |
| 81 | A | B | Budget/priority governance belongs to an executive steering committee |
| 84 | A | B | Adoption KPI is logins, not Closed Lost |
| 88 | A | C | Build in a Developer sandbox, test in a staging environment |
| 113 | A | C | Cumulative Forecast Rollups give the across-categories view |
| 127 | A | C | Partner churn is tracked on Accounts, not Opportunities |
| 137 | C | A | Only one territory model can be active — the key migration consideration |
| 145 | A | C | Retire a product by unchecking Active; it can't be deleted while on opportunities |
| 159 | B | C | Run assignment rules in Planning; activation isn't needed to view results |
| 173 | C | B | Documenting use cases starts with discovery, not a data merge |
| 177 | A | B | View-all/edit-own → Public Read-Only OWD |
| 182 | B | A | Training deliverables are defined in the SOW Scope section |
| 189 | C | A | Roll-ups need master-detail; Account Hierarchy is a lookup → use a flow |

**Judgment calls** (kept as decided but worth a second look): Q14, 25, 53, 64, 75, 76, 87, 88, 102, 105, 113, 118, 126, 127, 137, 149, 184, 186, 190 — listed in `datasets/source-snapshots/sales-consultant/flagged-questions.json`.

## Other fixes

- **Q117** — the question stem bled into option A in the PDF; stem restored, options re-lettered A–C, key kept on "Forecast Type on Opportunity Product grouped by Product Family".
- OCR cleanup across stems/options: `dat a`→`data`, `formul a`→`formula`, `Sales Could`→`Sales Cloud`, stray capitalised `In/Is/Items/Information`, `4 custom field`→`a custom field`, `@ report`→`a report`, `assignedsales`, `flied`→`field`, broken hyphens (`real- time`, `Read- Only`), curly quotes.

## Registration

Exam `sales-cloud-consultant` added to `exams.json` and the embedded `EXAM_REGISTRY` in `app.js` (passing score 62%, 105 minutes, 190 questions). Code shown as `SALES-CLOUD-CONSULTANT` (from the PDF) — rename if a PLAT-style code is preferred.
