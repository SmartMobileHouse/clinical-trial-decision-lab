"""Post-hoc sensitivity checks for the locked final run (written 2026-11-25, AFTER results were seen; exploratory, not part of the locked analysis).

Responds to the independent review of the results:
  1. trial linkage: registration numbers found in abstracts connect some sample families and some training rows to the sample
  2. questions 4 and 5 used 2,000 bootstrap draws instead of the planned 10,000
  3. rank correlations ignored ties
Nothing here replaces final_analysis.py or final-results.json. Run with .venv-classic/bin/python. Writes final-sensitivity.json / .txt.
"""
import json, re, random, collections, statistics as st, sys, os
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))
import classic_final as cf

T = SRC.parents[2] / "screening-check/trialpanorama"
SEED, DRAWS, MARGIN = 20261122, 10000, -0.05
CUT_EXCLUDE, CUT_INCLUDE = 0.019619440825558058, 0.96434342645985
lines = []
def out(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); lines.append(s)

TRIAL = re.compile(r"\b(NCT\s?\d{8}|ISRCTN\s?\d{8}|ACTRN\s?\d{14}|ChiCTR[-A-Z0-9]{6,}|DRKS\s?\d{8}|UMIN\s?\d{9}|NTR\s?\d{3,5}|PACTR\s?\d{15}|"
                   r"CTRI/\d{4}/\d{2,3}/\d{6}|IRCT\d{6,}N\d+|KCT\s?\d{7}|TCTR\s?\d{11}|RBR-[0-9a-z]{6}|JPRN-[A-Za-z0-9]+|\d{4}-\d{6}-\d{2})\b", re.I)
def trial_ids(r):
    return {re.sub(r"\s+", "", m).upper() for m in TRIAL.findall(r["title"] + " " + r["abstract"])}

rows = {}
for l in open(T / "final/sample.jsonl"):
    r = json.loads(l); rows[f'{r["review"]}|{r["pmid"]}'] = r
reviews = json.load(open(T / "final/reviews.json"))
fams = sorted({r["review"] for r in rows.values()})
ids_by_fam = {f: [i for i, r in rows.items() if r["review"] == f] for f in fams}
y = {i: r["label"] for i, r in rows.items()}; N = len(rows)
tid = {i: trial_ids(r) for i, r in rows.items()}
sample_ids = set().union(*tid.values())

# ---- 1a. clusters of families joined by a shared trial number ----
par = {}
def find(x):
    while par.setdefault(x, x) != x: par[x] = par[par[x]]; x = par[x]
    return x
for i, r in rows.items():
    for t in tid[i]: par[find("T:" + t)] = find("F:" + r["review"])
clus = collections.defaultdict(list)
for f in fams: clus[find("F:" + f)].append(f)
clusters = sorted(clus.values())
by_trial = collections.defaultdict(set)
for i in rows:
    for t in tid[i]: by_trial[t].add(rows[i]["review"])
cross = {t: sorted(v) for t, v in by_trial.items() if len(v) > 1}
out("POST-HOC SENSITIVITY CHECKS (exploratory; written after the locked results were seen)")
out(f"\n1. TRIAL LINKAGE by registration numbers found in titles and abstracts (partial: papers that do not print their number stay unlinked)")
out(f"   sample records carrying a registration number: {sum(1 for i in rows if tid[i])} of {N}; distinct numbers {len(sample_ids)}")
out(f"   numbers shared by more than one sample family: {len(cross)}; families involved: {len(set().union(*cross.values())) if cross else 0}; records involved: {sum(1 for i in rows if tid[i] & set(cross))}")
out(f"   review families {len(fams)} -> clusters after joining linked families {len(clusters)}")

train = [json.loads(l) for l in open(T / "classic-final/train.jsonl")]
lab = collections.defaultdict(set)
for r in train: lab[(r["review"], r["pmid"])].add(r["label"])
train = [r for r in train if len(lab[(r["review"], r["pmid"])]) == 1]
ttid = [trial_ids(r) for r in train]
leak_rows = [k for k, t in enumerate(ttid) if t & sample_ids]
leak_ids = set().union(*(ttid[k] & sample_ids for k in leak_rows)) if leak_rows else set()
out(f"   training rows sharing a registration number with the sample: {len(leak_rows)} of {len(train)} (numbers: {len(leak_ids)}; sample records affected: {sum(1 for i in rows if tid[i] & leak_ids)})")
pilot_ids = set()
for d in ("pilot", "info-test"):
    for l in open(T / d / "sample.jsonl"): pilot_ids |= trial_ids(json.loads(l))
pilot_shared = sample_ids & pilot_ids
pilot_recs = {i for i in rows if tid[i] & pilot_shared}
out(f"   registration numbers shared between the pilots and the sample: {len(pilot_shared)} (sample records affected: {len(pilot_recs)})")

# ---- predictions ----
def load(path, provider=None):
    sc = {}
    for l in open(SRC / path):
        p = json.loads(l)
        if provider and p.get("provider") != provider: continue
        pr = (p.get("probabilities") or {}).get("included") if "probabilities" in p else p.get("p")
        if p.get("status", "ok") == "ok" and isinstance(pr, (int, float)) and 0 <= pr <= 1 and p["case_id"] in rows: sc[p["case_id"]] = pr
    return sc
P = {"decider": load("final-pass1-direct/predictions.jsonl", "pplx_decider_v13"), "nimble": load("final-pass1-direct/predictions.jsonl", "nimble"),
     "gemini": load("final-pass1-or_gemini_decision_1/predictions.jsonl"), "gpt": load("final-pass1-prob/llm_openai_prob.jsonl"),
     "haiku": load("final-pass1-prob/llm_anthropic_prob.jsonl"), "logistic": load("final-classic-logistic.jsonl"), "xgboost": load("final-classic-xgboost.jsonl")}
P2 = {"decider": load("final-pass2-direct/predictions.jsonl", "pplx_decider_v13"), "nimble": load("final-pass2-direct/predictions.jsonl", "nimble"),
      "gemini": load("final-pass2-or_gemini_decision_1/predictions.jsonl")}

# ---- 1b. refit the classic baselines without the linked training rows (same frozen settings; no new model selection) ----
chosen = json.load(open(T / "classic-final/selection.json"))["chosen"]
srows = [{**r, "review_title": reviews[r["review"]]["title"]} for r in rows.values()]; skeys = list(rows)
def refit(tr):
    yy = np.array([r["label"] for r in tr]); F = cf.Features(tr); b = F.blocks(tr); F.fit_scaler(b[2]); sb = F.blocks(srows); res = {}
    for name in ("logistic", "xgboost"):
        kind, par_ = chosen[name]["features"], chosen[name]["params"]
        m = cf.make_lr(*par_) if name == "logistic" else cf.make_xgb(int(par_[0]), int(par_[1]), int(par_[2]))
        m.fit(F.assemble(b, kind), yy); res[name] = dict(zip(skeys, map(float, m.predict_proba(F.assemble(sb, kind))[:, 1])))
    return res
same = refit(train)
for name in ("logistic", "xgboost"):
    out(f"   check: refitting {name} on the unchanged training set reproduces the frozen predictions to within {max(abs(same[name][i] - P[name][i]) for i in rows):.2e}")
drop = set(leak_rows)
clean = refit([r for k, r in enumerate(train) if k not in drop])
P["logistic_clean"], P["xgboost_clean"] = clean["logistic"], clean["xgboost"]
for name in ("logistic", "xgboost"):
    with open(SRC / f"final-sensitivity-classic-{name}.jsonl", "w") as f:
        for i in rows: f.write(json.dumps({"case_id": i, "p": clean[name][i]}) + "\n")

# ---- scoring ----
correct = lambda sc, i: i in sc and ((sc[i] >= .5) == bool(y[i]))
def ba(sc, keep=None):
    o = {}
    for f in fams:
        inc = [i for i in ids_by_fam[f] if y[i] and (keep is None or i in keep)]; exc = [i for i in ids_by_fam[f] if not y[i] and (keep is None or i in keep)]
        if inc and exc: o[f] = (sum(correct(sc, i) for i in inc) / len(inc) + sum(correct(sc, i) for i in exc) / len(exc)) / 2
    return o
rng = random.Random(SEED); DRAW_F = [[rng.choice(fams) for _ in fams] for _ in range(DRAWS)]          # identical to the locked analysis
rng = random.Random(SEED); DRAW_C = [[f for _ in clusters for f in rng.choice(clusters)] for _ in range(DRAWS)]
def interval(per, draws):
    v = sorted(st.mean(per[f] for f in d if f in per) for d in draws)
    return st.mean(per.values()), v[int(.025 * DRAWS)], v[int(.975 * DRAWS) - 1]
BA = {k: ba(P[k]) for k in P}
diff = lambda a, b, B=None: {f: (B or BA)[a][f] - (B or BA)[b][f] for f in (B or BA)[a]}
fmt = lambda t: f"{t[0]:+.2%} ({t[1]:+.2%} to {t[2]:+.2%})"
res = {"linkage": {"clusters": len(clusters), "cross_family_trial_numbers": cross, "training_rows_removed": len(leak_rows), "trial_numbers_shared_with_training": sorted(leak_ids),
                   "trial_numbers_shared_with_pilots": sorted(pilot_shared)}}

out("\n   Classic baselines, balanced accuracy on the locked sample")
for k, lab_ in (("logistic", "Logistic regression, as locked"), ("logistic_clean", "Logistic regression, linked rows removed"), ("xgboost", "XGBoost, as locked"), ("xgboost_clean", "XGBoost, linked rows removed")):
    t = interval(BA[k], DRAW_C); res.setdefault("classic", {})[k] = t; out(f"      {lab_:<42}{t[0]:.2%} ({t[1]:.2%} to {t[2]:.2%})   [linked families resampled together]")
out("\n   Paired differences, three ways")
out(f'      {"comparison":<34}{"as locked (79 families)":>30}{"linked families together (" + str(len(clusters)) + ")":>36}')
res["differences"] = {}
for a, b in (("decider", "gpt"), ("decider", "logistic"), ("decider", "xgboost"), ("decider", "logistic_clean"), ("decider", "xgboost_clean"), ("nimble", "xgboost_clean"), ("gpt", "xgboost_clean")):
    d = diff(a, b); t1, t2 = interval(d, DRAW_F), interval(d, DRAW_C); res["differences"][f"{a}-{b}"] = {"family": t1, "cluster": t2}
    out(f"      {a + ' minus ' + b:<34}{fmt(t1):>30}{fmt(t2):>36}")
t = res["differences"]["decider-gpt"]["cluster"]
out(f"   Question 1 with linked families together: lower end {t[1]:+.3%} against the margin -5.0 -> {'still passes' if t[1] > MARGIN else 'DOES NOT PASS'}")
keep = set(rows) - pilot_recs; Bk = {k: ba(P[k], keep) for k in ("decider", "gpt")}; t = interval(diff("decider", "gpt", Bk), DRAW_C)
res["q1_without_pilot_linked_records"] = t
out(f"   Question 1 also dropping the {len(pilot_recs)} sample records that share a trial number with the pilots: {fmt(t)} -> {'still passes' if t[1] > MARGIN else 'DOES NOT PASS'}")
m3 = all(res["differences"][f"decider-{b}"]["cluster"][1] > 0 for b in ("logistic_clean", "xgboost_clean"))
out(f"   Question 3 with the cleaned baselines: {'MET' if m3 else 'still NOT MET'}")

# ---- 2. questions 4 and 5 with the planned 10,000 draws ----
out("\n2. QUESTIONS 4 AND 5 with the planned 10,000 draws (locked output used 2,000)")
res["q4"], res["q5"] = {}, {}
for k in P2:
    a, b = P[k], P2[k]; s = {i: int(i in a and i in b and ((a[i] >= .5) == (b[i] >= .5))) for i in rows}; r_ = {}
    for nm, D in (("family", DRAW_F), ("cluster", DRAW_C)):
        v = sorted(sum(s[i] for f in d for i in ids_by_fam[f]) / sum(len(ids_by_fam[f]) for f in d) for d in D); r_[nm] = [v[int(.025 * DRAWS)], v[int(.975 * DRAWS) - 1]]
    res["q4"][k] = {"same": sum(s.values()), "of": N, **r_}
    out(f"   Q4 {k}: {sum(s.values())}/{N} = {sum(s.values()) / N:.2%}; interval {r_['family'][0]:.2%} to {r_['family'][1]:.2%} (linked families together: {r_['cluster'][0]:.2%} to {r_['cluster'][1]:.2%})")
sc = P["decider"]
for name, sel, want in (("automatic exclude", lambda p: p <= CUT_EXCLUDE, 0), ("automatic include", lambda p: p >= CUT_INCLUDE, 1)):
    I = [i for i in sc if sel(sc[i])]; ok = sum(y[i] == want for i in I); r_ = {}
    for nm, D in (("family", DRAW_F), ("cluster", DRAW_C)):
        bs = sorted(sum(y[i] == want for i in J) / len(J) for J in ([i for f in d for i in ids_by_fam[f] if sel(sc[i])] for d in D) if J)
        r_[nm] = [bs[int(.025 * len(bs))], bs[int(.975 * len(bs)) - 1]]
    res["q5"][name] = {"correct": ok, "decisions": len(I), **r_}
    out(f"   Q5 {name}: {ok}/{len(I)} = {ok / len(I):.1%}; interval {r_['family'][0]:.1%} to {r_['family'][1]:.1%} (linked families together: {r_['cluster'][0]:.1%} to {r_['cluster'][1]:.1%})")

# ---- 3. rank correlations with ties handled ----
out("\n3. REVIEW DIFFICULTY, rank correlations with ties handled correctly (Decider, exploratory)")
b = [BA["decider"][f] for f in fams]; res["difficulty"] = {}
for name, v in (("records sampled per review", [len(ids_by_fam[f]) for f in fams]), ("review year", [int(reviews[f].get("year") or 0) for f in fams]), ("length of review title", [len(reviews[f]["title"]) for f in fams])):
    rho = float(spearmanr(v, b).statistic); res["difficulty"][name] = rho; out(f"   {name}: {rho:+.3f}")

# ---- 4. probability quality (reported in the locked output as Brier only) ----
out("\n4. PROBABILITY QUALITY: Brier score (lower is better; always answering 0.5 scores 0.250)")
res["brier"] = {}
for k in ("decider", "nimble", "gemini", "gpt", "haiku", "logistic", "xgboost", "xgboost_clean"):
    br = st.mean((P[k][i] - y[i]) ** 2 for i in P[k]); res["brier"][k] = br; out(f"   {k:<16}{br:.3f}  {'worse than 0.5 everywhere' if br > .25 else 'better than 0.5 everywhere'}")
json.dump(res, open(SRC / "final-sensitivity.json", "w"), indent=1, default=list)
open(SRC / "final-sensitivity.txt", "w").write("\n".join(lines) + "\n")
