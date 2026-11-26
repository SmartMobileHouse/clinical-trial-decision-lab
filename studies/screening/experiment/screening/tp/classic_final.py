"""Leak-free classic baselines (logistic regression, XGBoost) for the locked final run.

Modes (run from the project root or anywhere; paths are absolute-relative to this file):
  build                                  fetch/assemble screening-check/trialpanorama/classic-final/train.jsonl  (network: Europe PMC only)
  fit                                    5-fold family-grouped CV over the declared search space of classic.py, freeze settings, fit on the
                                         whole training set, write models.pkl and selection.json (incl. leakage checks)
  score <sample.jsonl> <reviews.json> <out_prefix>
                                         load models.pkl, write <out_prefix>-logistic.jsonl and <out_prefix>-xgboost.jsonl
Interpreter: .venv-classic/bin/python.  The pickle references functions in this file (`__main__`), so always run it as a script.

Training exclusions: reviews of any candidate family (normalised title match, every edition), pilot / info-test reviews and their title
matches; papers that appear in any candidate-family review, any pilot / info-test sample, or final/records.jsonl (pmid field only).
Features, search space and models are the same as experiment/screening/tp/classic.py (copied here because that file runs on import).
"""
import json, re, sys, os, math, time, csv, random, pickle, collections, urllib.parse, urllib.request
import numpy as np, scipy.sparse as sp
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))
T = ROOT + "/screening-check/trialpanorama/"
OUT = T + "classic-final/"
SEED = 0
MINL = int(os.environ.get("MINL", "2"))   # minimum usable included and excluded papers per added review (2 by default; see selection notes)
OK = {"cc by", "cc0", "cc by-sa", "cc by-nd"}
PLAN = re.compile(r"protocol|study design|design of|rationale|trial design", re.I)
norm = lambda s: re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()
clean = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()

# ---------------- text processing and features (identical to classic.py) ----------------
def stem(w):
    for suf in ("ations", "ation", "ings", "ing", "ies", "es", "ed", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 4: return w[: -len(suf)]
    return w
def toks(s): return [stem(w) for w in re.findall(r"[a-z0-9]{3,}", (s or "").lower()) if w not in ENGLISH_STOP_WORDS]
def bigr(t): return set(zip(t, t[1:]))
txt = lambda r: r["title"] + ". " + r["abstract"]

class Features:
    """Fitted on training rows only."""
    def __init__(self, rows, max_features=20000):
        self.vec = TfidfVectorizer(tokenizer=toks, token_pattern=None, lowercase=False, ngram_range=(1, 2), min_df=3,
                                   max_features=max_features, sublinear_tf=True)
        self.vec.fit([txt(r) for r in rows])
        df = collections.Counter(); self.N = len(rows); L = 0
        for r in rows:
            t = set(toks(txt(r))); df.update(t); L += len(toks(txt(r)))
        self.df = dict(df); self.avgdl = L / self.N
        self.scaler = None; self.fit_rows = len(rows)
    def idf(self, w):
        d = self.df.get(w, 0); return math.log(1 + (self.N - d + 0.5) / (d + 0.5))
    def bm25(self, q, t, k1=1.2, b=0.75):
        tf = collections.Counter(t); dl = max(1, len(t)); s = 0.0
        for w in q:
            if w in tf: s += self.idf(w) * tf[w] * (k1 + 1) / (tf[w] + k1 * (1 - b + b * dl / self.avgdl))
        return s
    def blocks(self, rows):
        Xs = self.vec.transform([txt(r) for r in rows])
        Xt = self.vec.transform([r["title"] for r in rows]); Q = self.vec.transform([r["review_title"] for r in rows])
        cos_abs = np.asarray(Xs.multiply(Q).sum(axis=1)).ravel()
        cos_tit = np.asarray(Xt.multiply(Q).sum(axis=1)).ravel()
        Qb = (Q > 0).astype(np.float64)
        Xint = Xs.multiply(Qb).tocsr()
        D = []
        for r in rows:
            q = set(toks(r["review_title"])); tt, ta = toks(r["title"]), toks(r["abstract"]); td = tt + ta; sd = set(td)
            iq = sum(self.idf(w) for w in q) or 1.0
            mt, md = q & set(tt), q & sd
            bq, bd = bigr(toks(r["review_title"])), bigr(td)
            mb = bq & bd
            D.append([self.bm25(q, tt), self.bm25(q, td), len(mt) / max(1, len(q)), len(md) / max(1, len(q)),
                      sum(self.idf(w) for w in mt) / iq, sum(self.idf(w) for w in md) / iq,
                      len(mb), len(mb) / max(1, len(bq)), max([self.idf(w) for w in md], default=0.0),
                      math.log(1 + len(q)), math.log(1 + len(td)), math.log(1 + len(tt))])
        D = np.c_[cos_tit, cos_abs, np.array(D)]
        return Xs, Xint, D
    def fit_scaler(self, D): self.scaler = StandardScaler().fit(D)
    def assemble(self, blk, kind):
        Xs, Xint, D = blk; Ds = sp.csr_matrix(self.scaler.transform(D))
        if kind == "study_only": return Xs
        if kind == "interaction_only": return sp.hstack([Ds, Xint]).tocsr()
        return sp.hstack([Xs, Ds, Xint]).tocsr()

def make_lr(C): return LogisticRegression(C=C, max_iter=3000)
def make_xgb(depth, n, mcw): return XGBClassifier(n_estimators=n, max_depth=depth, learning_rate=0.05, subsample=0.8, colsample_bytree=0.3,
                                                  min_child_weight=mcw, random_state=SEED, n_jobs=4, tree_method="hist")
def auc(s, y):
    pos, neg = s[y == 1], s[y == 0]
    return float(np.mean([(a > neg).mean() + 0.5 * (a == neg).mean() for a in pos])) if len(pos) and len(neg) else None
LR_GRID = {"C": [0.03, 0.1, 0.3, 1, 3, 10]}
XGB_GRID = [(d, n, m) for d in (2, 4) for n in (200, 400) for m in (1, 5)]
KINDS = ("study_only", "interaction_only", "all")

def family_metrics(p, y, fam):
    """equal-family balanced accuracy and mean within-family AUC; families lacking a label are skipped."""
    bal, aus = [], []
    for k in sorted(set(fam)):
        m = fam == k; yy, pp = y[m], p[m]
        if (yy == 1).sum() == 0 or (yy == 0).sum() == 0: continue
        bal.append(0.5 * (((pp >= .5)[yy == 1]).mean() + ((pp < .5)[yy == 0]).mean())); aus.append(auc(pp, yy))
    return (float(np.mean(bal)) if bal else None, float(np.mean(aus)) if aus else None, len(bal))

# ---------------- reservations ----------------
def read_records_pmids():
    f = T + "final/records.jsonl"; out = set()
    if os.path.exists(f):
        for l in open(f):
            try: out.add(str(json.loads(l)["pmid"]))
            except Exception: pass          # partial last line while the file is being written
    return out

def reservations(titles):
    """titles: review pmid -> title. Returns dict of reserved sets."""
    cand = json.load(open(T + "final-run-candidates.json"))
    cand_norm = {norm(c["family"]) for c in cand} | {norm(c["title"]) for c in cand}
    cand_revs = {c["review"] for c in cand}
    dev_revs, dev_pm, dev_titles = set(), set(), set()
    for d in ("pilot", "info-test"):
        for l in open(T + d + "/sample.jsonl"):
            r = json.loads(l); dev_revs.add(r["review"]); dev_pm.add(str(r["pmid"]))
        for k, v in json.load(open(T + d + "/reviews.json")).items(): dev_revs.add(k); dev_titles.add(norm(v["title"]))
    cand_all = cand_revs | {k for k, t in titles.items() if norm(t) in cand_norm}
    dev_all = dev_revs | {k for k, t in titles.items() if norm(t) in dev_titles}
    ids = collections.defaultdict(set)
    for r in csv.DictReader(open(T + "tp_ids.csv")): ids[r["review"]].add(r["pmid"])
    cand_pm = set().union(*(ids[k] for k in cand_all if k in ids)) if cand_all else set()
    return {"cand_norm": cand_norm, "cand_revs": cand_all, "dev_revs": dev_all, "dev_titles": dev_titles, "dev_pm": dev_pm,
            "cand_pm": cand_pm, "final_pm": read_records_pmids(), "ids": ids}

# ---------------- Europe PMC ----------------
def epmc(ids, cache, name):
    ids = [i for i in ids if i not in cache]
    for i in range(0, len(ids), 50):
        b = ids[i:i + 50]
        q = "(" + " OR ".join("EXT_ID:" + x for x in b) + ") AND SRC:MED"
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
            {"query": q, "format": "json", "resultType": "core", "pageSize": "50"})
        ok = False
        for a in range(5):
            try:
                res = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-client"}), timeout=90))["resultList"]["result"]
                got = {x.get("pmid"): x for x in res}
                for x in b: cache[x] = ({"title": clean(got[x].get("title")), "abstract": clean(got[x].get("abstractText")),
                                         "license": (got[x].get("license") or "").lower()} if x in got else None)
                ok = True; break
            except Exception as e: time.sleep(4 * (a + 1))
        open(OUT + "progress.txt", "w").write(f"{name}: fetched {min(i + 50, len(ids))} of {len(ids)} {time.strftime('%H:%M:%S')}\n")
        if (i // 50) % 10 == 0: json.dump(cache, open(OUT + f"cache-{name}.json", "w"))
    json.dump(cache, open(OUT + f"cache-{name}.json", "w"))
    return cache

def loadc(name):
    f = OUT + f"cache-{name}.json"; return json.load(open(f)) if os.path.exists(f) else {}

# ---------------- build ----------------
def build():
    os.makedirs(OUT, exist_ok=True)
    allrev = sorted({r["review"] for r in csv.DictReader(open(T + "tp_ids.csv"))})
    rc = epmc(allrev, loadc("reviews"), "reviews")
    titles = {k: v["title"] for k, v in rc.items() if v}
    old = [json.loads(l) for f in ("classic/train-with-leak.jsonl", "classic/train.jsonl") for l in open(T + f)]
    for r in old: titles.setdefault(r["review"], r["review_title"])
    json.dump(titles, open(OUT + "review_titles.json", "w"))
    R = reservations(titles)
    reserved_pm = R["cand_pm"] | R["dev_pm"] | R["final_pm"]
    bad_rev = R["cand_revs"] | R["dev_revs"]
    print("reserved reviews", len(bad_rev), "reserved pmids", len(reserved_pm), "final records pmids", len(R["final_pm"]))
    # surviving old rows
    seen, rows = set(), []
    for r in old:
        key = (r["review"], r["pmid"])
        if key in seen: continue
        seen.add(key)
        if r["review"] in bad_rev or norm(r["review_title"]) in R["cand_norm"] | R["dev_titles"] or r["pmid"] in reserved_pm or PLAN.search(r["title"]): continue
        rows.append(r)
    old_revs = {r["review"] for r in old}
    print("old rows surviving", len(rows), "from", len({r["review"] for r in rows}), "reviews")
    # candidate new reviews
    us = {json.loads(l)["pmid"] for l in open(T + "usable.jsonl")}
    lab = collections.defaultdict(lambda: {"included": set(), "excluded": set()})
    for r in csv.DictReader(open(T + "tp_ids.csv")):
        if r["label"] in lab[r["review"]] or r["label"] in ("included", "excluded"):
            if r["pmid"] in us and r["pmid"] not in reserved_pm: lab[r["review"]][r["label"]].add(r["pmid"])
    rng = random.Random(20261123)
    revs = sorted(k for k, v in lab.items() if k not in bad_rev and k not in old_revs and k in titles
                  and norm(titles[k]) not in R["cand_norm"] | R["dev_titles"] and len(v["included"]) >= MINL and len(v["excluded"]) >= MINL)
    rng.shuffle(revs)
    print("eligible new reviews", len(revs))
    TARGET = 5600; pairs = []; need = TARGET - len(rows)
    for k in revs:
        both = lab[k]["included"] & lab[k]["excluded"]
        for l in ("included", "excluded"):
            ids = sorted(lab[k][l] - both); rng.shuffle(ids); pairs += [(k, p, int(l == "included")) for p in ids[:8]]
        if len(pairs) >= need * 1.08: break
    pc = epmc(sorted({p for _, p, _ in pairs}), loadc("papers"), "papers")
    new = []
    for k, p, y in pairs:
        x = pc.get(p)
        if not x or x["license"] not in OK or len(x["abstract"]) < 200 or PLAN.search(x["title"]): continue
        new.append({"review": k, "review_title": clean(titles[k]), "pmid": p, "label": y, "title": x["title"], "abstract": x["abstract"]})
    # a review keeps rows only if both labels remain
    cnt = collections.defaultdict(lambda: [0, 0])
    for r in new: cnt[r["review"]][r["label"]] += 1
    new = [r for r in new if min(cnt[r["review"]]) >= 1]
    rows += new[:max(0, TARGET - len(rows))]
    with open(OUT + "train.jsonl", "w") as f:
        for r in rows: f.write(json.dumps(r) + "\n")
    print("new rows", len(new), "total written", len(rows), "reviews", len({r["review"] for r in rows}))

# ---------------- leakage checks ----------------
def leakage(train, old_train):
    titles = json.load(open(OUT + "review_titles.json"))
    R = reservations(titles)
    trev = {r["review"]: norm(r["review_title"]) for r in train}
    tpm = {r["pmid"] for r in train}
    cand = json.load(open(T + "final-run-candidates.json"))
    old_t = {norm(r["review_title"]) for r in old_train}
    cand_fams = {norm(c["family"]) for c in cand}
    fam_cnt = len({norm(c["family"]) for c in cand})
    return {"training_rows": len(train), "training_reviews": len(trev), "training_families": len(set(trev.values())),
            "candidate_families_total": fam_cnt,
            "overlap_training_reviews_in_candidate_families": sum(1 for k, t in trev.items() if k in R["cand_revs"] or t in R["cand_norm"]),
            "overlap_training_families_with_candidate_families": len(set(trev.values()) & R["cand_norm"]),
            "overlap_training_reviews_pilot_infotest_or_title_match": sum(1 for k, t in trev.items() if k in R["dev_revs"] or t in R["dev_titles"]),
            "overlap_training_papers_with_pilot_infotest_samples": len(tpm & R["dev_pm"]),
            "overlap_training_papers_with_candidate_family_review_papers": len(tpm & R["cand_pm"]),
            "overlap_training_papers_with_final_records_pmids": len(tpm & R["final_pm"]),
            "final_records_pmids_read": len(R["final_pm"]),
            "candidate_review_ids_incl_other_editions": len(R["cand_revs"]),
            "candidate_families_in_OLD_training_data_classic_train_jsonl": len(cand_fams & old_t),
            "candidate_families_in_OLD_training_data_incl_train_with_leak": len(cand_fams & {norm(r["review_title"]) for r in old_train}),
            }

def groups_for(train):
    """connected components over (family, paper PMID): whole families together and a paper never in two folds."""
    par = {}
    def f(x):
        while par.setdefault(x, x) != x: par[x] = par[par[x]]; x = par[x]
        return x
    for r in train: par[f("F:" + norm(r["review_title"]))] = f("P:" + r["pmid"])
    comp = [f("F:" + norm(r["review_title"])) for r in train]
    ids = {c: i for i, c in enumerate(sorted(set(comp)))}
    return np.array([ids[c] for c in comp])

# ---------------- fit ----------------
def fit():
    train = [json.loads(l) for l in open(OUT + "train.jsonl")]
    # drop ambiguous rows: same paper with both labels inside one review
    lab = collections.defaultdict(set)
    for r in train: lab[(r["review"], r["pmid"])].add(r["label"])
    train = [r for r in train if len(lab[(r["review"], r["pmid"])]) == 1]
    y = np.array([r["label"] for r in train]); fam = np.array([norm(r["review_title"]) for r in train])
    grp = groups_for(train)
    sizes = collections.Counter(grp)
    print(f"rows {len(train)} families {len(set(fam))} components {len(sizes)} largest {max(sizes.values())}", flush=True)
    folds = list(GroupKFold(n_splits=5).split(np.zeros(len(train)), y, grp))
    for a, b in folds:   # leak guard: no family and no PMID in both sides
        assert not (set(fam[a]) & set(fam[b])) and not ({train[i]["pmid"] for i in a} & {train[i]["pmid"] for i in b})
    oof = {}; t0 = time.time()
    for fi, (a, b) in enumerate(folds):
        ra, rb = [train[i] for i in a], [train[i] for i in b]
        F = Features(ra); ba, bb = F.blocks(ra), F.blocks(rb); F.fit_scaler(ba[2])
        for kind in KINDS:
            Xa, Xb = F.assemble(ba, kind), F.assemble(bb, kind)
            cands = [("logistic", (C,), make_lr(C)) for C in LR_GRID["C"]] + [("xgboost", g, make_xgb(*g)) for g in XGB_GRID]
            for name, par, m in cands:
                m.fit(Xa, y[a]); p = m.predict_proba(Xb)[:, 1]
                oof.setdefault((name, par, kind), np.zeros(len(train)))[b] = p
        print(f"  fold {fi + 1}/5 done {time.strftime('%H:%M:%S')} ({time.time() - t0:.0f}s)", flush=True)
    table, cvres = [], {}
    for k, p in oof.items():
        bal, au, nf = family_metrics(p, y, fam); cvres[k] = (bal, au)
        table.append({"model": k[0], "params": list(k[1]), "features": k[2], "cv_family_balanced_accuracy": round(bal, 4),
                      "cv_mean_family_auc": round(au, 4), "families_scored": nf})
    table.sort(key=lambda r: -r["cv_family_balanced_accuracy"])
    best = {}
    for name in ("logistic", "xgboost"):
        c = [(k, v) for k, v in cvres.items() if k[0] == name]; top = max(v[0] for _, v in c)
        best[name] = max((kv for kv in c if kv[1][0] >= top - 0.002), key=lambda kv: kv[1][1])[0]
        print("chosen", name, best[name], "bal-acc %.4f auc %.4f" % cvres[best[name]])
    F = Features(train); btr = F.blocks(train); F.fit_scaler(btr[2]); models = {}
    for name, par, kind in best.values():
        m = make_lr(*par) if name == "logistic" else make_xgb(*par)
        models[name] = (kind, m.fit(F.assemble(btr, kind), y))
    pickle.dump({"features": F, "models": models, "chosen": {k: {"features": v[2], "params": list(v[1])} for k, v in best.items()}},
                open(OUT + "models.pkl", "wb"))
    old_train = [json.loads(l) for l in open(T + "classic/train.jsonl")]
    old_leak = [json.loads(l) for l in open(T + "classic/train-with-leak.jsonl")]
    lk = leakage(train, old_train); lk["candidate_families_in_OLD_training_data_incl_train_with_leak"] = leakage(train, old_leak)["candidate_families_in_OLD_training_data_classic_train_jsonl"]
    lk.update({"cv_folds_share_no_family_or_pmid": True, "preprocessing_fitted_inside_training_folds": True,
               "final_vectoriser_idf_scaler_fit_rows": F.fit_rows, "label_counts": {"included": int(y.sum()), "excluded": int((1 - y).sum())}})
    json.dump({"cv_table": table, "chosen": {k: {"features": v[2], "params": list(v[1]), "cv_family_balanced_accuracy": cvres[v][0],
               "cv_mean_family_auc": cvres[v][1]} for k, v in best.items()},
               "selection_rule": "5-fold CV, folds = connected components of (family, PMID); out-of-fold predictions pooled; equal-family balanced accuracy at p>=0.5; per model type pick the best within 0.002 of the top by mean within-family AUC",
               "training_counts": {"rows": len(train), "reviews": len({r["review"] for r in train}), "families": len(set(fam)),
                                   "cv_groups": len(sizes), "largest_group_rows": max(sizes.values())},
               "leakage_checks": lk, "cv_seconds": round(time.time() - t0)}, open(OUT + "selection.json", "w"), indent=1)
    print(json.dumps(lk, indent=1)); print("total %.0fs" % (time.time() - t0))

# ---------------- score ----------------
def score(sample, reviews, prefix):
    P = pickle.load(open(OUT + "models.pkl", "rb")); F = P["features"]
    revs = json.load(open(reviews)); rows = []
    for l in open(sample):
        r = json.loads(l); rows.append({**r, "review_title": revs[r["review"]]["title"]})
    blk = F.blocks(rows)
    for name, (kind, m) in P["models"].items():
        p = m.predict_proba(F.assemble(blk, kind))[:, 1]
        with open(f"{prefix}-{name}.jsonl", "w") as f:
            for r, pi in zip(rows, p): f.write(json.dumps({"case_id": f'{r["review"]}|{r["pmid"]}', "p": float(pi)}) + "\n")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "build": build()
    elif mode == "fit": fit()
    elif mode == "score" and len(sys.argv) == 5: score(*sys.argv[2:5])
    else: sys.exit("usage: classic_final.py build | fit | score <sample.jsonl> <reviews.json> <out_prefix>")
