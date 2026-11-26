"""Final run, step 1: fetch title, abstract, DOI and licence for every usable candidate record of the kept review families.
No labels are sent anywhere; Europe PMC is asked only for public article metadata. Resumable; progress in final/progress.txt."""
import csv, json, collections, os, re, time, urllib.parse, urllib.request
OK = {"cc by", "cc0", "cc by-sa", "cc by-nd"}
keep = [f["review"] for f in json.load(open("final/family-adjudication.json"))["families"] if f["keep"]]
us = {json.loads(l)["pmid"] for l in open("usable.jsonl")}
pilot = {json.loads(l)["pmid"] for f in ("pilot/sample.jsonl", "info-test/sample.jsonl") for l in open(f)}
R = collections.defaultdict(lambda: {"included": set(), "excluded": set()})
for r in csv.DictReader(open("tp_ids.csv")):
    if r["review"] in keep and r["pmid"] in us and r["label"] in ("included", "excluded"): R[r["review"]][r["label"]].add(r["pmid"])
need = sorted({p for v in R.values() for p in v["included"] | v["excluded"]} - pilot)
have = {}
if os.path.exists("final/records.jsonl"):
    for l in open("final/records.jsonl"): j = json.loads(l); have[j["pmid"]] = j
todo = [p for p in need if p not in have]
clean = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()
t0 = time.time()
with open("final/records.jsonl", "a") as out:
    for i in range(0, len(todo), 50):
        chunk = todo[i:i + 50]; res = None
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode({"query": "(" + " OR ".join("EXT_ID:" + x for x in chunk) + ") AND SRC:MED", "format": "json", "resultType": "core", "pageSize": "50"})
        for a in range(5):
            try: res = {x["pmid"]: x for x in json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-client"}), timeout=90))["resultList"]["result"]}; break
            except Exception: time.sleep(4 * (a + 1))
        if res is None: continue
        for p in chunk:
            x = res.get(p) or {}
            out.write(json.dumps({"pmid": p, "found": bool(x), "doi": (x.get("doi") or "").lower() or None, "pmcid": x.get("pmcid"), "licence": (x.get("license") or "").lower(), "year": x.get("pubYear"),
                                  "title": clean(x.get("title")), "abstract": clean(x.get("abstractText")), "licence_ok": (x.get("license") or "").lower() in OK}) + "\n")
        out.flush(); done = i + len(chunk); el = time.time() - t0
        open("final/progress.txt", "w").write(f"fetching records: {100*done/len(todo):.0f}% ({done} of {len(todo)}) | about {el/done*(len(todo)-done)/60:.0f} min left | updated {time.strftime('%H:%M:%S')}\n")
open("final/progress.txt", "a").write("FINISHED\n"); print("families", len(keep), "records needed", len(need), "fetched now", len(todo))
