"""Same-day repeat check for the two general models. Written before any request of the check was sent.
See reports/Same-day repeat check plan.md. Writes same-day-repeat.json. Usage: python same_day_repeat_analysis.py"""
import json, random, statistics as st
from pathlib import Path

SRC = Path(__file__).resolve().parent
T = SRC.parents[2] / "screening-check/trialpanorama"
SEED, DRAWS = 20261122, 10000
rows = {}
for l in open(T / "final-corrected/sample.jsonl"):
    r = json.loads(l); rows[f'{r["review"]}|{r["pmid"]}'] = r
changed = {f'{c["review"]}|{c["pmid"]}' for c in json.load(open(T / "final-corrected/changed.json"))}
same_text = set(rows) - changed
fams = sorted({r["review"] for r in rows.values()}); ids_by_fam = {f: [i for i, r in rows.items() if r["review"] == f] for f in fams}
y = {i: int(r["label"]) for i, r in rows.items()}
rng = random.Random(SEED); DRAW = [[rng.choice(fams) for _ in fams] for _ in range(DRAWS)]

def load(path):
    sc = {}
    for l in open(SRC / path):
        p = json.loads(l)
        pr = (p.get("probabilities") or {}).get("included")
        if p.get("status", "ok") == "ok" and isinstance(pr, (int, float)) and 0 <= pr <= 1: sc[p["case_id"]] = pr
    return sc

FILE = {"gpt": "llm_openai_prob.jsonl", "haiku": "llm_anthropic_prob.jsonl"}
RUN = {"day1": "final-pass1-prob", "day2": "corrected-pass1-prob", "day3a": "same-day-a-prob", "day3b": "same-day-b-prob"}
P = {m: {d: load(f"{folder}/{FILE[m]}") for d, folder in RUN.items()} for m in FILE}
ok = lambda sc, i: i in sc and ((sc[i] >= .5) == bool(y[i]))

def compare(a, b, keep):
    ids = [i for i in rows if i in keep]
    diff = {i: int(not (i in a and i in b and ((a[i] >= .5) == (b[i] >= .5)))) for i in ids}
    v = sorted(sum(diff[i] for f in d for i in ids_by_fam[f] if i in diff) / max(1, sum(1 for f in d for i in ids_by_fam[f] if i in diff)) for d in DRAW)
    flips = [i for i in ids if diff[i]]; both = [i for i in ids if i in a and i in b]
    acc = lambda sc: (sum(ok(sc, i) for i in ids if y[i]) / sum(1 for i in ids if y[i]) + sum(ok(sc, i) for i in ids if not y[i]) / sum(1 for i in ids if not y[i])) / 2
    return {"records": len(ids), "answers_changed": len(flips), "share_changed": len(flips) / len(ids), "range": [v[int(.025 * DRAWS)], v[int(.975 * DRAWS) - 1]],
            "missing_or_invalid": sum(1 for i in ids if i not in a or i not in b),
            "toward_label": sum(ok(b, i) for i in flips), "away_from_label": sum(ok(a, i) for i in flips),
            "identical_probability": sum(abs(a[i] - b[i]) <= 1e-9 for i in both) / len(both), "mean_absolute_probability_change": st.mean(abs(a[i] - b[i]) for i in both),
            "accuracy_first": acc(a), "accuracy_second": acc(b)}

res = {"papers": len(rows), "same_text_papers": len(same_text), "models": {}}
for m in FILE:
    p = P[m]
    res["models"][m] = {
        "within_day_all": compare(p["day3a"], p["day3b"], set(rows)),
        "across_days_26_to_28_all": compare(p["day2"], p["day3a"], set(rows)),
        "within_day_same_text": compare(p["day3a"], p["day3b"], same_text),
        "across_days_26_to_28_same_text": compare(p["day2"], p["day3a"], same_text),
        "across_days_25_to_26_same_text": compare(p["day1"], p["day2"], same_text),
        "across_days_25_to_28_same_text": compare(p["day1"], p["day3a"], same_text),
    }
json.dump(res, open(SRC / "same-day-repeat.json", "w"), indent=1)
for m, v in res["models"].items():
    print(m)
    for k, c in v.items():
        print(f'  {k:32s} {c["answers_changed"]:4d} of {c["records"]:4d} = {c["share_changed"]:.1%} ({c["range"][0]:.1%} to {c["range"][1]:.1%}) | toward {c["toward_label"]}, away {c["away_from_label"]} | same prob {c["identical_probability"]:.1%} | acc {c["accuracy_first"]:.1%} -> {c["accuracy_second"]:.1%}')
