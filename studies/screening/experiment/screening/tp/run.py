"""Screening pilot: each model scores one title+abstract against one review's criteria.
Usage: python run.py <model,model,...> <cap_usd> <out_dir> <subset: all|llm120> [env files...]
Reuses the Clinical Trial Decision Lab adapters, spending guard and call ledger. Nothing secret is printed."""
import asyncio, json, random, sys, time
from pathlib import Path
import httpx
from dotenv import load_dotenv
from triallab.core.budget import Budget
from triallab.core.ledger import Ledger, prediction_costs
from triallab.datasets import payload_hash
from triallab.providers.base import Task
from triallab.providers.registry import make_remote, worst_case_cost
from triallab.providers.spec import load_registry
from triallab.questions import Question, QuestionSet

HERE = Path(__file__).resolve().parent
models, cap, out, subset = sys.argv[1].split(","), float(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
out.mkdir(parents=True, exist_ok=True)
for env in sys.argv[5:]:
    load_dotenv(env, override=False)
import os as _os
raw = json.load(open(HERE / _os.environ.get("QUESTIONS_FILE", "questions.json")))
qs = QuestionSet(raw["version"], "screening", raw["context"], tuple(Question(q["id"], q["text"], q["true"], q["false"]) for q in raw["questions"]))
reviews = json.load(open(HERE.parents[2] / "screening-check/trialpanorama" / _os.environ.get("SAMPLE_DIR", "pilot") / "reviews.json"))

def review_block(rev):
    """What the model is told about the review: title only, or title plus the review's own objectives and selection criteria."""
    b = {"review_title": rev["title"]}
    if _os.environ.get("CONTEXT_MODE") == "criteria":
        b["review_objectives"] = rev.get("objectives"); b["review_selection_criteria"] = rev.get("selection_criteria")
    return b
rows, seen = [], set()
for l in open(HERE.parents[2] / "screening-check/trialpanorama" / _os.environ.get("SAMPLE_DIR", "pilot") / "sample.jsonl"):
    r = json.loads(l)
    if (r["review"], r["pmid"]) not in seen:
        seen.add((r["review"], r["pmid"])); rows.append(r)
if subset == "llm120":  # matched subset for the general model: 3 relevant + 3 not relevant per review, fixed seed
    rng, pick = random.Random(20261120), []
    for rev in sorted({r["review"] for r in rows}):
        for lab, n in ((1, 3), (0, 3)):
            pool = sorted((r for r in rows if r["review"] == rev and r["label"] == lab), key=lambda r: r["pmid"])
            pick += rng.sample(pool, n)
    rows = pick
import os
if os.environ.get('PILOT_LIMIT'): rows = rows[:: max(1, len(rows) // int(os.environ['PILOT_LIMIT']))][: int(os.environ['PILOT_LIMIT'])]
tasks = []
for r in rows:
    rev = reviews[r["review"]]
    state = {**review_block(rev), "study": {"title": r["title"], "abstract": r["abstract"]}}
    # hash covers the question text too, so a changed prompt never reuses old answers
    tasks.append(Task(f'{r["review"]}|{r["pmid"]}', state, payload_hash({"state": state, "questions_version": raw["version"], "questions": [q["text"] for q in raw["questions"]], "context": raw["context"]}), qs))

async def main():
    registry = load_registry(); ledger = Ledger(out / "attempts.jsonl"); past = ledger.summary()
    budget = Budget(cap, past.spent_usd, past.estimated_usd); allrows = []
    async with httpx.AsyncClient(limits=httpx.Limits(max_connections=20)) as client:
        async def run_model(name):
            provider = make_remote(name, registry, client); provider.credentials()
            sem, t0 = asyncio.Semaphore(3), time.perf_counter()
            async def one(task):
                prev = past.completed.get((name, task.case_id))
                if prev is not None and prev.payload_hash == task.payload_hash: return prev
                reserve = worst_case_cost(provider, task)
                async with sem:
                    if not await budget.reserve(reserve): return None
                    await asyncio.sleep(0.4)
                    attempt = ledger.start(name, task.case_id, reserve)
                    pred = await provider.evaluate(task); ledger.finish(attempt, pred)
                    known, est = prediction_costs(pred, reserve); await budget.settle(reserve, known, estimated_usd=est)
                    return pred
            preds = await asyncio.gather(*(one(t) for t in tasks)); wall = time.perf_counter() - t0
            st = {}
            for p in preds:
                s = "not_run_budget" if p is None else p.status; st[s] = st.get(s, 0) + 1
            print(f"{name:<24} statuses {st}  wall {wall:.0f}s  first error: {next((p.error for p in preds if p is not None and p.error), None)}")
            json.dump({"wall_seconds": wall, "n": len(preds)}, open(out / f"wall-{name}.json", "w"))
            return [p.as_dict() for p in preds if p is not None]
        for res in await asyncio.gather(*(run_model(m) for m in models), return_exceptions=True):
            if isinstance(res, Exception): print("model failed to start:", type(res).__name__, str(res)[:160])
            else: allrows += res
    with open(out / "predictions.jsonl", "w") as f:
        for r in allrows: f.write(json.dumps(r) + "\n")
    s = budget.state
    print(f"accounted ${s.spent_usd:.4f} (of which estimated ${s.estimated_usd:.4f}); cap ${cap:.2f}; refused by budget {s.refused}")
asyncio.run(main())
