"""Analysis of the corrected-text rerun. Written before any corrected-text prediction existed.

A copy of final_analysis.py (the locked analysis) with these changes only, all declared in reports/Corrected-text rerun plan.md:
  1. it reads the corrected sample (final-corrected) and the corrected-* prediction files, and writes corrected-results.json;
  2. questions 4 and 5 use all 10,000 resamples, as the locked plan intended (the locked script used 2,000);
  3. the rank correlations at the end are removed (the locked script's formula mishandled ties);
  4. the heading line says what this run is.
No threshold, calibration or prompt is fitted here.

Usage: python corrected_text_analysis.py    (prints the report; writes corrected-results.json)
"""
import json, math, random, re, statistics as st, collections, sys
from pathlib import Path

import os
SRC = Path(__file__).resolve().parent
T = SRC.parents[2] / "screening-check/trialpanorama/final-corrected"
HERE = Path(os.environ.get("CORRECTED_PRED_DIR", SRC))   # override only for the dry run with random numbers
SEED, DRAWS, MARGIN = 20261122, 10000, -0.05
CUT_EXCLUDE, CUT_INCLUDE = 0.019619440825558058, 0.96434342645985   # frozen from the 400-record pilot

rows = {}
for l in open(T / "sample.jsonl"):
    r = json.loads(l); rows[f'{r["review"]}|{r["pmid"]}'] = r
reviews = json.load(open(T / "reviews.json"))
fams = sorted({r["review"] for r in rows.values()})
ids_by_fam = {f: [i for i, r in rows.items() if r["review"] == f] for f in fams}
y = {i: r["label"] for i, r in rows.items()}
N = len(rows)


def valid(p):
    return isinstance(p, (int, float)) and not isinstance(p, bool) and p == p and 0 <= p <= 1


def load_predictions(path, provider=None):
    """case_id -> probability for valid answers only; plus cost and counts over all scheduled records."""
    sc, cost, n_rows, invalid = {}, 0.0, 0, 0
    if not Path(path).exists(): return None
    for l in open(path):
        p = json.loads(l)
        if provider and p.get("provider") != provider: continue
        n_rows += 1; cost += p.get("cost_usd") or 0
        pr = (p.get("probabilities") or {}).get("included") if "probabilities" in p else p.get("p")
        if p.get("status", "ok") == "ok" and valid(pr) and p["case_id"] in rows: sc[p["case_id"]] = pr
        else: invalid += 1
    return {"scores": sc, "cost": cost, "rows": n_rows, "invalid_or_missing": N - len(sc)}


def keyword_scores():
    STOP = set("a an the of and or in on to for with by from at as is are was were be been that this these those it its we our not no than which who into during after before between using used study studies".split())
    tok = lambda s: [w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP and len(w) > 1]
    docs = {i: tok(r["title"] + " " + r["abstract"]) for i, r in rows.items()}; df = collections.Counter(w for d in docs.values() for w in set(d)); sc = {}
    for i, r in rows.items():
        tf = collections.Counter(docs[i]); q = set(tok(reviews[r["review"]]["title"]))
        sc[i] = sum(math.log(1 + (N - df[w] + .5) / (df[w] + .5)) * tf[w] / (tf[w] + 1.2) for w in q if w in tf)
    return sc


SYSTEMS = [  # key, label, file for the first scheduled pass, provider filter
    ("decider", "Decider 1.3", HERE / "corrected-pass1-direct/predictions.jsonl", "pplx_decider_v13"),
    ("nimble", "Nimble 4.1", HERE / "corrected-pass1-direct/predictions.jsonl", "nimble"),
    ("gemini", "Gemini Decision 1", HERE / "corrected-pass1-or_gemini_decision_1/predictions.jsonl", None),
    ("gpt", "GPT-6 Luna (probability)", HERE / "corrected-pass1-prob/llm_openai_prob.jsonl", None),
    ("haiku", "Claude Haiku 5.5 (probability)", HERE / "corrected-pass1-prob/llm_anthropic_prob.jsonl", None),
    ("logistic", "Logistic regression (classic)", HERE / "corrected-classic-logistic.jsonl", None),
    ("xgboost", "XGBoost (classic)", HERE / "corrected-classic-xgboost.jsonl", None),
]
PASS2 = {"decider": (HERE / "corrected-pass2-direct/predictions.jsonl", "pplx_decider_v13"), "nimble": (HERE / "corrected-pass2-direct/predictions.jsonl", "nimble"),
         "gemini": (HERE / "corrected-pass2-or_gemini_decision_1/predictions.jsonl", None)}
P = {k: load_predictions(f, prov) for k, _, f, prov in SYSTEMS}
LABEL = {k: lab for k, lab, _, _ in SYSTEMS}
missing = [LABEL[k] for k in P if P[k] is None]
P = {k: v for k, v in P.items() if v is not None}


def correct(sc, i):
    """An item is correct only if a valid answer exists and falls on the right side of 0.5."""
    return i in sc and ((sc[i] >= 0.5) == bool(y[i]))


def fam_stats(sc):
    out = {}
    for f in fams:
        inc = [i for i in ids_by_fam[f] if y[i]]; exc = [i for i in ids_by_fam[f] if not y[i]]
        a1 = sum(correct(sc, i) for i in inc) / len(inc); a0 = sum(correct(sc, i) for i in exc) / len(exc)
        out[f] = ((a1 + a0) / 2, a1, a0)
    return out


def fam_auc(sc):
    v = []
    for f in fams:
        pos = [sc[i] for i in ids_by_fam[f] if y[i] and i in sc]; neg = [sc[i] for i in ids_by_fam[f] if not y[i] and i in sc]
        if pos and neg: v.append(sum((a > b) + .5 * (a == b) for a in pos for b in neg) / (len(pos) * len(neg)))
    return st.mean(v) if v else None


rng = random.Random(SEED)
DRAW = [[rng.choice(fams) for _ in fams] for _ in range(DRAWS)]          # the same resampled families for every system


def interval(per_family):
    """95% percentile interval of the equal-family mean of a per-family quantity."""
    v = sorted(st.mean(per_family[f] for f in d) for d in DRAW)
    return st.mean(per_family[f] for f in fams), v[int(.025 * DRAWS)], v[int(.975 * DRAWS) - 1]


FS = {k: fam_stats(P[k]["scores"]) for k in P}
BA = {k: {f: FS[k][f][0] for f in fams} for k in P}
res = {"sample": {"families": len(fams), "records": N, "included": sum(y.values())}, "systems_not_run": missing, "systems": {}}
out = lambda *a: print(*a)

out(f"CORRECTED-TEXT RERUN (after the fact, not confirmatory): {len(fams)} review families, {N} records ({sum(y.values())} included)")
if missing: out("NOT RUN (reported as unavailable; comparisons involving them are unassessed):", ", ".join(missing))
kw = keyword_scores()
out("\nAll systems, first scheduled pass. Missing or invalid answers count as wrong.")
out(f'{"system":<32}{"balanced acc (95% interval)":>30}{"included":>10}{"excluded":>10}{"record acc":>12}{"AUC":>7}{"Brier":>7}{"invalid":>9}')
for k in P:
    sc = P[k]["scores"]; m, lo, hi = interval(BA[k]); a1 = st.mean(FS[k][f][1] for f in fams); a0 = st.mean(FS[k][f][2] for f in fams)
    rec = sum(correct(sc, i) for i in rows) / N; auc = fam_auc(sc); brier = st.mean((sc[i] - y[i]) ** 2 for i in sc) if sc else None
    res["systems"][k] = {"label": LABEL[k], "balanced_accuracy": m, "interval": [lo, hi], "accuracy_included": a1, "accuracy_excluded": a0, "record_accuracy": rec, "auc": auc,
                         "brier_valid_only": brier, "invalid_or_missing": P[k]["invalid_or_missing"], "cost_usd_first_pass": P[k]["cost"]}
    out(f'{LABEL[k]:<32}{f"{m:.1%} ({lo:.1%} to {hi:.1%})":>30}{a1:>10.1%}{a0:>10.1%}{rec:>12.1%}{(auc or 0):>7.3f}{(brier or 0):>7.3f}{P[k]["invalid_or_missing"]:>9}')
out(f'{"Keyword overlap (floor)":<32}{"ranking only":>30}{"":>10}{"":>10}{"":>12}{fam_auc(kw):>7.3f}')
res["keyword_auc"] = fam_auc(kw)


def paired(a, b):
    d = {f: BA[a][f] - BA[b][f] for f in fams}; return interval(d)


# Question 1 (the only confirmatory test)
out("\nQUESTION 1 (confirmatory): is Decider within five percentage points of probability-output GPT?")
if "decider" in P and "gpt" in P:
    m, lo, hi = paired("decider", "gpt")
    verdict = "NON-INFERIORITY ESTABLISHED" if lo > MARGIN else ("DECIDER IS WORSE BY MORE THAN THE MARGIN" if hi < MARGIN else "INCONCLUSIVE")
    out(f"   Decider minus GPT, equal-family balanced accuracy: {m:+.1%}  (95% interval {lo:+.1%} to {hi:+.1%}); margin -5.0 points -> {verdict}")
    res["q1"] = {"difference": m, "interval": [lo, hi], "margin": MARGIN, "verdict": verdict}
else: out("   UNASSESSED: a required system did not run."); res["q1"] = {"verdict": "UNASSESSED"}

# Question 2
out("\nQUESTION 2 (secondary): does Decider cost at most one fifth as much? One production pass, all charges, divided by all scheduled records.")
if "decider" in P and "gpt" in P and P["gpt"]["cost"] > 0:
    cd, cg = P["decider"]["cost"] / N * 1000, P["gpt"]["cost"] / N * 1000
    out(f"   Decider ${cd:.4f} per 1,000 records; GPT ${cg:.4f}; ratio {cd / cg:.3f} -> {'MET' if cd / cg <= 0.2 else 'NOT MET'} (prices as published, retrieved 2026-11-16; computed from token counts)")
    res["q2"] = {"decider_per_1000": cd, "gpt_per_1000": cg, "ratio": cd / cg, "met": cd / cg <= 0.2}
else: out("   UNASSESSED"); res["q2"] = {"met": None}

# Question 3
out("\nQUESTION 3 (secondary): does Decider outperform both classic baselines?")
q3 = {}
for b in ("logistic", "xgboost"):
    if "decider" in P and b in P:
        m, lo, hi = paired("decider", b); q3[b] = {"difference": m, "interval": [lo, hi]}
        out(f"   Decider minus {LABEL[b]}: {m:+.1%}  (95% interval {lo:+.1%} to {hi:+.1%})")
res["q3"] = {**q3, "met": (len(q3) == 2 and all(v["interval"][0] > 0 for v in q3.values())) if len(q3) == 2 else None}
out("   ->", {True: "MET (both lower endpoints above zero)", False: "NOT MET", None: "UNASSESSED"}[res["q3"]["met"]])

# Question 4
out("\nQUESTION 4 (secondary, descriptive): do classifications repeat? Two valid, identical yes/no answers, over all scheduled records.")
res["q4"] = {}
for k, (f2, prov) in PASS2.items():
    second = load_predictions(f2, prov)
    if k not in P or second is None: out(f"   {LABEL.get(k, k)}: UNASSESSED"); continue
    a, b = P[k]["scores"], second["scores"]
    same = {i: int(i in a and i in b and ((a[i] >= .5) == (b[i] >= .5))) for i in rows}
    per = {f: st.mean(same[i] for i in ids_by_fam[f]) for f in fams}; v = sorted(sum(same[i] for f in d for i in ids_by_fam[f]) / sum(len(ids_by_fam[f]) for f in d) for d in DRAW)
    rate = sum(same.values()) / N; exact = sum(1 for i in rows if i in a and i in b and abs(a[i] - b[i]) <= 1e-9) / N
    res["q4"][k] = {"same_classification": rate, "interval": [v[int(.025 * DRAWS)], v[int(.975 * DRAWS) - 1]], "identical_probability": exact}
    out(f"   {LABEL[k]}: {rate:.1%} (family-cluster interval {v[int(.025 * DRAWS)]:.1%} to {v[int(.975 * DRAWS) - 1]:.1%}); identical probability on {exact:.1%}" + ("  -> meets the 98% descriptive benchmark" if k == "decider" and rate >= .98 else ("  -> below the 98% descriptive benchmark" if k == "decider" else "")))

# Question 5
out("\nQUESTION 5 (descriptive, no pass mark): the frozen Decider rule. Exclude when p <= %.6f; include when p >= %.6f; otherwise defer." % (CUT_EXCLUDE, CUT_INCLUDE))
if "decider" in P:
    sc = P["decider"]["scores"]; res["q5"] = {}
    for name, sel, want in (("automatic exclude", lambda p: p <= CUT_EXCLUDE, 0), ("automatic include", lambda p: p >= CUT_INCLUDE, 1)):
        I = [i for i in sc if sel(sc[i])]
        if not I: out(f"   {name}: no decisions (reliability undefined, coverage 0%)"); res["q5"][name] = {"decisions": 0}; continue
        ok = sum(y[i] == want for i in I); bs = []
        for d in DRAW:
            J = [i for f in d for i in ids_by_fam[f] if i in sc and sel(sc[i])]
            if J: bs.append(sum(y[i] == want for i in J) / len(J))
        bs.sort(); ci = [bs[int(.025 * len(bs))], bs[int(.975 * len(bs)) - 1]] if len(bs) > 100 else [None, None]
        res["q5"][name] = {"correct": ok, "decisions": len(I), "reliability": ok / len(I), "coverage": len(I) / N, "families": len({rows[i]["review"] for i in I}), "interval": ci}
        out(f"   {name}: {ok}/{len(I)} correct = {ok / len(I):.1%}" + (f" (family-bootstrap interval {ci[0]:.1%} to {ci[1]:.1%})" if ci[0] is not None else " (interval not estimable)") + f"; coverage {len(I) / N:.1%} of records; {len({rows[i]['review'] for i in I})} families contribute")
    out("   This describes one fixed rule on a balanced sample. It does not show what other rules could do, and it is not a deployment reliability.")

# Question 6
out("\nQUESTION 6 (exploratory, no pass mark): variation between reviews and between models.")
if "decider" in P:
    b = BA["decider"]; obs_var = st.pvariance(b.values())
    p1 = st.mean(FS["decider"][f][1] for f in fams); p0 = st.mean(FS["decider"][f][2] for f in fams)
    noise = st.mean((p1 * (1 - p1) + p0 * (1 - p0)) / (4 * (len(ids_by_fam[f]) / 2)) for f in fams)
    under = math.sqrt(max(0.0, obs_var - noise))
    out(f"   Decider, per-review balanced accuracy: lowest {min(b.values()):.0%}, highest {max(b.values()):.0%}; observed standard deviation {math.sqrt(obs_var):.1%};")
    out(f"   expected from sampling so few records per review alone: {math.sqrt(noise):.1%}; estimated underlying spread after removing that: {under:.1%}")
    res["q6"] = {"observed_sd": math.sqrt(obs_var), "sampling_noise_sd": math.sqrt(noise), "estimated_underlying_sd": under, "gaps": {}}
    for a_, b_ in (("decider", "nimble"), ("decider", "gemini"), ("nimble", "gemini")):
        if a_ in P and b_ in P:
            m, lo, hi = paired(a_, b_); res["q6"]["gaps"][f"{a_}-{b_}"] = [m, lo, hi]; out(f"   gap {LABEL[a_]} minus {LABEL[b_]}: {m:+.1%} ({lo:+.1%} to {hi:+.1%})")

# Secondary descriptive analyses
out("\nSECONDARY (descriptive, nominal intervals)")
for a_, b_ in (("nimble", "gpt"), ("gemini", "gpt"), ("decider", "haiku"), ("nimble", "haiku"), ("gpt", "haiku"), ("nimble", "logistic"), ("nimble", "xgboost"), ("gpt", "xgboost")):
    if a_ in P and b_ in P:
        m, lo, hi = paired(a_, b_); res.setdefault("secondary_differences", {})[f"{a_}-{b_}"] = [m, lo, hi]; out(f"   {LABEL[a_]} minus {LABEL[b_]}: {m:+.1%} ({lo:+.1%} to {hi:+.1%})")
out("   Confidence: accuracy among the quarter of valid answers the system is most sure about, and the quarter it is least sure about")
res["confidence"] = {}
for k in P:
    sc = P[k]["scores"]; o = sorted(sc, key=lambda i: -abs(sc[i] - .5)); n = len(o) // 4
    if n:
        top = sum(correct(sc, i) for i in o[:n]) / n; low = sum(correct(sc, i) for i in o[-n:]) / n; res["confidence"][k] = [top, low]; out(f"      {LABEL[k]:<32} most sure {top:.1%}   least sure {low:.1%}")
dm = [k for k in ("decider", "nimble", "gemini") if k in P]
if len(dm) == 3:
    common = [i for i in rows if all(i in P[k]["scores"] for k in dm)]; votes = {i: sum(P[k]["scores"][i] >= .5 for k in dm) for i in common}
    un = [i for i in common if votes[i] in (0, 3)]; rest = [i for i in common if votes[i] not in (0, 3)]
    a_un = sum((votes[i] == 3) == bool(y[i]) for i in un) / len(un) if un else None; a_rest = sum((votes[i] >= 2) == bool(y[i]) for i in rest) / len(rest) if rest else None
    res["disagreement"] = {"unanimous_share": len(un) / len(common), "accuracy_unanimous": a_un, "accuracy_split_majority": a_rest}
    out(f"   Disagreement: the three decision models agree on {len(un) / len(common):.1%} of records and are right on {a_un:.1%} of those; where they split, the majority is right on {(a_rest or 0):.1%}")
json.dump(res, open(HERE / "corrected-results.json", "w"), indent=1)
