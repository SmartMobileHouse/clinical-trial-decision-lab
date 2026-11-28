"""Addendum to the same-day repeat check, written after an independent review of it (28 November 2026). Exploratory.

The review pointed out that (1) comparing separate ranges hides differences between measurements made on the same papers,
(2) the direction counts mixed real answer flips with invalid answers, and (3) the accuracy reported was balanced accuracy,
not paper-level accuracy. This script adds the paired comparison, the valid-flip counts and paper-level accuracy.
Writes same-day-repeat-addendum.json."""
import json, random, statistics as st
from pathlib import Path
SRC = Path(__file__).resolve().parent
T = SRC.parents[2] / "screening-check/trialpanorama"
SEED, DRAWS = 20261122, 10000
rows = {}
for l in open(T / "final-corrected/sample.jsonl"):
    r = json.loads(l); rows[f'{r["review"]}|{r["pmid"]}'] = r
changed = {f'{c["review"]}|{c["pmid"]}' for c in json.load(open(T / "final-corrected/changed.json"))}
same = [i for i in rows if i not in changed]
fams = sorted({r["review"] for r in rows.values()}); by = {f: [i for i in same if rows[i]["review"] == f] for f in fams}
y = {i: int(r["label"]) for i, r in rows.items()}
rng = random.Random(SEED); DRAW = [[rng.choice(fams) for _ in fams] for _ in range(DRAWS)]
def load(path):
    sc = {}
    for l in open(SRC / path):
        p = json.loads(l); pr = (p.get("probabilities") or {}).get("included")
        if p.get("status", "ok") == "ok" and isinstance(pr, (int, float)) and 0 <= pr <= 1: sc[p["case_id"]] = pr
    return sc
FILE = {"gpt": "llm_openai_prob.jsonl", "haiku": "llm_anthropic_prob.jsonl"}
RUN = {"d1": "final-pass1-prob", "d2": "corrected-pass1-prob", "a": "same-day-a-prob", "b": "same-day-b-prob"}
res = {"same_text_papers": len(same), "models": {}}
for m, fn in FILE.items():
    P = {k: load(f"{v}/{fn}") for k, v in RUN.items()}
    dis = lambda u, v: {i: int(not (i in P[u] and i in P[v] and ((P[u][i] >= .5) == (P[v][i] >= .5)))) for i in same}
    D = {"d1_d2": dis("d1", "d2"), "a_b": dis("a", "b"), "d2_a": dis("d2", "a"), "d1_a": dis("d1", "a")}
    def excess(x, z):
        f = lambda fl: st.mean(D[x][i] - D[z][i] for g in fl for i in by[g])
        v = sorted(f(d) for d in DRAW); return {"points": f(fams) * 100, "low": v[int(.025 * DRAWS)] * 100, "high": v[int(.975 * DRAWS) - 1] * 100}
    a, b = P["a"], P["b"]
    valid = [i for i in same if i in a and i in b and ((a[i] >= .5) != (b[i] >= .5))]
    acc = lambda sc, ids: sum((i in sc) and ((sc[i] >= .5) == bool(y[i])) for i in ids) / len(ids)
    res["models"][m] = {
        "excess_d1_d2_over_same_day": excess("d1_d2", "a_b"), "excess_d1_d2_over_d2_a": excess("d1_d2", "d2_a"), "excess_d1_d2_over_d1_a": excess("d1_d2", "d1_a"),
        "excess_d2_a_over_same_day": excess("d2_a", "a_b"),
        "same_day_valid_flips": len(valid), "same_day_valid_toward": sum((b[i] >= .5) == bool(y[i]) for i in valid), "same_day_valid_away": sum((a[i] >= .5) == bool(y[i]) for i in valid),
        "same_day_invalid_pairs": sum(1 for i in same if i not in a or i not in b),
        "paper_accuracy_same_text": {k: acc(P[k], same) for k in RUN}, "paper_accuracy_all": {k: acc(P[k], list(rows)) for k in ("d2", "a", "b")},
    }
json.dump(res, open(SRC / "same-day-repeat-addendum.json", "w"), indent=1); print(json.dumps(res, indent=1))
