"""Run decision models through OpenRouter's System One route on the TrialPanorama pilot sample.
Builds the same state and question text as the lab's System One adapter. Cost is the figure OpenRouter reports.
Usage: python run_openrouter.py <model,model,...> <cap_usd> <limit or 0> <env file>"""
import asyncio, json, os, sys, time
from pathlib import Path
import httpx
from dotenv import load_dotenv
from triallab.providers.adapters import question_instructions
from triallab.questions import Question
models, cap, limit = sys.argv[1].split(","), float(sys.argv[2]), int(sys.argv[3]); load_dotenv(sys.argv[4])
HERE = Path(__file__).resolve().parent; S = HERE.parents[2] / "screening-check/trialpanorama" / os.environ.get("SAMPLE_DIR", "pilot")
raw = json.load(open(HERE / os.environ.get("QUESTIONS_FILE", "questions.json"))); reviews = json.load(open(S / "reviews.json")); q = raw["questions"][0]
instr = question_instructions(raw["context"], Question(q["id"], q["text"], q["true"], q["false"]))
rows = [json.loads(l) for l in open(S / "sample.jsonl")]
if limit: rows = rows[:: len(rows) // limit][:limit]
H = {"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"].strip(), "Content-Type": "application/json"}

def review_block(rev):
    """What the model is told about the review: title only, or title plus the review's own objectives and selection criteria."""
    b = {"review_title": rev["title"]}
    if os.environ.get("CONTEXT_MODE") == "criteria":
        b["review_objectives"] = rev.get("objectives"); b["review_selection_criteria"] = rev.get("selection_criteria")
    return b
spent = 0.0
async def run(model, client):
    global spent
    sem, res = asyncio.Semaphore(3), []
    async def one(r):
        global spent
        state = {**review_block(reviews[r["review"]]), "study": {"title": r["title"], "abstract": r["abstract"]}}
        body = {"model": model, "state": state, "questions": {"included": {"type": "noul", "instructions": instr}}}
        async with sem:
            if spent >= cap: return {"status": "not_run_budget"}
            err, attempts = None, []
            for a in range(4):
                t = time.perf_counter(); started = time.strftime("%Y-%m-%dT%H:%M:%S%z")
                try:
                    resp = await client.post("https://openrouter.ai/api/v1/systemone", headers=H, json=body); ms = (time.perf_counter() - t) * 1000
                    attempts.append({"started": started, "latency_ms": ms, "status_code": resp.status_code})
                    if resp.status_code == 200:
                        j = resp.json(); ans = (j.get("answers") or {}).get("included") or {}; p = ans.get("noul"); u = j.get("usage") or {}; spent += u.get("cost") or 0
                        if not isinstance(p, (int, float)): return {"status": "error", "error": "no probability: " + json.dumps(ans)[:120]}
                        return {"status": "ok", "probabilities": {"included": p}, "answers": {"included": p >= 0.5}, "latency_ms": ms, "cost_usd": u.get("cost") or 0,
                                "input_tokens": u.get("input_tokens"), "model_reported": j.get("model"), "upstream": j.get("provider"), "attempts": attempts}
                    err = f"HTTP {resp.status_code}: {resp.text[:160]}"
                    if resp.status_code not in (429, 500, 502, 503, 529): break
                except httpx.HTTPError as e: err = type(e).__name__; attempts.append({"started": started, "error": err})
                await asyncio.sleep(2 * (a + 1))
            return {"status": "error", "error": err, "attempts": attempts}
    out = await asyncio.gather(*(one(r) for r in rows))
    name = "or_" + model.split("/")[1].replace("-", "_").replace(".", "_")
    recs = [{"case_id": f'{r["review"]}|{r["pmid"]}', "provider": name, "model_requested": model, **o} for r, o in zip(rows, out)]
    st = {}
    for o in out: st[o["status"]] = st.get(o["status"], 0) + 1
    ok = [o for o in out if o["status"] == "ok"]
    print(f'{model:<34} {st}  reported {sorted({o["model_reported"] for o in ok})} via {sorted({str(o["upstream"]) for o in ok})}  cost ${sum(o["cost_usd"] for o in ok):.4f}  first error: {next((o.get("error") for o in out if o.get("error")), None)}', flush=True)
    if not limit:
        d = HERE / (os.environ.get("OUT_PREFIX", "pilot-") + name); d.mkdir(exist_ok=True)
        with open(d / "predictions.jsonl", "w") as f:
            for x in recs: f.write(json.dumps(x) + "\n")
    else: print("    sample probabilities:", [round(o["probabilities"]["included"], 3) for o in ok])
async def main():
    async with httpx.AsyncClient(timeout=120) as client:
        await asyncio.gather(*(run(m, client) for m in models))   # models are on different providers, so they run side by side
    print(f"total reported cost ${spent:.4f} (cap ${cap:.2f})")
asyncio.run(main())
