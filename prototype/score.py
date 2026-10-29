"""
Deterministic scoring prototype (no AI, no API key needed).

Input : criteria.json (admin config) + facts.json (output of the AI extraction step)
Output: a ranked list with status, score and a per-criterion breakdown.

Run:  python score.py
Same inputs always give the same output. That is the point: AI reads the text,
plain code does the maths.
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
criteria = json.loads((HERE / "criteria.json").read_text())
facts = json.loads((HERE / "facts.json").read_text())
facts = {k: v for k, v in facts.items() if not k.startswith("_")}


# ---------- Step 1: mandatory pass/fail gate ----------
def gate(f):
    """Returns 'ineligible', 'flagged' or 'pass' plus a list of notes."""
    notes = []
    for name in ("licence", "wsib_and_insurance"):
        if f[name] == "no":
            return "ineligible", [f"mandatory check failed: {name}"]
        if f[name] == "not_stated":
            notes.append(f"mandatory item not stated: {name} (reviewer must check the PDF)")
    return ("flagged" if notes else "pass"), notes


# ---------- Step 2: per-criterion scores (each returns 0-100) ----------
def experience_score(f):
    for min_count, pts in criteria["experience_bands"]:
        if f["qualifying_installs"] >= min_count:
            return pts
    return 0


def price_score(f, lowest_price):
    if f["price_cad"] is None or f["price_cad"] > criteria["budget_ceiling_cad"]:
        return 0.0
    return 100.0 * lowest_price / f["price_cad"]


def timeline_score(f, shortest_weeks):
    w = f["weeks"]
    if w is None or w > criteria["max_weeks"]:
        return 0.0  # missing or over the limit: cannot earn points
    return 100.0 * shortest_weeks / w


def warranty_score(f):
    b = criteria["warranty_benchmarks"]
    panel = min(f["panel_warranty_years"] / b["panel_years"], 1)
    work = min(f["workmanship_warranty_years"] / b["workmanship_years"], 1)
    return 100.0 * (0.5 * panel + 0.5 * work)


def team_score(f):
    items = criteria["team_items"]
    return 100.0 * sum(1 for i in items if f[i]) / len(items)


# ---------- Step 3: run ----------
status, notes = {}, {}
for pid, f in facts.items():
    status[pid], notes[pid] = gate(f)

in_play = [p for p in facts if status[p] != "ineligible"]  # ineligible bids never affect normalisation

lowest_price = min(facts[p]["price_cad"] for p in in_play)
valid_weeks = [facts[p]["weeks"] for p in in_play
               if facts[p]["weeks"] is not None and facts[p]["weeks"] <= criteria["max_weeks"]]
shortest_weeks = min(valid_weeks)

results = []
for pid in in_play:
    f = facts[pid]
    parts = {
        "experience": experience_score(f),
        "price": price_score(f, lowest_price),
        "timeline": timeline_score(f, shortest_weeks),
        "warranty": warranty_score(f),
        "team": team_score(f),
    }
    total = sum(parts[k] * criteria["weights"][k] / 100 for k in parts)

    if f["integrity_flag"]:
        status[pid] = "flagged"
        notes[pid].append("instruction aimed at the AI/reviewer found in document (ignored)")
    if f["weeks"] is None:
        status[pid] = "flagged"
        notes[pid].append("completion time not stated: cannot confirm it meets the limit")
    start = f["installs_period_start_year"]
    if start is not None and start < criteria["window_start_year"]:
        notes[pid].append("experience period starts before the 5-year window: count may be overstated")

    results.append({"id": pid, "status": status[pid], "total": round(total, 1),
                    "parts": {k: round(v, 1) for k, v in parts.items()}, "notes": notes[pid]})

ranked = sorted([r for r in results if r["status"] == "pass"],
                key=lambda r: (-r["total"], -r["parts"]["price"], r["id"]))  # fixed tie-break
for i, r in enumerate(ranked, 1):
    r["status"], r["rank"] = "ranked", i
for r in results:
    r.setdefault("rank", None)

print(f"Criteria {criteria['category']} {criteria['version']}\n")
for r in sorted(results, key=lambda r: (r["rank"] is None, r["rank"] or 0, r["id"])):
    label = f"#{r['rank']}" if r["rank"] else r["status"].upper()
    print(f"{r['id']}  {label:<8} total={r['total']:>5}  {r['parts']}")
    for n in r["notes"]:
        print(f"      note: {n}")
for pid in facts:
    if status[pid] == "ineligible":
        print(f"{pid}  INELIGIBLE  {notes[pid][0]}")

# ---------- Step 4: check against ranking.json ----------
expected = {e["proposal"]: e for e in json.loads((HERE.parent / "ranking.json").read_text())}
ok = True
for r in results:
    e = expected[r["id"]]
    if e["status"] == "ranked" and not (e["rank"] == r["rank"] and e["score"] == r["total"]):
        ok = False
    if e["status"] != "ranked" and e["status"] != r["status"]:
        ok = False
for pid in facts:
    if status[pid] == "ineligible" and expected[pid]["status"] != "ineligible":
        ok = False
print("\nMatches ranking.json:", "YES" if ok else "NO")
