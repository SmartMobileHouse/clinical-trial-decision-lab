"""Addendum to info_work_saved.py, written after an independent review (28 November 2026). Exploratory.
The pooled 5% loss limit hides what happens inside single reviews. For each model and condition this reports, at the
pooled cut-off that loses at most 5% of included papers overall: the worst loss inside any one review, how many reviews
lose more than 5%, and how much can be removed with no included paper lost at all. Writes info-work-saved-addendum.json."""
import collections, glob, json, statistics as st
T = "../../../screening-check/trialpanorama/"
R = {f'{r["review"]}|{r["pmid"]}': r for r in map(json.loads, open(T + "info-test/sample.jsonl"))}
y = {i: int(r["label"]) for i, r in R.items()}; revs = sorted({r["review"] for r in R.values()})
def load(pat):
    A = collections.defaultdict(dict)
    for f in glob.glob(pat):
        for l in open(f):
            p = json.loads(l)
            if p.get("status", "ok") != "ok": continue
            pr = (p.get("probabilities") or {}).get("included")
            if isinstance(pr, (int, float)) and 0 <= pr <= 1 and p["case_id"] in R: A[p["provider"]][p["case_id"]] = pr
    return A
def detail(sc):
    pos = sorted(sc[i] for i in sc if y[i]); neg = [sc[i] for i in sc if not y[i]]
    t = pos[int(.05 * len(pos) + 1e-9)]
    per = {}
    for rv in revs:
        inc = [i for i in sc if R[i]["review"] == rv and y[i]]
        if inc: per[rv] = sum(sc[i] < t for i in inc) / len(inc)
    return {"removed": sum(v < t for v in neg) / len(neg), "removed_count": sum(v < t for v in neg), "excluded": len(neg), "included_lost": sum(v < t for v in pos), "included": len(pos),
            "worst_review_loss": max(per.values()), "reviews_losing_more_than_5pct": sum(v > .05 for v in per.values()), "reviews": len(per),
            "removed_at_zero_loss": sum(v < pos[0] for v in neg) / len(neg), "removed_at_zero_loss_count": sum(v < pos[0] for v in neg)}
A, B = load("info-title-*/predictions.jsonl"), load("info-criteria-*/predictions.jsonl")
out = {m: {"title": detail(A[m]), "rules": detail(B[m])} for m in sorted(A) if m in B and len(A[m]) >= 380 and len(B[m]) >= 380}
res = {"decision_models": len(out), "median_worst_review_loss_rules": st.median(v["rules"]["worst_review_loss"] for v in out.values()),
       "models_removing_something_at_zero_loss_rules": sum(v["rules"]["removed_at_zero_loss_count"] > 0 for v in out.values()), "models": out}
json.dump(res, open("info-work-saved-addendum.json", "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "models"})); print(json.dumps(out["pplx_decider_v13"], indent=1))
