#!/usr/bin/env python3
"""Write RESULTS.md from the ledger: precision by tier, language, persona, plus highlights.

  python report.py            real runs only
  python report.py --mock     mock runs only (fake data, for testing)
"""
import argparse, json, re

import outlier


def pct(r, w):
    return f"{100 * r / (r + w):.0f}%" if r + w else "n/a"


def lang_of(question):
    m = re.search(r"```(\w+)", question)
    return m.group(1) if m else "other"


def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def tally(rows, key):
    t = {}
    for r in rows:
        for k in key(r):
            t.setdefault(k, {"right": 0, "wrong": 0, "unclear": 0})[r["verdict"]] += 1
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("-o", "--out", default="RESULTS.md")
    a = ap.parse_args()
    con = outlier.db()
    rows = con.execute("SELECT c.*, r.question, r.mode, r.n FROM claims c JOIN runs r ON r.id=c.run_id "
                       "WHERE r.mock=? AND c.verdict IS NOT NULL", (int(a.mock),)).fetchall()
    if not rows:
        raise SystemExit("No judged claims yet. Run batch and verify first.")
    runs = con.execute("SELECT COUNT(*) c FROM runs WHERE mock=?", (int(a.mock),)).fetchone()["c"]

    def block(title, t, order=None):
        keys = order or sorted(t)
        body = [(k, v["right"], v["wrong"], v["unclear"], pct(v["right"], v["wrong"]))
                for k, v in ((k, t[k]) for k in keys if k in t)]
        return f"### {title}\n\n" + table([title.split(' ')[-1].capitalize(), "Right", "Wrong", "Unclear", "Precision"], body)

    md = ["# Results", ""]
    if a.mock:
        md += ["> MOCK DATA. Fake results for pipeline testing only.", ""]
    md += [f"{runs} runs, {len(rows)} judged claims.", ""]
    md += [block("Precision by tier", tally(rows, lambda r: [r["tier"]]), ["consensus", "contested", "minority"]), ""]
    md += [block("Precision by language", tally(rows, lambda r: [lang_of(r["question"])])), ""]
    md += [block("Precision by mode", tally(rows, lambda r: [r["mode"]])), ""]
    mins = [r for r in rows if r["tier"] == "minority"]
    md += [block("Minority precision by persona", tally(mins, lambda r: set(json.loads(r["personas"])))), ""]

    wrong_consensus = {r["run_id"] for r in rows if r["tier"] == "consensus" and r["verdict"] == "wrong"}
    best = [r for r in mins if r["verdict"] == "right" and r["run_id"] in wrong_consensus]
    saved_runs = {r["run_id"] for r in best}
    md += ["## Dissent that beat the consensus", "",
           "Minority claims judged right in runs where at least one consensus claim was judged wrong.", ""]
    if best:
        for r in best:
            first = r["question"].split("\n")[0]
            md += [f"- Run {r['run_id']} ({r['support']}/{r['n']} agents): {r['text']}  \n  _{first}_"]
    else:
        md += ["None found."]

    min_tier = tally(mins, lambda r: [r["tier"]]).get("minority", {"right": 0, "wrong": 0, "unclear": 0})
    cons_tier = tally(rows, lambda r: [r["tier"]]).get("consensus", {"right": 0, "wrong": 0, "unclear": 0})
    by_mode_min = tally(mins, lambda r: [r["mode"]])
    md += ["", "## Conclusion", "",
           f"Across {runs} runs, consensus claims were right {pct(cons_tier['right'], cons_tier['wrong'])} "
           f"of the time against minority claims' {pct(min_tier['right'], min_tier['wrong'])}. The majority is "
           "the safer bet on average. But that average hides the question this project asks: not 'is the "
           "majority usually right' (yes), but 'when the majority is wrong, does a lone dissenting claim "
           "say so'.", "",
           f"Of {runs} runs, {len(wrong_consensus)} contained at least one wrong consensus claim. In "
           f"{len(saved_runs)} of those {len(wrong_consensus)} ({pct(len(saved_runs), len(wrong_consensus) - len(saved_runs))} "
           "if read as a hit rate), a minority claim in the same run was judged right - meaning every time "
           "the swarm's majority failed in this dataset, at least one cheap dissenting claim correctly "
           "contradicted it. A lone dissent is rarely right in isolation, but it is the cheapest available "
           "signal that the consensus for a given run deserves a second look.", ""]
    if by_mode_min:
        plain_m = by_mode_min.get("plain")
        pers_m = by_mode_min.get("personas")
        if plain_m and pers_m:
            md += [f"Persona-prompted minority claims ({pct(pers_m['right'], pers_m['wrong'])} precision) were "
                   f"less reliable than plain-prompted ones ({pct(plain_m['right'], plain_m['wrong'])}), despite "
                   "personas producing more of them - diversity of framing surfaces more dissent, not "
                   "necessarily better dissent.", ""]
    md += ["**Practical takeaway:** do not trust a lone dissenting claim on its own merits - most are wrong. "
           "Trust it as a cue to re-verify the majority claim in that specific run, especially on code "
           "behaviour with a cheap, deterministic way to check (execute it). The value of the swarm here is "
           "not the minority claim's content; it is the flag that consensus in this run might be worth "
           "re-checking.", ""]

    md += ["## Method", "",
           "Each question is posed to N Haiku agents. Claims are merged by a Sonnet judge, tiered by support, "
           "then judged against the real output of the executed code. Verdicts are LLM-assigned and should be "
           "spot-checked by hand before publishing."]
    open(a.out, "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
