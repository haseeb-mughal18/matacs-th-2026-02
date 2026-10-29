# Write-up (MATACS-TH-2026-02)

**Idea in one line:** AI only *reads* proposals and copies facts out. Plain code *decides* (pass/fail, scores, ranking). A human confirms everything before it matters.

**Assumptions:** the award is in 2026, so "last 5 years" means 2021 onward. If a number is missing, the tool never guesses. It flags the proposal. See the [diagram](diagram/process-flow.png).

## 1. AI vs. rules

**AI (2 steps):**
- **Extraction:** turns messy proposal text into fixed fields (licence, price, weeks, warranty years...) with a word-for-word quote and page number for each.
- **Reason writing:** turns finished scores into one readable sentence. It cannot change any number.

**Plain code or rules:** upload checks, PDF-to-text, locking the criteria version, quote verification, injection pattern scan, mandatory pass/fail, weighted maths, sorting, tie-breaks, audit log.

**Why the line is here:** AI is good at understanding unstructured language. Code is better where the answer must be exact, repeatable and defensible. An AI-given score could differ between runs and nobody could show *why*. So AI never scores or ranks.

## 2. Consistency and explainability

- **Scores come from formulas.** Each criterion has a written rule in the admin config (for example, price points = lowest eligible price ÷ this price × 100). Same facts plus same criteria version always give the same scores and order. Ties break the same way every time (higher price score, then proposal letter).
- **The only variable part is extraction.** To keep it stable: temperature 0, fixed JSON schema, pinned model version, and code checks every quote exists in the PDF text. Extracted facts are saved against the file's hash, so ranking the same files twice reuses them and gives an identical result. A fresh re-extraction runs twice, and any field that differs is flagged. AI at temperature 0 is *mostly* but not *guaranteed* identical, hence the saved facts and double-run check.
- **Reviewer view:** for each proposal, a table: criterion, extracted fact, rule applied, points, weight, and a link to the quote on the PDF page. The one-line reason is generated from this table, so the table is the real explanation.

## 3. Human in the loop

1. **Extraction review.** Flagged or unverified facts are shown beside the PDF page. The reviewer can correct a fact. Scores then recompute automatically.
2. **Results review.** Three lanes: *Ranked*, *Flagged* (needs a decision) and *Ineligible*. The reviewer must clear or confirm every flag, and can move a proposal in or out. Any override needs a written reason. An override is stored *next to* the tool's result, never replacing it.
3. **Award.** Always a human decision, outside the tool. The tool never awards anything.

**Audit log:** batch ID; who and when; file hashes; criteria version; model and prompt versions; raw AI output; quote-check results; flags; scores; every edit or override (before, after, reason, user); exported report.

## 4. Changing criteria

- Criteria are **versioned and never edited in place**. Saving a change creates a new version (weights must total 100 before saving).
- A batch is scored under one version only. Old results stay reproducible and are marked "scored under v1, current is v2".
- **Re-score is a button, creating a new run** (the old run is kept, and both can be compared). If only weights or thresholds changed, it uses saved facts and needs **no AI call**. If a criterion was added or redefined, only that field is re-extracted.
- Changing a mandatory criterion can change who is eligible, so the gate runs again and the reviewer sees who moved. Versions are never mixed in one ranking.

## 5. Risks and safeguards

| Risk | Safeguard |
|---|---|
| **Wrong extraction** (misread number, wrong page, scanned PDF) | Quote must exist in source text; schema validation; retry once; low-quality or unreadable scans flagged; reviewer checkpoint 1. |
| **Made-up facts** | The prompt forbids guessing, and "not stated" is a valid answer. Missing means flagged, never filled in. Reason sentences can only use numbers from the results, checked by code. |
| **Prompt injection / manipulation** (hidden text telling the AI to rank a bid first) | Proposal text is wrapped as data and the model is told never to obey it. A separate pattern scan runs in code. Any hit is flagged to a human and the instruction has no effect on scoring. |
| **Bias** (favouring big firms, nicer formatting, company names) | Scoring uses only extracted criteria facts, never company name or document style. Formulas are fixed and visible. Overrides are audited, so patterns can be reviewed. |
| **Gaming the formulas** (very low price, vague promises) | Ineligible bids are removed *before* price is normalised, so they cannot distort other scores. Vague or deferred promises count as "not stated". |
| **Cost** | AI is called once per proposal and cached by file hash. Re-scoring uses no AI. Size and batch limits on uploads. A smaller model handles extraction. |
| **Over-trust in the ranking** | Scores are decision support. Flags are shown first and the award stays human. |

## How the design handles the sample set

Full detail is in [ranking.json](ranking.json), and [prototype/score.py](prototype/score.py) reproduces the numbers.

- **A** and **E** pass everything and are ranked 1 and 2.
- **B** fails the licence rule, since the bidder does not hold it and plans to use a subcontractor to be confirmed after award. It is *ineligible*, and its low price is ignored.
- **C** contains hidden text addressed to automated reviewers. It is ignored and reported. C is *flagged* for a human, not ranked first and not silently dropped. If cleared, it would score third.
- **D** gives no completion time, so the 16-week limit cannot be checked. It is *flagged* and not given the benefit of the doubt.
- **Rubric choices** (experience bands, warranty benchmarks) are admin-set examples. Different values change the scores, not the process.
