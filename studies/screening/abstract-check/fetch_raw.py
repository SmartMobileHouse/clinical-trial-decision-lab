"""Fetch raw title and abstract text from Europe PMC for a list of PubMed ids. Public metadata only; nothing else is sent.
Usage: python fetch_raw.py <ids file, one PMID per line> <out.jsonl>   (resumable)"""
import json, os, sys, time, urllib.parse, urllib.request
ids = [l.strip() for l in open(sys.argv[1]) if l.strip()]
have = {json.loads(l)["pmid"] for l in open(sys.argv[2])} if os.path.exists(sys.argv[2]) else set()
todo = [p for p in ids if p not in have]
with open(sys.argv[2], "a") as out:
    for i in range(0, len(todo), 50):
        chunk = todo[i:i + 50]; res = None
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
            {"query": "(" + " OR ".join("EXT_ID:" + x for x in chunk) + ") AND SRC:MED", "format": "json", "resultType": "core", "pageSize": "50"})
        for a in range(5):
            try:
                res = {x["pmid"]: x for x in json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-client"}), timeout=90))["resultList"]["result"]}
                break
            except Exception:
                time.sleep(4 * (a + 1))
        if res is None:
            continue
        for p in chunk:
            x = res.get(p) or {}
            out.write(json.dumps({"pmid": p, "found": bool(x), "title_raw": x.get("title"), "abstract_raw": x.get("abstractText"), "licence": (x.get("license") or "").lower()}) + "\n")
        out.flush(); time.sleep(0.3)
print("ids", len(ids), "fetched now", len(todo))
