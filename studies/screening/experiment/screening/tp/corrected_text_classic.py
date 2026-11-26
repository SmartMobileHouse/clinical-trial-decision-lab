"""Corrected-text rerun: refit the two trained classifiers on correctly cleaned text and score the corrected sample.

Same training rows and the same settings as the locked run (classic-final/selection.json). No settings are selected again.
Written before any corrected-text prediction existed. See reports/Corrected-text rerun plan.md.

Usage: .venv-classic/bin/python corrected_text_classic.py <raw training text, jsonl from abstract-check/fetch_raw.py>
"""
import collections, json, re, sys
from pathlib import Path
import numpy as np
import classic_final as cf

SRC = Path(__file__).resolve().parent
T = SRC.parents[2] / "screening-check/trialpanorama"
TAGS = r"</?(?:h4|i|b|sup|sub|br|u|em|strong|p)\b[^<>]*>"
old = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()
new = lambda s: re.sub(r"\s+", " ", re.sub(TAGS, " ", s or "", flags=re.I)).strip()

raw = {j["pmid"]: j for j in map(json.loads, open(sys.argv[1]))}
train = [json.loads(l) for l in open(T / "classic-final/train.jsonl")]
lab = collections.defaultdict(set)
for r in train: lab[(r["review"], r["pmid"])].add(r["label"])
train = [r for r in train if len(lab[(r["review"], r["pmid"])]) == 1]        # same rule as the locked fit: drop papers with both labels in one review

stats = collections.Counter(); fixed = []
for r in train:
    x = raw.get(r["pmid"])
    if not x or not x["found"]: stats["source text not available today; old text kept"] += 1; fixed.append(r); continue
    if old(x["abstract_raw"]) != r["abstract"] or old(x["title_raw"]) != r["title"]:
        stats["source text differs from the text used in the locked fit; old text kept"] += 1; fixed.append(r); continue
    t, a = new(x["title_raw"]), new(x["abstract_raw"])
    stats["abstract corrected" if a != r["abstract"] else "abstract unchanged"] += 1
    if t != r["title"]: stats["title corrected"] += 1
    fixed.append({**r, "title": t, "abstract": a})

rows = {}
for l in open(T / "final-corrected/sample.jsonl"):
    r = json.loads(l); rows[f'{r["review"]}|{r["pmid"]}'] = r
reviews = json.load(open(T / "final-corrected/reviews.json"))
chosen = json.load(open(T / "classic-final/selection.json"))["chosen"]
srows = [{**r, "review_title": reviews[r["review"]]["title"]} for r in rows.values()]; skeys = list(rows)
yy = np.array([r["label"] for r in fixed]); F = cf.Features(fixed); b = F.blocks(fixed); F.fit_scaler(b[2]); sb = F.blocks(srows)
for name in ("logistic", "xgboost"):
    kind, par = chosen[name]["features"], chosen[name]["params"]
    m = cf.make_lr(*par) if name == "logistic" else cf.make_xgb(int(par[0]), int(par[1]), int(par[2]))
    m.fit(F.assemble(b, kind), yy); p = dict(zip(skeys, map(float, m.predict_proba(F.assemble(sb, kind))[:, 1])))
    with open(SRC / f"corrected-classic-{name}.jsonl", "w") as f:
        for i in rows: f.write(json.dumps({"case_id": i, "p": p[i]}) + "\n")
info = {"training_rows": len(fixed), "training_text": dict(stats), "settings": chosen}
json.dump(info, open(SRC / "corrected-classic-info.json", "w"), indent=1); print(json.dumps({k: v for k, v in info.items() if k != "settings"}, indent=1))
