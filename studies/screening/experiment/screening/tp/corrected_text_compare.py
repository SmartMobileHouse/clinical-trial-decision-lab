"""Corrected-text rerun: compare each system's answers on the corrected text with its answers in the locked run.

Written before any corrected-text result was looked at. Descriptive only. See reports/Corrected-text rerun plan.md.
Writes corrected-compare.json. Usage: python corrected_text_compare.py
"""
import json, random, statistics as st
from pathlib import Path

SRC = Path(__file__).resolve().parent
T = SRC.parents[2] / "screening-check/trialpanorama"
SEED, DRAWS = 20261122, 10000
rows = {}
for l in open(T / "final-corrected/sample.jsonl"):
    r = json.loads(l); rows[f'{r["review"]}|{r["pmid"]}'] = r
changed = {f'{c["review"]}|{c["pmid"]}' for c in json.load(open(T / "final-corrected/changed.json"))}
fams = sorted({r["review"] for r in rows.values()}); ids_by_fam = {f: [i for i, r in rows.items() if r["review"] == f] for f in fams}
y = {i: int(r["label"]) for i, r in rows.items()}

def load(path, provider=None):
    sc = {}
    for l in open(SRC / path):
        p = json.loads(l)
        if provider and p.get("provider") != provider: continue
        pr = (p.get("probabilities") or {}).get("included") if "probabilities" in p else p.get("p")
        if p.get("status", "ok") == "ok" and isinstance(pr, (int, float)) and 0 <= pr <= 1: sc[p["case_id"]] = pr
    return sc

FILES = {"decider": ("pass1-direct/predictions.jsonl", "pplx_decider_v13"), "nimble": ("pass1-direct/predictions.jsonl", "nimble"), "gemini": ("pass1-or_gemini_decision_1/predictions.jsonl", None),
         "gpt": ("pass1-prob/llm_openai_prob.jsonl", None), "haiku": ("pass1-prob/llm_anthropic_prob.jsonl", None), "logistic": ("classic-logistic.jsonl", None), "xgboost": ("classic-xgboost.jsonl", None)}
L = {k: load("final-" + f, p) for k, (f, p) in FILES.items()}; C = {k: load("corrected-" + f, p) for k, (f, p) in FILES.items()}
rng = random.Random(SEED); DRAW = [[rng.choice(fams) for _ in fams] for _ in range(DRAWS)]
ok = lambda sc, i: i in sc and ((sc[i] >= .5) == bool(y[i]))

def pooled_ba(sc, ids):
    inc = [i for i in ids if y[i]]; exc = [i for i in ids if not y[i]]
    return (sum(ok(sc, i) for i in inc) / len(inc) + sum(ok(sc, i) for i in exc) / len(exc)) / 2

res = {"records": len(rows), "corrected_abstracts": len(changed), "unchanged_abstracts": len(rows) - len(changed), "systems": {}}
for k in FILES:
    a, b = L[k], C[k]; out = {}
    for name, ids in (("corrected", [i for i in rows if i in changed]), ("unchanged", [i for i in rows if i not in changed])):
        flips = [i for i in ids if (a[i] >= .5) != (b[i] >= .5)]
        out[name] = {"records": len(ids), "answers_changed": len(flips), "share_changed": len(flips) / len(ids),
                     "changed_to_include": sum(b[i] >= .5 for i in flips), "changed_wrong_to_right": sum(ok(b, i) for i in flips), "changed_right_to_wrong": sum(ok(a, i) for i in flips),
                     "identical_probability": sum(abs(a[i] - b[i]) <= 1e-9 for i in ids) / len(ids), "mean_absolute_probability_change": st.mean(abs(a[i] - b[i]) for i in ids),
                     "balanced_accuracy_pooled_locked_text": pooled_ba(a, ids), "balanced_accuracy_pooled_corrected_text": pooled_ba(b, ids)}
    res["systems"][k] = out
# Decider minus GPT on each subset, pooled over papers, review-family bootstrap, for both texts
def diff_ci(A, B, keep):
    def d(fl):
        ids = [i for f in fl for i in ids_by_fam[f] if i in keep]
        inc = [i for i in ids if y[i]]; exc = [i for i in ids if not y[i]]
        if not inc or not exc: return None
        g = lambda sc: (sum(ok(sc, i) for i in inc) / len(inc) + sum(ok(sc, i) for i in exc) / len(exc)) / 2
        return g(A) - g(B)
    v = sorted(x for x in (d(dr) for dr in DRAW) if x is not None)
    return [d(fams), v[int(.025 * len(v))], v[int(.975 * len(v)) - 1]]
res["decider_minus_gpt_pooled"] = {}
for name, keep in (("all", set(rows)), ("corrected", changed), ("unchanged", set(rows) - changed)):
    res["decider_minus_gpt_pooled"][name] = {"locked_text": diff_ci(L["decider"], L["gpt"], keep), "corrected_text": diff_ci(C["decider"], C["gpt"], keep)}
json.dump(res, open(SRC / "corrected-compare.json", "w"), indent=1)
for k, v in res["systems"].items():
    print(f'{k:9s} corrected abstracts: {v["corrected"]["answers_changed"]:3d} of {v["corrected"]["records"]} answers changed ({v["corrected"]["share_changed"]:.1%}); unchanged abstracts: {v["unchanged"]["answers_changed"]:3d} of {v["unchanged"]["records"]} ({v["unchanged"]["share_changed"]:.1%})')
print(json.dumps(res["decider_minus_gpt_pooled"], indent=1))
