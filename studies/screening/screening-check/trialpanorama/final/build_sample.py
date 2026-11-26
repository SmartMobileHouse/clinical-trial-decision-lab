"""Final run, step 2: draw the locked sample exactly as written in reports/Locked run plan.md, section 3.
Reads only public metadata and the published include/exclude lists. Deterministic (seed 20261122)."""
import csv, json, collections, hashlib, random, re
SEED = 20261122
PLAN = re.compile(r"protocol|study design|design of|rationale|trial design", re.I)
adj = json.load(open("final/family-adjudication.json"))["families"]
keep = {f["review"]: f for f in adj if f["keep"]}
pilot = {json.loads(l)["pmid"] for f in ("pilot/sample.jsonl", "info-test/sample.jsonl") for l in open(f)}
rec = {}
for l in open("final/records.jsonl"):
    j = json.loads(l); rec[j["pmid"]] = j
lab = collections.defaultdict(lambda: {"included": set(), "excluded": set()})
for r in csv.DictReader(open("tp_ids.csv")):
    if r["review"] in keep and r["label"] in ("included", "excluded"): lab[r["review"]][r["label"]].add(r["pmid"])
flow = collections.Counter(); canon = {}                      # DOI duplicates collapse to one record (lowest PMID)
for p, j in sorted(rec.items(), key=lambda kv: int(kv[0])):
    if j.get("doi"): canon.setdefault(j["doi"], p)
def usable(p):
    j = rec.get(p)
    if p in pilot: return "used in pilot"
    if not j: return "no open commercial-reuse licence on record (never fetched)"
    if not j["found"]: return "metadata not found"
    if not j["licence_ok"]: return "licence not open for commercial reuse"
    if len(j["abstract"]) < 200 or not j["title"]: return "abstract shorter than 200 characters or no title"
    if PLAN.search(j["title"]): return "plan-like title"
    if j.get("doi") and canon[j["doi"]] != p: return "duplicate DOI"
    return None
rng = random.Random(SEED); order = sorted(keep); rng.shuffle(order)
taken, sample, fam_flow = set(), [], []
for rv in order:
    both = lab[rv]["included"] & lab[rv]["excluded"]; pool = {}
    for name in ("included", "excluded"):
        ids = []
        for p in sorted(lab[rv][name] - both, key=int):
            why = usable(p)
            if why: flow[f"{name} record dropped: {why}"] += 1; continue
            if p in taken: flow[f"{name} record dropped: already allocated to another family"] += 1; continue
            ids.append(p)
        pool[name] = ids
    flow["records carrying both labels (dropped)"] += len(both)
    ni, ne = len(pool["included"]), len(pool["excluded"])
    if ni < 6 or ne < 6:
        fam_flow.append({"review": rv, "title": keep[rv]["title"], "qualifies": False, "usable_included": ni, "usable_excluded": ne}); continue
    k = min(10, ni, ne)
    for name, y in (("included", 1), ("excluded", 0)):
        for p in rng.sample(pool[name], k):
            taken.add(p); j = rec[p]
            sample.append({"review": rv, "pmid": p, "pmcid": j.get("pmcid"), "doi": j.get("doi"), "licence": j["licence"], "label": y, "year": j.get("year"), "title": j["title"], "abstract": j["abstract"]})
    fam_flow.append({"review": rv, "title": keep[rv]["title"], "qualifies": True, "usable_included": ni, "usable_excluded": ne, "k_per_label": k})
with open("final/sample.jsonl", "w") as f:
    for s in sample: f.write(json.dumps(s, ensure_ascii=False) + "\n")
q = [f for f in fam_flow if f["qualifies"]]
json.dump({f["review"]: {"title": f["title"], "year": keep[f["review"]]["year"]} for f in q}, open("final/reviews.json", "w"), indent=1, ensure_ascii=False)
man = {"seed": SEED, "families_considered_after_title_adjudication": len(keep), "families_qualifying": len(q), "families_not_qualifying": len(fam_flow) - len(q),
       "records": len(sample), "included": sum(s["label"] for s in sample), "excluded": sum(1 - s["label"] for s in sample), "unique_pmids": len({s["pmid"] for s in sample}),
       "k_distribution": dict(sorted(collections.Counter(f["k_per_label"] for f in q).items())), "record_flow": dict(flow), "families": fam_flow,
       "sample_sha256": hashlib.sha256(open("final/sample.jsonl", "rb").read()).hexdigest(), "licences": dict(collections.Counter(s["licence"] for s in sample))}
json.dump(man, open("final/sample-manifest.json", "w"), indent=1, ensure_ascii=False)
print({k: man[k] for k in ("families_considered_after_title_adjudication", "families_qualifying", "records", "included", "excluded", "unique_pmids", "k_distribution", "licences")})
for k, v in sorted(flow.items()): print(f"   {v:>5}  {k}")
print("sha256", man["sample_sha256"])
