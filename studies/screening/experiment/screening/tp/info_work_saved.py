"""Exploratory, after the fact: in the small title-versus-rules test (392 papers, 11 reviews), how much of the rejected
pile could each decision model remove while missing at most 5% (or 10%) of the included papers?
The cut-off is chosen on the same data it is scored on, so these figures are optimistic. Writes info-work-saved.json."""
import collections, glob, json, statistics as st
T = "../../../screening-check/trialpanorama/"
R = {f'{r["review"]}|{r["pmid"]}': r for r in map(json.loads, open(T + "info-test/sample.jsonl"))}
y = {i: int(r["label"]) for i, r in R.items()}
def load(pat):
    A = collections.defaultdict(dict)
    for f in glob.glob(pat):
        for l in open(f):
            p = json.loads(l)
            if p.get("status", "ok") != "ok": continue
            pr = (p.get("probabilities") or {}).get("included")
            if isinstance(pr, (int, float)) and p["case_id"] in R: A[p["provider"]][p["case_id"]] = pr
    return A
def removed(sc, miss):
    pos = sorted(sc[i] for i in sc if y[i]); neg = [sc[i] for i in sc if not y[i]]
    t = pos[int(miss * len(pos) + 1e-9)]
    return sum(v < t for v in neg) / len(neg)
acc = lambda S: sum((S[i] >= .5) == bool(y[i]) for i in S) / len(S)
A, B = load("info-title-*/predictions.jsonl"), load("info-criteria-*/predictions.jsonl")
out = {m: {"accuracy_title": acc(A[m]), "accuracy_rules": acc(B[m]), "removed_5_title": removed(A[m], .05), "removed_5_rules": removed(B[m], .05),
           "removed_10_title": removed(A[m], .10), "removed_10_rules": removed(B[m], .10)} for m in sorted(A) if m in B and len(A[m]) >= 380 and len(B[m]) >= 380}
med = {k: st.median(v[k] for v in out.values()) for k in next(iter(out.values()))}
res = {"papers": len(R), "included": sum(y.values()), "reviews": len({r["review"] for r in R.values()}), "decision_models": len(out), "median": med,
       "improved_at_5": sum(v["removed_5_rules"] > v["removed_5_title"] for v in out.values()), "models": out}
json.dump(res, open("info-work-saved.json", "w"), indent=1); print(json.dumps({k: res[k] for k in res if k != "models"}, indent=1)); print(json.dumps(out["pplx_decider_v13"]))
