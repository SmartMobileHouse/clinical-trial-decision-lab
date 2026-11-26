"""Ask the two general models for a probability (not just yes/no), so their confidence can be compared fairly with the
decision models'. Same state and question as elsewhere; the only change is the requested output: {"probability": 0..1}.
Usage: python run_llm_probability.py <sample dir: pilot|info-test> <context mode: title|criteria> <questions file> <out dir> <cap_usd> <env>"""
import asyncio, json, os, sys, time
from pathlib import Path
import httpx
from dotenv import load_dotenv
sample, mode, qfile, out, cap = sys.argv[1], sys.argv[2], sys.argv[3], Path(sys.argv[4]), float(sys.argv[5]); load_dotenv(sys.argv[6]); out.mkdir(parents=True, exist_ok=True)
HERE = Path(__file__).resolve().parent; S = HERE.parents[2] / "screening-check/trialpanorama" / sample
raw = json.load(open(HERE / qfile)); q = raw["questions"][0]; reviews = json.load(open(S / "reviews.json"))
INSTR = "\n".join([raw["context"], "", "Give the probability, from 0 to 1, that the answer to this question is yes.", "", f'{q["id"]}: {q["text"]}', f'  yes if: {q["true"]}', f'  no if: {q["false"]}',
                   "", "A probability of 0.2 should mean that about 20% of such studies turn out to be included."])
SCHEMA = {"type": "object", "properties": {"probability": {"type": "number"}}, "required": ["probability"], "additionalProperties": False}
PRICE = {"llm_openai_prob": (0.10, 0.50), "llm_anthropic_prob": (0.10, 0.50)}   # USD per million input / output tokens, published prices retrieved 2026-11-16
MODEL_ID = {"llm_openai_prob": "gpt-6-luna", "llm_anthropic_prob": "claude-haiku-5-5"}
rows = [json.loads(l) for l in open(S / "sample.jsonl")]; spent = 0.0
def state(r):
    rv = reviews[r["review"]]; b = {"review_title": rv["title"]}
    if mode == "criteria": b["review_objectives"] = rv.get("objectives"); b["review_selection_criteria"] = rv.get("selection_criteria")
    return json.dumps({"case": {**b, "study": {"title": r["title"], "abstract": r["abstract"]}}}, ensure_ascii=False)
async def openai(c, r):
    body = {"model": "gpt-6-luna", "instructions": INSTR, "input": [{"role": "user", "content": state(r)}], "reasoning": {"effort": "none"}, "max_output_tokens": 100, "store": False,
            "text": {"format": {"type": "json_schema", "name": "probability_answer", "strict": True, "schema": SCHEMA}}}
    x = await c.post("https://api.openai.com/v1/responses", headers={"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"].strip()}, json=body); d = x.json()
    if x.status_code != 200: return None, f"HTTP {x.status_code}", (0, 0)
    t = "".join(p.get("text", "") for i in d.get("output") or [] if i.get("type") == "message" for p in i.get("content") or [] if p.get("type") == "output_text"); u = d.get("usage") or {}
    return t, None, (u.get("input_tokens", 0), u.get("output_tokens", 0))
async def anthropic(c, r):
    body = {"model": "claude-haiku-5-5", "max_tokens": 100, "system": INSTR, "messages": [{"role": "user", "content": state(r)}], "thinking": {"type": "disabled"},
            "output_config": {"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}}}
    x = await c.post("https://api.anthropic.com/v1/messages", headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"].strip(), "anthropic-version": "2026-10-21"}, json=body); d = x.json()
    if x.status_code != 200: return None, f"HTTP {x.status_code}: {str(d)[:120]}", (0, 0)
    t = "".join(b.get("text", "") for b in d.get("content") or [] if b.get("type") == "text"); u = d.get("usage") or {}
    return t, None, (u.get("input_tokens", 0), u.get("output_tokens", 0))
async def run(name, fn, c):
    """Every transport attempt is logged (time, status, tokens, charge). At most four attempts, only for transport failures:
    an answer that arrives is never retried, whatever it says. Charges for invalid answers are counted."""
    global spent
    sem = asyncio.Semaphore(4)
    async def one(r):
        global spent
        async with sem:
            if spent >= cap: return {"status": "not_run_budget", "attempts": []}
            attempts, text, ti, to = [], None, 0, 0
            for a in range(4):
                t0 = time.perf_counter(); started = time.strftime("%Y-%m-%dT%H:%M:%S%z")
                try: text, err, (ti, to) = await fn(c, r)
                except httpx.HTTPError as e: text, err, ti, to = None, type(e).__name__, 0, 0
                ms = (time.perf_counter() - t0) * 1000; charge = (ti * PRICE[name][0] + to * PRICE[name][1]) / 1e6; spent += charge
                attempts.append({"started": started, "latency_ms": ms, "error": err, "input_tokens": ti, "output_tokens": to, "charge_usd": charge})
                if text is not None: break
                await asyncio.sleep(2 * (a + 1))
            base = {"attempts": attempts, "latency_ms": attempts[-1]["latency_ms"], "cost_usd": sum(x["charge_usd"] for x in attempts),
                    "input_tokens": sum(x["input_tokens"] for x in attempts), "output_tokens": sum(x["output_tokens"] for x in attempts), "model_requested": MODEL_ID[name]}
            try:
                p = float(json.loads(text)["probability"])
                if not (p == p and 0 <= p <= 1): raise ValueError
            except Exception: return {"status": "invalid", "error": attempts[-1]["error"] or "no valid probability", "raw": (text or "")[:80], **base}
            return {"status": "ok", "probabilities": {"included": p}, "answers": {"included": p >= 0.5}, **base}
    outs = await asyncio.gather(*(one(r) for r in rows)); st = {}
    for o in outs: st[o["status"]] = st.get(o["status"], 0) + 1
    with open(out / f"{name}.jsonl", "w") as f:
        for r, o in zip(rows, outs): f.write(json.dumps({"case_id": f'{r["review"]}|{r["pmid"]}', "provider": name, **o}) + "\n")
    print(name, st, "distinct probabilities:", len({o["probabilities"]["included"] for o in outs if o["status"] == "ok"}), "cost $%.4f" % sum(o.get("cost_usd", 0) for o in outs), "first error:", next((o.get("error") for o in outs if o.get("error")), None))
async def main():
    async with httpx.AsyncClient(timeout=120) as c: await asyncio.gather(run("llm_openai_prob", openai, c), run("llm_anthropic_prob", anthropic, c))
    print(f"spent ${spent:.4f} (cap ${cap:.2f})")
asyncio.run(main())
