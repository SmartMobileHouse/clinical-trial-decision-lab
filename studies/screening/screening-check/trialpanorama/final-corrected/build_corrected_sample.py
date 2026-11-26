"""Rebuild the locked sample with correctly cleaned text. Same papers, same reviews, same labels, same order.

The locked run removed markup with the rule <[^>]+>, which also deleted real text after a literal "<" (as in "p < 0.001")
up to the end of the next tag. This script strips only the markup tags that occur in the source text and keeps everything else.
Run from screening-check/trialpanorama. Reads final/sample.jsonl and the raw text fetched again from Europe PMC.
"""
import hashlib, json, re, sys
TAGS = r"</?(?:h4|i|b|sup|sub|br|u|em|strong|p)\b[^<>]*>"   # every tag name found in the raw titles and abstracts, plus close relatives
old = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()
new = lambda s: re.sub(r"\s+", " ", re.sub(TAGS, " ", s or "", flags=re.I)).strip()
raw = {j["pmid"]: j for j in map(json.loads, open(sys.argv[1]))}
rows = [json.loads(l) for l in open("final/sample.jsonl")]
out, changed_abs, changed_title, lost = [], 0, 0, []
for r in rows:
    x = raw[r["pmid"]]
    assert x["found"] and old(x["title_raw"]) == r["title"] and old(x["abstract_raw"]) == r["abstract"], r["pmid"]   # today's source text is the text the locked run used
    t, a = new(x["title_raw"]), new(x["abstract_raw"])
    assert not re.search(TAGS, t + " " + a, flags=re.I)
    changed_title += t != r["title"]; changed_abs += a != r["abstract"]
    if a != r["abstract"]: lost.append(len(a) - len(r["abstract"]))
    out.append({**r, "title": t, "abstract": a})
with open("final-corrected/sample.jsonl", "w") as f:
    for r in out: f.write(json.dumps(r, ensure_ascii=False) + "\n")
with open("final-corrected/changed.json", "w") as f:
    json.dump([{"review": r["review"], "pmid": r["pmid"]} for r, o in zip(out, rows) if r["abstract"] != o["abstract"]], f)
lost.sort()
manifest = {"records": len(out), "abstracts_changed": changed_abs, "titles_changed": changed_title,
            "characters_restored": {"median": lost[len(lost) // 2], "mean": round(sum(lost) / len(lost)), "max": lost[-1]},
            "share_of_corrected_abstract_restored_median": round(sorted((len(r["abstract"]) - len(o["abstract"])) / len(r["abstract"]) for r, o in zip(out, rows) if r["abstract"] != o["abstract"])[changed_abs // 2], 4),
            "changed_by_label": {"included": sum(1 for r, o in zip(out, rows) if r["abstract"] != o["abstract"] and int(r["label"]) == 1),
                                 "excluded": sum(1 for r, o in zip(out, rows) if r["abstract"] != o["abstract"] and int(r["label"]) == 0)},
            "reviews_with_a_changed_abstract": len({r["review"] for r, o in zip(out, rows) if r["abstract"] != o["abstract"]}),
            "labels_identical": all(r["label"] == o["label"] and r["review"] == o["review"] and r["pmid"] == o["pmid"] for r, o in zip(out, rows)),
            "sample_sha256": hashlib.sha256(open("final-corrected/sample.jsonl", "rb").read()).hexdigest()}
json.dump(manifest, open("final-corrected/manifest.json", "w"), indent=1); print(json.dumps(manifest, indent=1))
