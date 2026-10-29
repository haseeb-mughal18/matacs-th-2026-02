# MATACS-TH-2026-02: AI Proposal Triage Design

- **Name:** <<FILL: your full name>>
- **Reference:** MATACS-TH-2026-02
- **Role:** Associate Software Developer
- **Time actually spent:** <<FILL: your real time, e.g. "about 2 hours (60 min design + 60 min reviewing and editing)">>

## Summary

A design for an AI-assisted proposal triage tool. AI is used only to read proposals and copy facts out (and later to write one-line reasons). Plain code does the pass/fail checks, scoring and ranking, so results are repeatable and explainable. A human reviews at two checkpoints and makes the final award decision.

## Files

| File | What it contains |
|---|---|
| [WRITEUP.md](WRITEUP.md) | Answers to the five questions (under 1,000 words) |
| [diagram/process-flow.png](diagram/process-flow.png) | Process flow from upload to ranked output, showing AI steps, rule steps and human checkpoints |
| [PROMPTS.md](PROMPTS.md) | The extraction prompt and the reason-writer prompt, as I would send them |
| [ranking.json](ranking.json) | Expected ranking of proposals A to E |
| [prototype/score.py](prototype/score.py) | Optional. Small script that applies the scoring rules to extracted facts and checks them against ranking.json (run `python prototype/score.py`; no API key or install needed) |
| [prototype/criteria.json](prototype/criteria.json) | Optional. Example admin criteria config used by the script |
| [prototype/facts.json](prototype/facts.json) | Optional. Facts per proposal (numbers and yes/no only, no proposal text) |

Proposals are referred to by letter (A to E) only. No brief or sample proposal text is copied into this repository.

## How I used AI tools

<<FILL: write 2 to 3 sentences in your own words. Say which tool(s) you used (for example Claude) and what for (for example drafting the write-up, the prompts and the diagram script). Then include at least ONE real place where you disagreed with or corrected the AI's output, and explain why.>>

<!-- Ideas for a genuine disagreement. Use one ONLY if it is true for you after you review the design:
     - You changed how C is handled (ranked with a note instead of flagged), or kept it flagged and can explain why.
     - You changed how B is handled (flagged for a human instead of ineligible).
     - You changed a rubric choice (experience bands, warranty benchmark, how a missing timeline is scored).
     - You shortened or corrected something in the write-up that was wrong or unclear.
     Delete this comment before pushing. -->
